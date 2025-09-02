import json
from datetime import timedelta

from anymail.exceptions import AnymailRecipientsRefused
from anymail.signals import tracking
from celery import shared_task
from django.apps import apps
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.files.base import ContentFile
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.db.models import Count, OuterRef, Subquery
from django.dispatch import receiver
from django.template import Context, Template
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.translation import gettext, pgettext_lazy
from django.utils.translation import gettext_lazy as _
from django_fsm import FSMField, transition
from dynamic_preferences.registries import global_preferences_registry
from psycopg.types.range import TimestamptzRange
from rest_framework.reverse import reverse
from sentry_sdk import capture_message
from wbcore.contrib.color.enums import WBColor
from wbcore.contrib.directory.models import EmailContact
from wbcore.contrib.documents.models import Document, DocumentType
from wbcore.contrib.documents.models.mixins import DocumentMixin
from wbcore.contrib.icons import WBIcon
from wbcore.enums import RequestType
from wbcore.markdown.template import resolve_markdown
from wbcore.metadata.configs.buttons import ActionButton, ButtonDefaultColor
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    create_simple_display,
)
from wbcore.models import WBModel
from wbcore.utils.html import convert_html2text

from .mailing_lists import MailingListEmailContactThroughModel


def can_administrate_mail(mail, user):
    return user.has_perm("wbmailing.can_administrate_mail")


class MassMail(DocumentMixin, WBModel):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", _("Draft")
        PENDING = "PENDING", _("Pending")
        SENT = "SENT", _("Sent")
        SEND_LATER = "SEND LATER", _("Send later")
        DENIED = "DENIED", _("Denied")

    class Meta:
        verbose_name = _("Mass Mail")
        verbose_name_plural = _("Mass Mails")
        permissions = (("can_administrate_mail", "Can administrate mail"),)

    status = FSMField(default=Status.DRAFT, choices=Status.choices, verbose_name=_("Status"))

    @classmethod
    def subquery_expected_mails(cls, massmail_name="pk"):
        """
        Create subquery to count expected mails

        Arguments:
            massmail_name {str} -- Outerref field
        """
        return Subquery(
            EmailContact.objects.filter(subscriptions__mails=OuterRef(massmail_name))
            .values("subscriptions__mails")
            .annotate(c=Count("subscriptions__mails"))
            .values("c")[:1],
            output_field=models.IntegerField(),
        )

    BUTTON_SUBMIT = ActionButton(
        method=RequestType.PATCH,
        identifiers=("wbmailing:massmail",),
        icon=WBIcon.SEND.icon,
        color=ButtonDefaultColor.WARNING,
        key="submit",
        label=pgettext_lazy("Massmail draft", "Submit"),
        action_label=_("Submitting"),
        description_fields=_("<p>Subject: {{subject}}</p>"),
    )

    @transition(
        field=status,
        source=[Status.DRAFT],
        target=Status.PENDING,
        custom={"_transition_button": BUTTON_SUBMIT},
    )
    def submit(self, by=None, description=None, **kwargs):
        pass

    BUTTON_DENIED = ActionButton(
        method=RequestType.PATCH,
        identifiers=("wbmailing:massmail",),
        icon=WBIcon.REJECT.icon,
        color=ButtonDefaultColor.ERROR,
        key="deby",
        label=_("Deny"),
        action_label=_("Denial"),
        description_fields=_("<p>Subject: {{subject}}</p>"),
    )

    @transition(
        field=status,
        source=[Status.PENDING],
        target=Status.DENIED,
        permission=can_administrate_mail,
        custom={"_transition_button": BUTTON_DENIED},
    )
    def deny(self, by=None, description=None, **kwargs):
        pass

    BUTTON_REVISE = ActionButton(
        method=RequestType.PATCH,
        identifiers=("wbmailing:massmail",),
        icon=WBIcon.EDIT.icon,
        color=ButtonDefaultColor.WARNING,
        key="revise",
        label=_("Revise"),
        action_label=_("Revision"),
        description_fields=_("<p>Subject: {{subject}}</p>"),
    )

    @transition(
        field=status,
        source=[Status.PENDING],
        target=Status.DRAFT,
        permission=can_administrate_mail,
        custom={"_transition_button": BUTTON_REVISE},
    )
    def revise(self, by=None, description=None, **kwargs):
        pass

    BUTTON_SEND = ActionButton(
        method=RequestType.PATCH,
        identifiers=("wbmailing:massmail",),
        icon=WBIcon.MAIL.icon,
        color=ButtonDefaultColor.SUCCESS,
        key="send",
        label=_("Send"),
        action_label=_("Sending"),
        description_fields=_("<p>Subject: {{subject}}</p><p>Mailing Lists: {{mailing_lists}}</p>"),
    )

    @transition(
        field=status,
        source=[Status.PENDING, Status.SEND_LATER],
        target=Status.SENT,
        permission=lambda instance, user: user.has_perm("wbmailing.can_administrate_mail") and not instance.send_at,
        custom={"_transition_button": BUTTON_SEND},
    )
    def send(self, by=None, description=None, **kwargs):
        send_mail_task.delay(self.id)

    BUTTON_SEND_LATER = ActionButton(
        method=RequestType.PATCH,
        identifiers=("wbmailing:massmail",),
        icon=WBIcon.SEND_LATER.icon,
        key="sendlater",
        label=_("Send Later"),
        action_label=_("Sending later"),
        description_fields=_("<p>Subject: {{subject}}</p><p>Mailing Lists: {{mailing_lists}}</p>"),
        instance_display=create_simple_display([["send_at"]]),
    )

    @transition(
        field=status,
        source=[Status.PENDING, Status.SENT, Status.SEND_LATER],
        target=Status.SEND_LATER,
        permission=lambda instance, user: user.has_perm("wbmailing.can_administrate_mail")
        and (not instance.send_at or instance.send_at > timezone.now()),
        custom={"_transition_button": BUTTON_SEND_LATER},
    )
    def sendlater(self, by=None, description=None, **kwargs):
        pass

    @classmethod
    def get_emails(cls, included_mailing_list_ids: list[int], excluded_mailing_list_ids: list[int] = None):
        included_emails_id = MailingListEmailContactThroughModel.objects.filter(
            status=MailingListEmailContactThroughModel.Status.SUBSCRIBED, mailing_list__in=included_mailing_list_ids
        ).values_list("email_contact", flat=True)

        excluded_addresses = (
            MailingListEmailContactThroughModel.objects.filter(
                status=MailingListEmailContactThroughModel.Status.SUBSCRIBED,
                mailing_list__in=excluded_mailing_list_ids,
            ).values_list("email_contact__address", flat=True)
            if excluded_mailing_list_ids
            else []
        )
        return (
            EmailContact.objects.filter(id__in=included_emails_id)
            .exclude(address__in=list(excluded_addresses))
            .distinct("address")
        )

    def get_mail_addresses(self):
        return self.get_emails(
            self.mailing_lists.values_list("id"), self.excluded_mailing_lists.values_list("id")
        ).values("address")

    def create_email(self, email):
        global_preferences = global_preferences_registry.manager()
        context = MassMail.get_context(email, self.subject, self.attachment_url)
        if self.documents and self.documents.exists():
            context.update(
                {"urls": [attachment.generate_shareable_link().link for attachment in self.documents.all()]}
            )
        rendered_subject = Template(self.subject).render(Context(context))
        body = resolve_markdown(self.body, extensions=["sane_lists"])
        if self.template:
            rendered_body = self.template.render_content(body, extra_context=context)
        else:
            rendered_body = Template(body).render(Context(context))

        from_mail = self.from_email or global_preferences["wbmailing__default_source_mail"]

        return Mail.get_mailmessage(
            rendered_subject, rendered_body, from_mail, [email], attachments=self.documents, mass_mail=self
        )

    def send_test_mail(self, email):
        """
        Send a test mail

        Arguments:
            email {str} -- The address to send the test mail to
        """
        self.subject = _("Test mail: {}").format(self.subject)

        msg = self.create_email(email)
        msg.send()

    from_email = models.EmailField(null=True, blank=True, verbose_name=_("From"))
    template = models.ForeignKey(
        "MailTemplate",
        related_name="mass_mails",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Template"),
    )
    mailing_lists = models.ManyToManyField(
        "MailingList",
        related_name="mails",
        verbose_name=_("Mailing Lists"),
        help_text=_("The mailing lists to extract emails from. Duplicates will be skipped."),
    )
    excluded_mailing_lists = models.ManyToManyField(
        "MailingList",
        related_name="excluded_mails",
        verbose_name=_("Excluded Mailing Lists"),
        help_text=_(
            "The mailing lists to exlude emails from. The resulting list of emails is equals to Mailing Lists - Excluded Mailing Lists "
        ),
        blank=True,
    )
    subject = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Subject"))
    body = models.TextField(default="", verbose_name=_("Body"))

    attachment_url = models.URLField(null=True, blank=True, verbose_name=_("Attachment (URL)"))

    body_json = models.JSONField(default=dict, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, verbose_name=_("Created"))
    creator = models.ForeignKey(
        "directory.Person",
        related_name="created_mails",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name=_("Creator"),
    )

    send_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Send At"))

    def __str__(self):
        return self.subject

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbmailing:massmail"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbmailing:massmailrepresentation-list"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{subject}}"

    @classmethod
    def get_context(cls, email, subject=None, attachment_url=None):
        emails = EmailContact.objects.filter(address=email)
        context = {"email": email}
        if subject:
            context["subject"] = subject
        if attachment_url:
            context["attachment_url"] = attachment_url
        if emails.exists():
            email_contact = emails.first()
            unsubscribe_url = f'{settings.BASE_ENDPOINT_URL}{reverse("wbmailing:manage_mailing_list_subscriptions", args=[email_contact.id])}'
            context["unsubscribe"] = f"<a href={unsubscribe_url}>" + _("Unsubscribe</a>")
            entry = email_contact.entry
            if entry:
                if salutation := entry.salutation:
                    context["salutation"] = salutation
                casted_entry = entry.get_casted_entry()
                if hasattr(casted_entry, "first_name"):
                    context["first_name"] = casted_entry.first_name
                if hasattr(casted_entry, "last_name"):
                    context["last_name"] = casted_entry.last_name
        return context


class Mail(DocumentMixin, WBModel):
    class Status(models.TextChoices):
        OPENED = "OPENED", _("Opened")
        DELIVERED = "DELIVERED", _("Delivered")
        BOUNCED = "BOUNCED", _("Bounced")
        OTHER = "OTHER", _("Other")

    created = models.DateTimeField(auto_now_add=True, verbose_name=_("Created"))
    last_send = models.DateTimeField(verbose_name=_("Last Sent"), default=timezone.now)
    template = models.ForeignKey(
        "MailTemplate",
        related_name="mails",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Template"),
    )

    message_ids = ArrayField(models.CharField(max_length=255, null=True, blank=True), default=list)
    mass_mail = models.ForeignKey(
        "MassMail", related_name="mails", null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_("Mass Mail")
    )

    from_email = models.EmailField(verbose_name=_("From"))
    to_email = models.ManyToManyField("directory.EmailContact", related_name="mail_to", verbose_name=_("To"))
    cc_email = models.ManyToManyField(
        "directory.EmailContact", related_name="mail_cc", blank=True, verbose_name=_("CC")
    )
    bcc_email = models.ManyToManyField(
        "directory.EmailContact", related_name="mail_bcc", blank=True, verbose_name=_("BCC")
    )

    subject = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Subject"))
    body = models.TextField(blank=True, null=True, verbose_name=_("body"))
    body_json = models.JSONField(default=dict, null=True, blank=True)

    def resend(self):
        """
        Resend that mail
        """
        context = {}
        if self.to_email.count() == 1:
            context = MassMail.get_context(self.to_email.first().address, self.subject)
        if self.documents.exists():
            context.update(
                {"urls": [attachment.generate_shareable_link().link for attachment in self.documents.all()]}
            )
        rendered_subject = Template(self.subject).render(Context(context))

        if self.mass_mail:
            body = resolve_markdown(self.mass_mail.body, extensions=["sane_lists"])
            template = self.mass_mail.template
            if self.mass_mail.template:
                rendered_body = template.render_content(body, extra_context=context)
            else:
                rendered_body = Template(body).render(Context(context))
        else:
            rendered_body = self.body

        msg = {
            "subject": rendered_subject,
            "body": rendered_body,
            "from_email": self.from_email,
            "to": list(self.to_email.values_list("address", flat=True)),
            "bcc": list(self.bcc_email.values_list("address", flat=True)),
            "cc": list(self.cc_email.values_list("address", flat=True)),
            "mail_id": self.id,
        }
        if self.mass_mail:
            msg["mass_mail_id"] = self.mass_mail.id
        send_mail_as_task.delay(**msg)

    def convert_files_to_documents(self, attachments, alternatives):
        # If DMS sends this email, we expect to find an alternative containing a encoded dictionary with the
        # necessary information to retreive the document object
        dms_alternatives = list(
            map(
                lambda x: json.loads(x[0].decode("ascii")),
                filter(lambda x: x[1] == "wbdms/document", alternatives),  # leave this mimetype. Used by wbcore
            )
        )

        document_type, created = DocumentType.objects.get_or_create(name="mailing")
        for name, payload, mimetype in attachments:
            # If an alternative sent from DMS is found, we match against the attachment email.
            dms_elements = list(filter(lambda x: x["filename"] == name, dms_alternatives))
            if (len(dms_elements) == 1) and (document_id := dms_elements[0].get("id", None)):
                document = Document.objects.get(id=document_id)
            # Otherwise, we update or create the corresponding Document objects based on its generated system_key
            else:
                content_file = ContentFile(payload, name=name)
                system_key_base = f"mail-{self.id}" if not self.mass_mail else f"massmail-{self.mass_mail.id}"
                document, created = Document.objects.update_or_create(
                    document_type=document_type,
                    system_created=True,
                    system_key=f"{system_key_base}-{name}",
                    defaults={"file": content_file},
                )
            document.link(self)

    class Meta:
        verbose_name = _("Mail")
        verbose_name_plural = _("Mails")

    def __str__(self):
        return self.subject or str(self.id)

    @classmethod
    def get_mailmessage(
        cls,
        rendered_subject,
        rendered_body,
        from_email,
        to,
        bcc=None,
        cc=None,
        attachments=None,
        mass_mail=None,
        mail=None,
    ):
        """
        Get a set of parameters and returns the custom mail message alternative

        Args:
            rendered_subject (str): The mail subject
            rendered_body (str): Mail Body
            from_email (str): from email address
            to (list<string>): List of destination addresses
            bcc (list<string>): List of BCC addressses
            cc (list<string>): List of CC addresses
            attachments (list<File>): List of File to attach to the mail
            mass_mail (MassMail): The originating mass mail, None if a direct mail
            mail (Mail): The Mail object in case of a resend
        """
        msg = EmailMultiAlternatives(
            strip_tags(rendered_subject), convert_html2text(rendered_body), from_email, to=to, cc=cc, bcc=bcc
        )

        msg.mass_mail = mass_mail
        msg.mail = mail
        msg.attach_alternative(rendered_body, "text/html")

        if attachments:
            for attachment in attachments:
                msg.attach(attachment.file.name, attachment.file.read())
        return msg

    @classmethod
    def create_mail_from_mailmessage(cls, msg, user=None):
        def get_or_create_emails(emails):
            for email in emails:
                if e := EmailContact.objects.filter(address=email).first():
                    yield e
                else:
                    yield EmailContact.objects.create(address=email)

        args = {}

        if mass_mail := getattr(msg, "mass_mail", None):
            args["mass_mail"] = mass_mail
            args["subject"] = mass_mail.subject
        else:
            args["subject"] = msg.subject
            args["body"] = msg.body
            for content, mimetype in msg.alternatives:
                if mimetype == "text/html":
                    args["body"] = content

        mail = Mail.objects.create(from_email=msg.from_email, **args)

        if msg.attachments:
            mail.convert_files_to_documents(msg.attachments, msg.alternatives)
        if hasattr(msg, "clear_attachments"):
            msg.attachments = []
        if msg.to:
            _email = get_or_create_emails(msg.to)
            if _email:
                mail.to_email.set(_email)
        if msg.cc:
            _email = get_or_create_emails(msg.cc)
            if _email:
                mail.cc_email.set(_email)
        if msg.bcc:
            _email = get_or_create_emails(msg.bcc)
            if _email:
                mail.bcc_email.set(_email)
        mail.save()
        return mail

    @classmethod
    def subquery_send_mails(cls, mass_mail_name="pk"):
        """
        Create subquery to count number of mails created from sent Mass Mail
        """
        return Subquery(
            cls.objects.filter(mass_mail=OuterRef(mass_mail_name))
            .values("mass_mail")
            .annotate(c=Count("mass_mail"))
            .values("c")[:1],
            output_field=models.IntegerField(),
        )

    @classmethod
    def get_endpoint_basename(cls):
        return "wbmailing:mail"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbmailing:mailrepresentation-list"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{subject}}"


class MailEvent(models.Model):
    class EventType(models.TextChoices):
        """Constants for normalized Anymail event types"""

        CREATED = "CREATED", _("Created")  # Default Type
        QUEUED = "QUEUED", _("Queued")  # the ESP has accepted the message and will try to send it (possibly later)
        SENT = "SENT", _("Sent")  # the ESP has sent the message (though it may or may not get delivered)
        RESENT = "RESENT", _("Resent")
        REJECTED = (
            "REJECTED",
            _("Rejected"),
        )  # the ESP refused to send the messsage (e.g., suppression list, policy, invalid email)
        FAILED = "FAILED", _("Failed")  # the ESP was unable to send the message (e.g., template rendering error)
        BOUNCED = "BOUNCED", _("Bounced")  # rejected or blocked by receiving MTA
        DEFERRED = (
            "DEFERRED",
            _("Deferred"),
        )  # delayed by receiving MTA; should be followed by a later BOUNCED or DELIVERED
        DELIVERED = "DELIVERED", _("Delivered")  # accepted by receiving MTA
        AUTORESPONDED = "AUTORESPONDED", _("Autoresponded")  # a bot replied
        OPENED = "OPENED", _("Opened")  # open tracking
        CLICKED = "CLICKED", _("Clicked")  # click tracking
        COMPLAINED = "COMPLAINED", _("Complained")  # recipient reported as spam (e.g., through feedback loop)
        UNSUBSCRIBED = "UNSUBSCRIBED", _("Unsubscribed")  # recipient attempted to unsubscribe
        SUBSCRIBED = "SUBSCRIBED", _("Subscribed")  # signed up for mailing list through ESP-hosted form
        INBOUND = "INBOUND", _("Inbound")  # received message
        INBOUND_FAILED = "INBOUND_FAILED", _("Inbound Failed")
        UNKNOWN = "UNKNOWN", _("Unknown")  # anything else

        @classmethod
        def get_color(cls, name):
            return {
                "CREATED": WBColor.GREY.value,
                "QUEUED": WBColor.BLUE.value,
                "SENT": WBColor.BLUE_LIGHT.value,
                "RESENT": WBColor.BLUE_DARK.value,
                "REJECTED": WBColor.RED_DARK.value,
                "FAILED": WBColor.RED_DARK.value,
                "BOUNCED": WBColor.RED.value,
                "DEFERRED": WBColor.RED_LIGHT.value,
                "DELIVERED": WBColor.YELLOW_LIGHT.value,
                "AUTORESPONDED": WBColor.YELLOW.value,
                "OPENED": WBColor.GREEN_LIGHT.value,
                "CLICKED": WBColor.GREEN.value,
                "COMPLAINED": WBColor.RED_DARK.value,
                "UNSUBSCRIBED": WBColor.RED_DARK.value,
                "SUBSCRIBED": WBColor.BLUE_DARK.value,
                "INBOUND": WBColor.YELLOW.value,
                "INBOUND_FAILED": WBColor.RED_DARK.value,
                "UNKNOWN": WBColor.YELLOW_DARK.value,
            }[name]

    class RejectReason(models.TextChoices):
        """Constants for normalized Anymail reject/drop reasons"""

        INVALID = "INVALID", _("invalid")  # bad address format
        BOUNCED = "BOUNCED", _("bounced")  # (previous) bounce from recipient
        TIMED_OUT = "TIMED_OUT", _("timed_out")  # (previous) repeated failed delivery attempts
        BLOCKED = "BLOCKED", _("blocked")  # ESP policy suppression
        SPAM = "SPAM", _("spam")  # (previous) spam complaint from recipient
        UNSUBSCRIBED = "UNSUBSCRIBED", _("unsubscribed")  # (previous) unsubscribe request from recipient
        OTHER = "OTHER", _("other")

    mail = models.ForeignKey("Mail", related_name="events", on_delete=models.CASCADE, verbose_name=_("Mail"))
    timestamp = models.DateTimeField(default=timezone.now, verbose_name=_("Datetime"))
    event_type = models.CharField(
        max_length=64, default=EventType.CREATED, choices=EventType.choices, verbose_name=_("Type")
    )
    reject_reason = models.CharField(
        max_length=64, null=True, blank=True, choices=RejectReason.choices, verbose_name=_("Rejection Reason")
    )
    description = models.TextField(null=True, blank=True, verbose_name=_("Description"))
    recipient = models.EmailField(null=True, blank=True, verbose_name=_("Recipient"))
    click_url = models.URLField(
        max_length=2048, null=True, blank=True, verbose_name=_("Clicked URL")
    )  # 2048 is the maximum allowed url size by browser.
    ip = models.CharField(max_length=126, null=True, blank=True, verbose_name=_("IP Used To Send Mail"))
    user_agent = models.TextField(null=True, blank=True)
    raw_data = models.JSONField(default=dict, null=True, blank=True, verbose_name=_("Raw Data"))
    metadata = models.JSONField(default=dict, null=True, blank=True, verbose_name=_("Metadata"))
    tags = ArrayField(models.CharField(max_length=64, null=True, blank=True), default=list)

    class Meta:
        verbose_name = _("Mail Event")
        verbose_name_plural = _("Mail Events")

    @classmethod
    def subquery_delivered_mails(cls, mass_mail_name="pk"):
        """
        Create subquery to count number of delivered mails
        """
        return Subquery(
            cls.objects.filter(event_type=MailEvent.EventType.DELIVERED, mail__mass_mail=OuterRef(mass_mail_name))
            .values("mail__mass_mail")
            .annotate(c=Count("mail__mass_mail"))
            .values("c")[:1],
            output_field=models.IntegerField(),
        )

    @classmethod
    def subquery_opened_mails(cls, mass_mail_name="pk"):
        """
        Create subquery to count number of opened mails
        """
        return Subquery(
            cls.objects.filter(event_type=MailEvent.EventType.OPENED, mail__mass_mail=OuterRef(mass_mail_name))
            .values("mail__mass_mail")
            .annotate(c=Count("mail__to_email", distinct=True))
            .values("c")[:1],
            output_field=models.IntegerField(),
        )

    @classmethod
    def subquery_clicked_mails(cls, mass_mail_name="pk"):
        """
        Create subquery to count number of clicked mails
        """
        return Subquery(
            cls.objects.filter(event_type=MailEvent.EventType.CLICKED, mail__mass_mail=OuterRef(mass_mail_name))
            .values("mail__mass_mail")
            .annotate(c=Count("mail__mass_mail"))
            .values("c")[:1],
            output_field=models.IntegerField(),
        )

    @classmethod
    def get_endpoint_basename(cls):
        return "wbmailing:mailevent"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{event_type}} ({{mail__subject}})"


class MailTemplate(WBModel):
    title = models.CharField(max_length=255)
    template = models.TextField()

    def render_content(self, content, extra_context=None):
        context = {"content": content}
        if extra_context:
            context = {**context, **extra_context}
        return Template(self.template).render(Context(context))

    class Meta:
        verbose_name = _("Mail Template")
        verbose_name_plural = _("Mail Templates")

    def __str__(self):
        return self.title

    @classmethod
    def get_endpoint_basename(cls):
        return "wbmailing:mailtemplate"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbmailing:mailtemplaterepresentation-list"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{title}}"


@receiver(tracking)
def handle_mail_tracking(sender, event, esp_name, **kwargs):
    """
    Signal triggered by the Sendgrid sdk. Create MailEvent
    """
    global_preferences = global_preferences_registry.manager()

    def handle_subscription_change(
        recipient, event_type, description, mass_mail, automatically_approve=False, reject_reason=None
    ):
        email_contacts = EmailContact.objects.filter(address=recipient)
        for email_contact in email_contacts:
            for mailing_list in mass_mail.mailing_lists.all():
                if event_type == MailEvent.EventType.SUBSCRIBED:
                    mailing_list.subscribe(
                        email_contact,
                        reason=gettext(
                            "Received an ESP resubscription request for {}. Please check the pending subscription change request"
                        ).format(recipient),
                    )
                else:
                    mailing_list.unsubscribe(
                        email_contact,
                        reason=gettext(
                            "Received an ESP unsubscription request for {}:\n <p>Event Type: {}</p>\n<p>Rejection Reason: {}</p>\n<p>Description: {}</p>\n<p>Automatically approve: {}</p>"
                        ).format(recipient, event_type, reject_reason, description, automatically_approve),
                        automatically_approve=automatically_approve,
                    )

    def get_mail(message_id, tags=[]):
        mail = Mail.objects.filter(message_ids__contains=[event.message_id]).first()
        if mail:
            return mail

        # We support only one tag
        tags = tags[0].split("-") if tags and isinstance(tags[0], str) else []
        if len(tags) == 2:
            try:
                _id = int(tags[1])
                if tags[0] == "massmail":
                    mail = Mail.objects.filter(mass_mail=_id, to_email__address=event.recipient).first()
                elif tags[0] == "mail":
                    mail = Mail.objects.get(id=_id)
            except ValueError:
                pass
        return mail

    event_type = event.event_type.upper()
    if event_type not in MailEvent.EventType.names:
        event_type = MailEvent.EventType.UNKNOWN

    reject_reason = None
    if event.reject_reason:
        reject_reason = event.reject_reason.upper()
        if reject_reason not in MailEvent.RejectReason.names:
            reject_reason = MailEvent.RejectReason.OTHER

    if event_type == MailEvent.EventType.UNKNOWN and event.esp_event.get("RecordType", None) == "SubscriptionChange":
        if event.esp_event.get("SuppressSending", True):
            event_type = MailEvent.EventType.UNSUBSCRIBED
            if reason := event.esp_event.get("SuppressionReason", None):
                if reason == "HardBounce":
                    reject_reason = MailEvent.RejectReason.BOUNCED
                elif reason == "SpamComplaint":
                    reject_reason = MailEvent.RejectReason.SPAM
                else:
                    reject_reason = MailEvent.RejectReason.UNSUBSCRIBED
        else:
            event_type = MailEvent.EventType.SUBSCRIBED

    mail = get_mail(event.message_id, event.tags)
    if mail:
        MailEvent.objects.create(
            mail=mail,
            timestamp=event.timestamp if event.timestamp else timezone.now(),
            event_type=event_type,
            recipient=event.recipient,
            reject_reason=reject_reason,
            user_agent=event.user_agent,
            click_url=event.click_url,
            description=event.description,
            raw_data=event.esp_event,
            tags=event.tags,
        )
        is_hard_bounce = event.esp_event.get("Type", None) == "HardBounce"
        if mail.mass_mail:  # we handle unsubscription and subscription only if the mail comes from a mass mail
            # Handle PostMark unsubcription notification
            if event_type in [
                MailEvent.EventType.REJECTED,
                MailEvent.EventType.COMPLAINED,
                MailEvent.EventType.UNSUBSCRIBED,
                MailEvent.EventType.SUBSCRIBED,
            ] or (event_type == MailEvent.EventType.BOUNCED and is_hard_bounce):
                handle_subscription_change(
                    event.recipient,
                    event_type,
                    event.description,
                    mail.mass_mail,
                    automatically_approve=is_hard_bounce
                    and global_preferences["wbmailing__automatically_approve_unsubscription_request_from_hard_bounce"],
                    reject_reason=reject_reason,
                )

    else:
        capture_message(gettext("Received event but could not find related mail"))


@shared_task
def send_mail_as_task(
    subject=None,
    body=None,
    from_email=None,
    to=None,
    bcc=None,
    cc=None,
    mass_mail_id=None,
    mail_id=None,
):
    msg = Mail.get_mailmessage(
        subject,
        body,
        from_email,
        to,
        bcc=bcc,
        cc=cc,
        mass_mail=MassMail.objects.get(id=mass_mail_id) if mass_mail_id else None,
        mail=Mail.objects.get(id=mail_id) if mail_id else None,
    )
    msg.send()


@shared_task
def send_mass_mail_as_task(mass_mail_id: int, email_address: str):
    mass_mail = MassMail.objects.get(id=mass_mail_id)
    try:
        msg = mass_mail.create_email(email_address)
        msg.send()
    except AnymailRecipientsRefused:
        global_preferences = global_preferences_registry.manager()
        for mailing_list in mass_mail.mailing_lists.exclude(id__in=mass_mail.excluded_mailing_lists.values("id")):
            for rel in MailingListEmailContactThroughModel.objects.filter(
                mailing_list=mailing_list,
                email_contact__address=email_address,
                status=MailingListEmailContactThroughModel.Status.SUBSCRIBED,
            ):
                rel.change_state(
                    automatically_approve=global_preferences[
                        "wbmailing__automatically_approve_unsubscription_request_from_hard_bounce"
                    ],
                    reason="Email address was rejected by our ESP.",
                )


@shared_task
def send_mail_task(mass_mail_id):
    """
    MailingListSubscriberChangeRequest post_save signal: Automatically approve if user is superuser/manager

    Arguments:
        mass_mail {MassMail} -- MassMail to send mails from
    """
    mass_mail = MassMail.objects.filter(id=mass_mail_id).first()

    if apps.is_installed("wbcrm.Activity"):  # Until we find something else
        from wbcrm.models import Activity, ActivityType

        activity_type, created = ActivityType.objects.get_or_create(slugify_title="email", defaults={"title": "Email"})
        Activity.objects.create(
            status=Activity.Status.REVIEWED,
            type=activity_type,
            title=_("Mass mail sent: {}").format(mass_mail.subject),
            description=mass_mail.body,
            period=TimestamptzRange(timezone.now(), timezone.now() + timedelta(minutes=1)),
            creator=mass_mail.creator,
            assigned_to=mass_mail.creator,
        )

    mass_mail.mails.all().delete()
    for subscriber in mass_mail.get_mail_addresses():
        send_mass_mail_as_task.delay(mass_mail.id, subscriber["address"])
