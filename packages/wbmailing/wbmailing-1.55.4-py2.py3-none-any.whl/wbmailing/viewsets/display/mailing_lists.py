from typing import Optional

from django.utils.translation import gettext as _
from wbcore.contrib.color.enums import WBColor
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
    create_simple_section,
)
from wbcore.metadata.configs.display.instance_display.utils import repeat_field
from wbcore.metadata.configs.display.view_config import DisplayViewConfig

from wbmailing import models


class MailingListDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="title", label=_("Title")),
                dp.Field(key="nb_subscribers", label=_("Subscribers")),
                dp.Field(key="is_public", label=_("Public")),
            ]
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [["title", "nb_subscribers", "is_public"], [repeat_field(3, "email_contacts_section")]],
            [
                create_simple_section(
                    "email_contacts_section",
                    _("Email Contacts"),
                    [["email_contacts"]],
                    "email_contacts",
                    collapsed=True,
                )
            ],
        )


class MailingListSubscriberChangeRequestDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="type", label=_("Type")),
                dp.Field(key="email_contact", label=_("Email Contact")),
                dp.Field(key="entry_repr", label=_("Entry")),
                dp.Field(key="requester", label=_("Requester")),
                dp.Field(key="mailing_list", label=_("Mailing List")),
                dp.Field(key="created", label=_("Creation Date")),
                dp.Field(key="expiration_date", label=_("Expiration Date")),
                dp.Field(key="reason", label=_("Reason")),
            ],
            legends=[
                dp.Legend(
                    key="status",
                    items=[
                        dp.LegendItem(
                            icon=WBColor.YELLOW_LIGHT.value,
                            label=models.MailingListSubscriberChangeRequest.Status.PENDING.label,
                            value=models.MailingListSubscriberChangeRequest.Status.PENDING,
                        ),
                        dp.LegendItem(
                            icon=WBColor.GREEN_LIGHT.value,
                            label=models.MailingListSubscriberChangeRequest.Status.APPROVED.label,
                            value=models.MailingListSubscriberChangeRequest.Status.APPROVED,
                        ),
                        dp.LegendItem(
                            icon=WBColor.RED_LIGHT.value,
                            label=models.MailingListSubscriberChangeRequest.Status.DENIED.label,
                            value=models.MailingListSubscriberChangeRequest.Status.DENIED,
                        ),
                    ],
                )
            ],
            formatting=[
                dp.Formatting(
                    column="status",
                    formatting_rules=[
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.YELLOW_LIGHT.value},
                            condition=(
                                "==",
                                models.MailingListSubscriberChangeRequest.Status.PENDING,
                            ),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.GREEN_LIGHT.value},
                            condition=(
                                "==",
                                models.MailingListSubscriberChangeRequest.Status.APPROVED,
                            ),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.RED_LIGHT.value},
                            condition=(
                                "==",
                                models.MailingListSubscriberChangeRequest.Status.DENIED,
                            ),
                        ),
                    ],
                )
            ],
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                [repeat_field(3, "status")],
                ["email_contact", "mailing_list", "expiration_date"],
                [
                    "requester",
                    "approver",
                    ".",
                ],
                [
                    "created",
                    "updated",
                    ".",
                ],
                [repeat_field(3, "reason")],
            ]
        )


class MailingListSubscriberRequestMailingListDisplayConfig(MailingListSubscriberChangeRequestDisplayConfig):
    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                [repeat_field(2, "status")],
                ["expiration_date", "email_contact"],
            ]
        )


class EmailContactMailingListDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="status", label=_("Status")),
                dp.Field(key="email_contact", label=_("Email Contact")),
                dp.Field(key="expiration_date", label=_("Expiration Date")),
                dp.Field(key="is_pending_request_change", label=_("Pending Change")),
            ]
        )


class MailingListEntryDisplayConfig(MailingListDisplayConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="status", label=_("Status")),
                dp.Field(key="mailing_list", label=_("Mailing List")),
                dp.Field(key="is_public", label=_("Public")),
                dp.Field(key="expiration_date", label=_("Expiration Date")),
                dp.Field(key="is_pending_request_change", label=_("Pending Change")),
            ]
        )


class MailingListEntryCompanyDisplayConfig(MailingListEntryDisplayConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="title", label=_("Mailing List")),
                dp.Field(key="is_public", label=_("Public")),
            ]
        )


class MailingListSubscriberRequestEntryDisplayConfig(MailingListSubscriberChangeRequestDisplayConfig):
    def get_instance_display(self) -> Display:
        return create_simple_display(
            [[repeat_field(3, "status")], ["email_contact", "mailing_list", "expiration_date"]]
        )
