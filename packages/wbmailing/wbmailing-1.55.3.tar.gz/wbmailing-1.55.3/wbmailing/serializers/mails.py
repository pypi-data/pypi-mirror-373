from datetime import timedelta

from django.utils import timezone
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from dynamic_preferences.registries import global_preferences_registry
from rest_framework import serializers
from rest_framework.reverse import reverse
from wbcore import serializers as wb_serializers
from wbcore.contrib.directory.models import EmailContact
from wbcore.contrib.directory.serializers import (
    EmailContactRepresentationSerializer,
    EntryRepresentationSerializer,
    PersonRepresentationSerializer,
)

from wbmailing import models

from .mailing_lists import MailingListRepresentationSerializer


class MailRepresentationSerializer(wb_serializers.RepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbmailing:mail-detail")

    class Meta:
        model = models.Mail
        fields = ("id", "subject", "_detail")


class MassMailRepresentationSerializer(wb_serializers.RepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbmailing:massmail-detail")

    class Meta:
        model = models.MassMail
        fields = ("id", "subject", "_detail")


class MailTemplateRepresentationSerializer(wb_serializers.RepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbmailing:mailtemplate-detail")

    class Meta:
        model = models.MailTemplate
        fields = ("id", "title", "_detail")


class MassMailListSerializer(wb_serializers.ModelSerializer):
    _creator = PersonRepresentationSerializer(source="creator")
    _mailing_lists = MailingListRepresentationSerializer(label=_("Mailing List"), source="mailing_lists", many=True)
    _excluded_mailing_lists = MailingListRepresentationSerializer(
        label=_("Excluded Mailing List"), source="excluded_mailing_lists", many=True
    )
    _template = MailTemplateRepresentationSerializer(source="template")
    subject = wb_serializers.CharField(required=True, label=_("Subject"))

    class Meta:
        model = models.MassMail
        fields = (
            "id",
            "status",
            "mailing_lists",
            "_mailing_lists",
            "excluded_mailing_lists",
            "_excluded_mailing_lists",
            "from_email",
            "template",
            "_template",
            "subject",
            "created",
            "creator",
            "_creator",
            "send_at",
        )


class MassMailModelSerializer(MassMailListSerializer):
    from_email = wb_serializers.CharField(
        default=lambda: global_preferences_registry.manager()["wbmailing__default_source_mail"], label=_("From")
    )

    @wb_serializers.register_resource()
    def send_test_mail(self, instance, request, user):
        return {
            "send_test_mail": reverse(
                "wbmailing:massmail-sendtestmail",
                args=[instance.id],
                request=request,
            )
        }

    @wb_serializers.register_resource()
    def mails(self, instance, request, user):
        return {
            "mails": reverse(
                "wbmailing:massmail-mailstatus-list",
                args=[instance.id],
                request=request,
            ),
            "events": reverse(
                "wbmailing:massmail-mailevent-list",
                args=[instance.id],
                request=request,
            ),
        }

    @wb_serializers.register_resource()
    def analytics(self, instance, request, user):
        return {
            "mailstatus_barchart": reverse(
                "wbmailing:massmail-mailstatusbarchart-list", args=[instance.id], request=request
            ),
            "mailclick_barchart": reverse(
                "wbmailing:massmail-mailclickbarchart-list", args=[instance.id], request=request
            ),
            "clients_barchart": reverse(
                "wbmailing:massmail-clientsbarchart-list", args=[instance.id], request=request
            ),
            "country_barchart": reverse(
                "wbmailing:massmail-countrybarchart-list", args=[instance.id], request=request
            ),
            "region_barchart": reverse("wbmailing:massmail-regionbarchart-list", args=[instance.id], request=request),
        }

    def create(self, validated_data, *args, **kwargs):
        if request := self.context.get("request"):
            validated_data["creator"] = request.user.profile
        return super().create(validated_data, *args, **kwargs)

    class Meta:
        model = models.MassMail
        fields = (
            "id",
            "status",
            "mailing_lists",
            "_mailing_lists",
            "excluded_mailing_lists",
            "_excluded_mailing_lists",
            "from_email",
            "template",
            "_template",
            "subject",
            "created",
            "body",
            "creator",
            "_creator",
            "send_at",
            "attachment_url",
            "_additional_resources",
        )

    def validate(self, data):
        send_at = data.get("send_at", None)
        if send_at:
            if send_at < timezone.now() - timedelta(minutes=1):
                raise serializers.ValidationError(
                    {"non_field_errors": gettext("Send time shouldn't be earlier than now.")}
                )
        return super().validate(data)


class MailModelSerializer(wb_serializers.ModelSerializer):
    from_email = wb_serializers.CharField(
        default=wb_serializers.CurrentUserDefault(user_attr="email"), label=_("From")
    )
    created = wb_serializers.DateTimeField(default=lambda: timezone.now(), label=_("Created"))
    _mass_mail = MassMailRepresentationSerializer(many=False, source="mass_mail")
    _template = MailTemplateRepresentationSerializer(many=False, source="template")
    _to_email = EmailContactRepresentationSerializer(many=True, source="to_email")
    _cc_email = EmailContactRepresentationSerializer(many=True, source="cc_email")
    _bcc_email = EmailContactRepresentationSerializer(many=True, source="bcc_email")

    status = wb_serializers.ChoiceField(
        choices=models.MailEvent.EventType.choices, default=models.MailEvent.EventType.UNKNOWN, read_only=True
    )

    @wb_serializers.register_resource()
    def mail_event(self, instance, request, user):
        return {
            "mailevent": reverse(
                "wbmailing:mail-mailevent-list",
                args=[instance.id],
                request=request,
            ),
            "resend_mail": reverse(
                "wbmailing:mail-resend",
                args=[instance.id],
                request=request,
            ),
        }

    class Meta:
        model = models.Mail
        fields = (
            "id",
            "created",
            "last_send",
            "template",
            "_template",
            "message_ids",
            "mass_mail",
            "_mass_mail",
            "from_email",
            "to_email",
            "_to_email",
            "cc_email",
            "_cc_email",
            "bcc_email",
            "_bcc_email",
            "subject",
            "body",
            "status",
            "_additional_resources",
        )


class MailStatusMassMailModelSerializer(wb_serializers.ModelSerializer):
    mail_id = wb_serializers.CharField(read_only=True)
    _entry = EntryRepresentationSerializer(source="entry")
    status = wb_serializers.ChoiceField(
        choices=(*models.MailEvent.EventType.choices, ("NOT_SENT", gettext("Not Sent"))),
        default="NOT_SENT",
        read_only=True,
    )

    class Meta:
        model = EmailContact
        fields = ("id", "entry", "_entry", "address", "status", "mail_id")


class MailTemplateModelSerializer(wb_serializers.ModelSerializer):
    class Meta:
        model = models.MailTemplate
        fields = ("id", "title", "template")


class MailEventModelSerializer(wb_serializers.ModelSerializer):
    _mail = MailRepresentationSerializer(source="mail")

    class Meta:
        model = models.MailEvent
        fields = (
            "id",
            "mail",
            "_mail",
            "timestamp",
            "event_type",
            "reject_reason",
            "description",
            "recipient",
            "click_url",
            "ip",
            "user_agent",
        )
