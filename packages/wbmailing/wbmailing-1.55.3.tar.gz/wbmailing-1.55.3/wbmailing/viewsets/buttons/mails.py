from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy
from rest_framework.reverse import reverse
from wbcore import serializers as wb_serializers
from wbcore.contrib.icons import WBIcon
from wbcore.enums import RequestType
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.buttons.view_config import ButtonViewConfig
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    create_simple_display,
)

from wbmailing.models import MassMail


class MassMailButtonConfig(ButtonViewConfig):
    def get_custom_instance_buttons(self):
        class SendTestMailActionButtonSerializer(wb_serializers.Serializer):
            to_test_email = wb_serializers.CharField(label=gettext_lazy("Send To"), default=self.request.user.email)

            class Meta:
                fields = ["to_test_email"]

        return {
            bt.ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbmailing:entry-mailinglist",),
                action_label=_("Sending test mail"),
                key="send_test_mail",
                description_fields=_("<p>Are you sure you want to send a test mail?</p>"),
                serializer=SendTestMailActionButtonSerializer,
                icon=WBIcon.CHART_SWITCHES.icon,
                title=_("Test Mail"),
                label=_("Test Mail"),
                instance_display=create_simple_display([["to_test_email"]]),
            ),
            bt.WidgetButton(key="mails", label=_("Mails' Status"), icon=WBIcon.MAIL_OPEN.icon),
        }


class MailButtonConfig(ButtonViewConfig):
    def get_custom_instance_buttons(self):
        title = gettext_lazy("Resend Mail")
        action_label = gettext_lazy("Resending mail")
        description = gettext_lazy("<p>Are you sure you want to resend the mail?</p>")
        icon = WBIcon.REPLACE.icon
        try:
            mail = self.view.get_object()
            if not mail.events.exists():
                title = gettext_lazy("Send Mail")
                action_label = gettext_lazy("Sending mail")
                description = gettext_lazy("<p>Are you sure you want to send the mail?</p>")
                icon = WBIcon.SEND.icon
        except AssertionError:
            pass
        return {
            bt.ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbmailing:mail",),
                action_label=action_label,
                key="resend_mail",
                description_fields=description,
                icon=icon,
                title=title,
                label=title,
            )
        }

    def get_custom_list_instance_buttons(self):
        return self.get_custom_instance_buttons()


class MailStatusMassMailButtonConfig(ButtonViewConfig):
    def get_custom_buttons(self):
        if not self.view.kwargs.get("pk", None) and (mass_mail_id := self.view.kwargs.get("mass_mail_id", None)):
            mass_mail = MassMail.objects.get(id=mass_mail_id)
            if mass_mail.status == MassMail.Status.SENT:
                return {
                    bt.ActionButton(
                        method=RequestType.PATCH,
                        identifiers=("wbmailing:massmail",),
                        endpoint=reverse(
                            "wbmailing:massmail-mailstatus-resendbouncedmails",
                            args=[mass_mail_id],
                            request=self.request,
                        ),
                        label=_("Resend Bounced Emails"),
                        description_fields=_(
                            """
                        <p>Do not abuse this function! Doing so will likely degrade your mailing reputation.</p>
                        <p>If you are sure, please confirm</>
                        <p>
                        """
                        ),
                        action_label=_("Resending bounced emails"),
                        title=_("Resend Bounced Emails"),
                    )
                }
        return set()
