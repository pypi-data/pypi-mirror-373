from django.dispatch import receiver
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.reverse import reverse
from wbcore import serializers as wb_serializers
from wbcore.contrib.directory.serializers import (
    CompanyModelSerializer,
    EmailContactRepresentationSerializer,
    EntryModelSerializer,
    PersonModelSerializer,
    PersonRepresentationSerializer,
)
from wbcore.signals.serializers import add_instance_additional_resource

from wbmailing import models
from wbmailing.models import MailingListEmailContactThroughModel


class MailingListRepresentationSerializer(wb_serializers.RepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbmailing:mailinglist-detail")

    class Meta:
        model = models.MailingList
        fields = ("id", "title", "_detail")


class MailingListEntryRepresentationSerializer(MailingListRepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbmailing:mailinglist-detail")

    def get_filter_params(self, request):
        entry_id = request.parser_context["view"].kwargs.get("entry_id", None)
        return {"negative_entry": entry_id}

    class Meta:
        model = models.MailingList
        fields = ("id", "title", "_detail")


class MailingListListSerializer(wb_serializers.ModelSerializer):
    nb_subscribers = wb_serializers.IntegerField(read_only=True, label=_("Number of Subscribers"), default=0)

    class Meta:
        model = models.MailingList
        fields = (
            "id",
            "title",
            "is_public",
            "nb_subscribers",
        )


class MailingListModelSerializer(wb_serializers.ModelSerializer):
    nb_subscribers = wb_serializers.IntegerField(read_only=True, label=_("Number of Subscribers"), default=0)

    @wb_serializers.register_resource()
    def email_contacts(self, instance, request, user):
        # Do some something (checks, etc.)
        return {
            "mailevent_chart": reverse(
                "wbmailing:mailing_list-maileventchart-list", args=[instance.id], request=request
            ),
            "email_contacts": reverse(
                "wbmailing:mailing_list-email_contacts-list", args=[instance.id], request=request
            ),
        }

    class Meta:
        model = models.MailingList
        fields = ("id", "title", "is_public", "nb_subscribers", "_additional_resources")


class MailingListEmailContactThroughModelModelSerializer(wb_serializers.ModelSerializer):
    _email_contact = EmailContactRepresentationSerializer(source="email_contact")
    _mailing_list = MailingListRepresentationSerializer(source="mailing_list")

    in_charge = wb_serializers.CharField(read_only=True, label=_("Relationship Managers"))
    expiration_date = wb_serializers.DateField(read_only=True, label=_("Expiration Date"))
    is_public = wb_serializers.BooleanField(read_only=True, label=_("Public Mailing list"))
    is_pending_request_change = wb_serializers.BooleanField(
        read_only=True,
        default=False,
        label=_("Pending change request exists"),
        help_text=_("If true, a pending change request exists for this email and mailing list"),
    )

    @wb_serializers.register_resource()
    def delete_from_mailinglist(self, instance, request, user):
        res = {
            "requests": f'{reverse("wbmailing:mailinglistsubscriberchangerequest-list", args=[], request=request)}?email_contact={instance.email_contact.id}&mailing_list={instance.mailing_list.id}'
        }
        if getattr(instance, "expiration_date", None):
            res["remove_expiration_date"] = reverse(
                "wbmailing:mailinglistemailcontact-removeexpirationdate",
                args=[instance.id],
                request=request,
            )
        if instance.status != MailingListEmailContactThroughModel.Status.SUBSCRIBED:
            res["delete_from_mailinglist"] = reverse(
                "wbmailing:mailinglistemailcontact-delete",
                args=[instance.id],
                request=request,
            )
        else:
            res["unsubscribe"] = reverse(
                "wbmailing:mailinglistemailcontact-unsubscribe",
                args=[instance.id],
                request=request,
            )
        return res

    class Meta:
        model = MailingListEmailContactThroughModel
        fields = (
            "id",
            "status",
            "email_contact",
            "mailing_list",
            "_email_contact",
            "_mailing_list",
            "in_charge",
            "expiration_date",
            "is_public",
            "is_pending_request_change",
            "_additional_resources",
        )


class MailingListSubscriberChangeRequestModelSerializer(wb_serializers.ModelSerializer):
    _email_contact = EmailContactRepresentationSerializer(many=False, source="email_contact")
    _mailing_list = MailingListRepresentationSerializer(many=False, source="mailing_list")
    _requester = PersonRepresentationSerializer(source="requester", many=False)
    _approver = PersonRepresentationSerializer(source="approver", many=False)

    approver = wb_serializers.PrimaryKeyRelatedField(read_only=True, label=_("Approver"))
    requester = wb_serializers.PrimaryKeyRelatedField(read_only=True, label=_("Requester"))
    created = wb_serializers.DateTimeField(read_only=True, label=_("Created"))
    updated = wb_serializers.DateTimeField(read_only=True, label=_("Updated"))
    entry_repr = wb_serializers.CharField(read_only=True)
    type = wb_serializers.ChoiceField(choices=models.MailingListSubscriberChangeRequest.Type.choices, required=False)

    def validate(self, attrs):
        instance_id = self.instance.id if self.instance else None
        email_contact = attrs.get("email_contact", self.instance.email_contact if self.instance else None)
        mailing_list = attrs.get("mailing_list", self.instance.mailing_list if self.instance else None)
        if email_contact and mailing_list:
            if (
                models.MailingListSubscriberChangeRequest.objects.exclude(id=instance_id)
                .filter(
                    email_contact=email_contact,
                    mailing_list=mailing_list,
                    status=models.MailingListSubscriberChangeRequest.Status.PENDING.name,
                )
                .count()
                > 0
            ):
                raise serializers.ValidationError(
                    {
                        "non_field_errors": gettext("There is already a pending request to subscribe {} to {}").format(
                            email_contact.address, mailing_list.title
                        )
                    }
                )
        if not email_contact:
            raise serializers.ValidationError(
                {"email_contact": gettext("Email contact is missing for this request to be valid")}
            )
        return super().validate(attrs)

    def create(self, validated_data):
        if request := self.context.get("request"):
            validated_data["requester"] = request.user.profile
        return super().create(validated_data)

    class Meta:
        model = models.MailingListSubscriberChangeRequest
        fields = (
            "id",
            "status",
            "email_contact",
            "_email_contact",
            "email_contact",
            "mailing_list",
            "_mailing_list",
            "expiration_date",
            "type",
            "created",
            "updated",
            "requester",
            "_requester",
            "approver",
            "_approver",
            "reason",
            "entry_repr",
            "_additional_resources",
        )


@receiver(add_instance_additional_resource, sender=CompanyModelSerializer)
@receiver(add_instance_additional_resource, sender=PersonModelSerializer)
@receiver(add_instance_additional_resource, sender=EntryModelSerializer)
def crm_adding_additional_resource(sender, serializer, instance, request, user, **kwargs):
    return {
        "mailinglist": reverse("wbmailing:entry-mailinglist-list", args=[instance.id], request=request),
        "mailinglistsubscriptionrequests": reverse(
            "wbmailing:entry-mailinglistsubscriberchangerequest-list",
            args=[instance.id],
            request=request,
        ),
    }
