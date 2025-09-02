from django.dispatch import receiver
from django.utils.translation import gettext as _
from rest_framework.reverse import reverse
from wbcore.contrib.directory.viewsets import (
    CompanyModelViewSet,
    EntryModelViewSet,
    PersonModelViewSet,
)
from wbcore.contrib.icons import WBIcon
from wbcore.enums import RequestType
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.buttons.view_config import ButtonViewConfig
from wbcore.signals.instance_buttons import add_instance_button


class MailingListSubcriptionRequestButtonConfig(ButtonViewConfig):
    def get_custom_buttons(self):
        if not hasattr(self.view.kwargs, "pk"):
            user = self.request.user
            if user.is_superuser or user.has_perm("wbmailing.administrate_mailinglistsubscriberchangerequest"):
                return {
                    bt.ActionButton(
                        method=RequestType.GET,
                        identifiers=("wbmailing:mailinglistsubscriberchangerequest",),
                        endpoint=reverse(
                            "wbmailing:mailinglistsubscriberchangerequest-approveall", args=[], request=self.request
                        ),
                        label=_("Approve All"),
                        description_fields=_(
                            """
                        <p>Do you really want to approve all pending subscriptions requests?</p>
                        """
                        ),
                        action_label=_("Approving all pending subscription requests"),
                        title=_("Approve all pending subscription requests"),
                    )
                }
        return {}


class MailingListButtonConfig(ButtonViewConfig):
    def get_custom_instance_buttons(self):
        return {
            bt.WidgetButton(key="mailevent_chart", label=_("Mail Penetration"), icon=WBIcon.FEEDBACK.icon),
        }

    def get_custom_list_instance_buttons(self):
        return self.get_custom_instance_buttons()


class MailingListEmailContactThroughModelButtonConfig(ButtonViewConfig):
    def get_custom_list_instance_buttons(self):
        return {
            bt.WidgetButton(key="requests", label="Changes Request History", icon=WBIcon.DATA_LIST.icon),
            bt.ActionButton(
                method=RequestType.PATCH,
                identifiers=("directory:email_contacts",),
                key="delete_from_mailinglist",
                label=_("Delete"),
                icon=WBIcon.DELETE.icon,
                description_fields=_(
                    "<p> Are you sure you want to delete {{_entry.computed_str}} from this mailinglist? Check with your compliance team if you are not sure</p>"
                ),
                title=_("Delete"),
                action_label=_("Deletion"),
            ),
            bt.ActionButton(
                method=RequestType.PATCH,
                identifiers=("directory:email_contacts",),
                key="unsubscribe",
                label=_("Unsubscribe"),
                icon=WBIcon.UNDO.icon,
                description_fields=_(
                    "<p> Are you sure you want to unsubscribe {{_entry.computed_str}} from this mailinglist? Until the entry exists, the user won't be able to resubscribe</p>"
                ),
                title=_("Unsubscribe"),
                action_label=_("Unsubscribing"),
            ),
        }


@receiver(add_instance_button, sender=PersonModelViewSet)
@receiver(add_instance_button, sender=EntryModelViewSet)
@receiver(add_instance_button, sender=CompanyModelViewSet)
def crm_adding_instance_buttons_ep(sender, many, *args, **kwargs):
    if not many:
        return bt.DropDownButton(
            label=_("Mailing"),
            icon=WBIcon.UNFOLD.icon,
            buttons=(bt.WidgetButton(key="mailinglist", label=_("Mailing"), icon=WBIcon.MAIL.icon),),
        )
