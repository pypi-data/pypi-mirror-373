from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Exists, OuterRef, Subquery
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from django_fsm import FSMField, transition
from wbcore.contrib.directory.models import EmailContact
from wbcore.contrib.directory.signals import deactivate_profile
from wbcore.contrib.icons import WBIcon
from wbcore.contrib.notifications.dispatch import send_notification
from wbcore.contrib.notifications.utils import create_notification_type
from wbcore.enums import RequestType
from wbcore.metadata.configs.buttons import ActionButton, ButtonDefaultColor
from wbcore.models import WBModel


def can_administrate_change_request(mail, user):
    return user.has_perm("wbmailing.administrate_mailinglistsubscriberchangerequest") or user.is_superuser


class MailingListSubscriberChangeRequest(models.Model):
    class Type(models.TextChoices):
        SUBSCRIBING = "SUBSCRIBING", _("Subscribing")
        UNSUBSCRIBING = "UNSUBSCRIBING", _("Unsubscribing")

    class Status(models.TextChoices):
        PENDING = "PENDING", _("Pending")
        APPROVED = "APPROVED", _("Approved")
        DENIED = "DENIED", _("Denied")

    status = FSMField(default=Status.PENDING, choices=Status.choices, verbose_name=_("Status"))
    type = models.CharField(max_length=32, choices=Type.choices, verbose_name=_("Type"))

    @transition(
        field=status,
        source=[Status.PENDING],
        target=Status.APPROVED,
        permission=can_administrate_change_request,
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbmailing:mailinglistsubscriberchangerequest",),
                color=ButtonDefaultColor.SUCCESS,
                icon=WBIcon.APPROVE.icon,
                key="approve",
                label=_("Approve"),
                action_label=_("Approving"),
                description_fields=_(
                    "<p>Address: {{_email_contact.address}}</p><p>Mailing list: {{_mailing_list.title}}</p>"
                ),
            )
        },
    )
    def approve(self, by=None, description=None, **kwargs):
        if profile := getattr(by, "profile", None):
            self.approver = profile
        if self.subscribing:
            self.relationship.status = MailingListEmailContactThroughModel.Status.SUBSCRIBED
        else:
            self.relationship.status = MailingListEmailContactThroughModel.Status.UNSUBSCRIBED
        self.relationship.save()
        if description:
            self.reason = description
        if self.requester != self.approver and (user := getattr(self.requester, "user_account", None)):
            approver_repr = self.approver.full_name if self.approver else "Unknown"
            send_notification(
                code="wbmailing.mailinglistsubscriberchangerequest.notify",
                title=f"{self.type} change request for {self.email_contact.address} to {self.mailing_list.title} approved by {approver_repr}",
                body=self.reason,
                user=user,
            )

    @transition(
        field=status,
        source=[Status.PENDING],
        target=Status.DENIED,
        permission=can_administrate_change_request,
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                color=ButtonDefaultColor.ERROR,
                identifiers=("wbmailing:mailinglistsubscriberchangerequest",),
                icon=WBIcon.DENY.icon,
                key="deny",
                label=_("Deny"),
                action_label=_("Denial"),
                description_fields=_(
                    "<p>Mail: {{_email_contact.address}}</p><p>Mailing list: {{_mailing_list.title}}</p>"
                ),
            )
        },
    )
    def deny(self, by=None, description=None, **kwargs):
        if profile := getattr(by, "profile", None):
            self.approver = profile
        if description:
            self.reason = description

    email_contact = models.ForeignKey(
        "directory.EmailContact",
        related_name="change_requests",
        on_delete=models.CASCADE,
        verbose_name=_("Subscriber"),
    )
    mailing_list = models.ForeignKey(
        "MailingList", related_name="change_requests", on_delete=models.CASCADE, verbose_name=_("Mailing List")
    )
    relationship = models.ForeignKey(
        "wbmailing.MailingListEmailContactThroughModel", on_delete=models.CASCADE, related_name="requests"
    )

    requester = models.ForeignKey(
        "directory.Person", null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_("Requester")
    )
    approver = models.ForeignKey(
        "directory.Person",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_requests",
        verbose_name=_("Approver"),
    )

    expiration_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Expiration Date"),
        help_text=_(
            "If set, this email will be removed automatically from the mailing list after the set expiration time"
        ),
    )

    reason = models.TextField(blank=True, null=True, verbose_name=_("Reason"))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_("Created"))
    updated = models.DateTimeField(auto_now=True, verbose_name=_("Updated"))

    class Meta:
        verbose_name = _("Mailing List Subscriber Change Request")
        verbose_name_plural = _("Mailing List Subscriber Change Requests")
        permissions = (
            (
                "administrate_mailinglistsubscriberchangerequest",
                "Can Administrate Mailing List Subscriber Change Requests",
            ),
        )
        constraints = [
            models.UniqueConstraint(
                fields=["mailing_list", "email_contact"],
                condition=models.Q(status="PENDING"),
                name="unique_pending_request",
            )
        ]

        notification_types = [
            create_notification_type(
                code="wbmailing.mailinglistsubscriberchangerequest.notify",
                title="Subscriber Notification",
                help_text="Sends out a notification when a recipient subscribes or unsubscribes",
            )
        ]

    def save(self, **kwargs):
        if not hasattr(self, "relationship"):
            self.relationship = MailingListEmailContactThroughModel.objects.get_or_create(
                mailing_list=self.mailing_list, email_contact=self.email_contact
            )[0]
        if not self.type:
            self.type = (
                self.Type.SUBSCRIBING
                if self.relationship.status == MailingListEmailContactThroughModel.Status.UNSUBSCRIBED
                else self.Type.UNSUBSCRIBING
            )
        if self.status == MailingListSubscriberChangeRequest.Status.PENDING:
            if self.mailing_list.is_public or (
                (user := getattr(self.requester, "user_account", None)) and can_administrate_change_request(self, user)
            ):
                if self.approver is None:
                    self.approver = self.requester
                self.approve(description=gettext("Automatically approved.") if not self.reason else self.reason)

        super().save(**kwargs)

    @property
    def subscribing(self) -> bool:
        """
        True if the state is unsubscribed and the change will subscribe it
        """
        return (
            self.relationship.status == MailingListEmailContactThroughModel.Status.UNSUBSCRIBED
            and self.type == self.Type.SUBSCRIBING
        )

    def __str__(self) -> str:
        return f"{self.type} {self.email_contact.address} {self.mailing_list.title}"

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbmailing:mailinglistsubscriberchangerequest"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{email_contact__address}} to {{mailing_list__title}}"

    @classmethod
    def get_approvers(cls):
        return (
            get_user_model()
            .objects.filter(
                models.Q(groups__permissions__codename="administrate_mailinglistsubscriberchangerequest")
                | models.Q(user_permissions__codename="administrate_mailinglistsubscriberchangerequest")
            )
            .distinct()
        )


class MailingListEmailContactThroughModel(models.Model):
    class Status(models.TextChoices):
        SUBSCRIBED = "SUBSCRIBED", _("Subscribed")
        UNSUBSCRIBED = "UNSUBSCRIBED", _("Unsubscribed")

    mailing_list = models.ForeignKey(
        "wbmailing.MailingList", on_delete=models.CASCADE, related_name="through_mailinglists"
    )
    email_contact = models.ForeignKey(
        "directory.EmailContact", on_delete=models.CASCADE, related_name="through_mailinglists"
    )
    status = models.CharField(
        max_length=32, default=Status.UNSUBSCRIBED, choices=Status.choices, verbose_name=_("Status")
    )

    class Meta:
        unique_together = ("mailing_list", "email_contact")

    def change_state(self, automatically_approve: bool = False, **kwargs):
        """
        When called, change the state of the relationship from subscribe to unsubscribe or unsubscribe to subscribe
        Args:
            reason: Text field explaining the reason
            requester: The subscription change state requester
            automatically_approve: True if the change request needs to be automatically approved.
        """
        request = MailingListSubscriberChangeRequest.objects.get_or_create(
            email_contact=self.email_contact,
            mailing_list=self.mailing_list,
            status=MailingListSubscriberChangeRequest.Status.PENDING,
            defaults={
                "relationship": self,
                "type": MailingListSubscriberChangeRequest.Type.SUBSCRIBING
                if self.status == self.Status.UNSUBSCRIBED
                else MailingListSubscriberChangeRequest.Type.UNSUBSCRIBING,
                **kwargs,
            },
        )[0]
        if automatically_approve and request.status == MailingListSubscriberChangeRequest.Status.PENDING:
            request.approve()
            request.save()

    @classmethod
    def get_expired_date_subquery(
        cls, mailing_list_label_field: str = "mailing_list", email_contact_label_field: str = "email_contact"
    ) -> Subquery:
        return Subquery(
            MailingListSubscriberChangeRequest.objects.filter(
                mailing_list=OuterRef(mailing_list_label_field),
                email_contact=OuterRef(email_contact_label_field),
                status=MailingListSubscriberChangeRequest.Status.APPROVED,
                type=MailingListSubscriberChangeRequest.Type.SUBSCRIBING,
            )
            .order_by("-created")
            .values("expiration_date")[:1],
        )

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbmailing:mailinglistemailcontact"


class MailingList(WBModel):
    class Meta:
        verbose_name = _("Mailing List")
        verbose_name_plural = _("Mailing Lists")

    title = models.CharField(max_length=255, verbose_name=_("Title"))
    is_public = models.BooleanField(
        default=False, verbose_name=_("Public"), help_text=_("If true, the factsheet is automatically subscribable")
    )
    email_contacts = models.ManyToManyField(
        "directory.EmailContact",
        through=MailingListEmailContactThroughModel,
        related_name="mailing_lists",
        blank=True,
        verbose_name=_("Subcribers"),
    )

    def __str__(self) -> str:
        return self.title

    def unsubscribe(self, email_contact: EmailContact, **kwargs):
        """
        Wrapper around the corresponding method in MailingListEmailContactThroughModel. Keyword argument matches the underlying signature
        """
        rel = MailingListEmailContactThroughModel.objects.get_or_create(
            email_contact=email_contact, mailing_list=self
        )[0]
        if rel.status == MailingListEmailContactThroughModel.Status.SUBSCRIBED:
            rel.change_state(**kwargs)

    def subscribe(self, email_contact: EmailContact, **kwargs):
        """
        Wrapper around the corresponding method in MailingListEmailContactThroughModel. Keyword argument matches the underlying signature
        """
        rel = MailingListEmailContactThroughModel.objects.get_or_create(
            email_contact=email_contact, mailing_list=self
        )[0]
        if rel.status == MailingListEmailContactThroughModel.Status.UNSUBSCRIBED:
            rel.change_state(**kwargs)

    @classmethod
    def get_subscribed_mailing_lists(cls, email_contact):
        return cls.objects.annotate(
            is_subscribe=Exists(
                MailingListEmailContactThroughModel.objects.filter(
                    mailing_list=OuterRef("id"),
                    email_contact=email_contact,
                    status=MailingListEmailContactThroughModel.Status.SUBSCRIBED,
                )
            )
        ).filter(is_subscribe=True)

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbmailing:mailinglist"

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbmailing:mailinglistrepresentation-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{title}}"


@receiver(post_save, sender=MailingListSubscriberChangeRequest)
def post_save_mailing_request(sender, instance, created, **kwargs):
    """
    MailingListSubscriberChangeRequest post_save signal: Send the notification email if needed
    """

    if created and instance.status == MailingListSubscriberChangeRequest.Status.PENDING.name:
        for user in MailingListSubscriberChangeRequest.get_approvers():
            entry_name = instance.email_contact.address
            if instance.email_contact.entry:
                entry_name += f" ({instance.email_contact.entry.computed_str})"

            send_notification(
                code="wbmailing.mailinglistsubscriberchangerequest.notify",
                title=_("New in Mailing Subscription Request Change for {}").format(entry_name),
                body=_("User requested to {} {} to the mailing list {}").format(
                    instance.type, entry_name, instance.mailing_list.title
                ),
                user=user,
                reverse_name="wbmailing:mailinglistsubscriberchangerequest-detail",
                reverse_args=[instance.id],
            )


@receiver(deactivate_profile)
@receiver(post_delete, sender="directory.Entry")
@receiver(post_delete, sender="directory.Person")
@receiver(post_delete, sender="directory.Company")
def handle_user_deactivation(sender, instance, substitute_profile=None, **kwargs):
    for email_contact in EmailContact.objects.filter(entry_id=instance.id):
        for rel in MailingListEmailContactThroughModel.objects.filter(
            email_contact=email_contact, status=MailingListEmailContactThroughModel.Status.SUBSCRIBED
        ):
            rel.change_state(reason=gettext("User's deactivation"), automatically_approve=True)
