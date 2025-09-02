from typing import Optional

from django.utils.translation import gettext as _
from wbcore.contrib.color.enums import WBColor
from wbcore.enums import Unit
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.display import Display
from wbcore.metadata.configs.display.instance_display.layouts.inlines import Inline
from wbcore.metadata.configs.display.instance_display.layouts.layouts import Layout
from wbcore.metadata.configs.display.instance_display.operators import default
from wbcore.metadata.configs.display.instance_display.pages import Page
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    create_simple_display,
    create_simple_section,
)
from wbcore.metadata.configs.display.instance_display.styles import Style
from wbcore.metadata.configs.display.instance_display.utils import repeat_field
from wbcore.metadata.configs.display.view_config import DisplayViewConfig

from wbmailing import models


class MassMailDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="subject", label=_("Subject")),
                dp.Field(key="from_email", label=_("From")),
                dp.Field(key="template", label=_("Template")),
                dp.Field(key="mailing_lists", label=_("Mailing Lists")),
                dp.Field(key="excluded_mailing_lists", label=_("Excluded Mailing Lists")),
                dp.Field(key="created", label=_("Created")),
                dp.Field(key="creator", label=_("Creator")),
                dp.Field(key="send_at", label=_("Send At")),
            ],
            legends=[
                dp.Legend(
                    key="status",
                    items=[
                        dp.LegendItem(
                            icon=WBColor.GREEN_LIGHT.value,
                            label=models.MassMail.Status.SENT.label,
                            value=models.MassMail.Status.SENT,
                        ),
                        dp.LegendItem(
                            icon=WBColor.GREEN.value,
                            label=models.MassMail.Status.SEND_LATER.label,
                            value=models.MassMail.Status.SEND_LATER,
                        ),
                        dp.LegendItem(
                            icon=WBColor.YELLOW_LIGHT.value,
                            label=models.MassMail.Status.PENDING.label,
                            value=models.MassMail.Status.PENDING,
                        ),
                        dp.LegendItem(
                            icon=WBColor.BLUE_LIGHT.value,
                            label=models.MassMail.Status.DRAFT.label,
                            value=models.MassMail.Status.DRAFT,
                        ),
                        dp.LegendItem(
                            icon=WBColor.RED_LIGHT.value,
                            label=models.MassMail.Status.DENIED.label,
                            value=models.MassMail.Status.DENIED,
                        ),
                    ],
                )
            ],
            formatting=[
                dp.Formatting(
                    column="status",
                    formatting_rules=[
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.GREEN_LIGHT.value},
                            condition=("==", models.MassMail.Status.SENT),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.GREEN.value},
                            condition=("==", models.MassMail.Status.SEND_LATER),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.YELLOW_LIGHT.value},
                            condition=("==", models.MassMail.Status.PENDING),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.BLUE_LIGHT.value},
                            condition=("==", models.MassMail.Status.DRAFT),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.RED_LIGHT.value},
                            condition=("==", models.MassMail.Status.DENIED),
                        ),
                    ],
                )
            ],
        )

    def get_instance_display(self) -> Display:
        display = Display(
            pages=[
                Page(
                    title="Home",
                    layouts={
                        default(): Layout(
                            grid_template_areas=[
                                ["status", "status"],
                                ["subject", "subject"],
                                ["from_email", "template"],
                                ["mailing_lists", "excluded_mailing_lists"],
                                ["body", "body"],
                                ["attachment_url", "attachment_url"],
                            ]
                        )
                    },
                ),
                Page(
                    title="Analytics",
                    layouts={
                        default(): Layout(
                            grid_template_areas=[
                                ["mailstatus_barchart", "mailclick_barchart"],
                                ["region_barchart", "region_barchart"],
                                ["clients_barchart", "country_barchart"],
                            ],
                            grid_template_rows=[Style.px(600), Style.px(600), Style.px(600)],
                            inlines=[
                                Inline(key="mailstatus_barchart", endpoint="mailstatus_barchart"),
                                Inline(key="mailclick_barchart", endpoint="mailclick_barchart"),
                                Inline(key="clients_barchart", endpoint="clients_barchart"),
                                Inline(key="country_barchart", endpoint="country_barchart"),
                                Inline(key="region_barchart", endpoint="region_barchart"),
                            ],
                        )
                    },
                ),
                Page(
                    title="Events",
                    layouts={
                        default(): Layout(
                            grid_template_areas=[["events_key"]],
                            inlines=[Inline(key="events_key", endpoint="events")],
                            grid_template_columns=[
                                "minmax(min-content, 1fr)",
                            ],
                            grid_auto_rows=Style.MIN_CONTENT,
                        ),
                    },
                ),
            ]
        )

        return display


EVENTTYPE_LEGENDS = dp.Legend(
    key="status",
    items=[
        dp.LegendItem(
            icon=WBColor.GREY.value,
            label=models.MailEvent.EventType.CREATED.label,
            value=models.MailEvent.EventType.CREATED,
        ),
        dp.LegendItem(
            icon=WBColor.BLUE_LIGHT.value,
            label=models.MailEvent.EventType.QUEUED.label,
            value=models.MailEvent.EventType.QUEUED,
        ),
        dp.LegendItem(
            icon=WBColor.BLUE_DARK.value,
            label=models.MailEvent.EventType.UNKNOWN.label,
            value=models.MailEvent.EventType.UNKNOWN,
        ),
        dp.LegendItem(
            icon=WBColor.YELLOW_LIGHT.value,
            label=models.MailEvent.EventType.DELIVERED.label,
            value=models.MailEvent.EventType.DELIVERED,
        ),
        dp.LegendItem(
            icon=WBColor.GREEN_LIGHT.value,
            label=models.MailEvent.EventType.OPENED.label,
            value=models.MailEvent.EventType.OPENED,
        ),
        dp.LegendItem(
            icon=WBColor.GREEN.value,
            label=models.MailEvent.EventType.CLICKED.label,
            value=models.MailEvent.EventType.CLICKED,
        ),
        dp.LegendItem(
            icon=WBColor.RED_LIGHT.value,
            label=models.MailEvent.EventType.DEFERRED.label,
            value=models.MailEvent.EventType.DEFERRED,
        ),
        dp.LegendItem(
            icon=WBColor.RED.value,
            label=models.MailEvent.EventType.BOUNCED.label,
            value=models.MailEvent.EventType.BOUNCED,
        ),
        dp.LegendItem(
            icon=WBColor.RED_DARK.value,
            label=models.MailEvent.EventType.REJECTED.label,
            value=models.MailEvent.EventType.REJECTED,
        ),
    ],
)

EVENTTYPE_FORMATTING = dp.Formatting(
    column="status",
    formatting_rules=[
        dp.FormattingRule(
            style={"backgroundColor": WBColor.BLUE_LIGHT.value},
            condition=("==", models.MailEvent.EventType.QUEUED),
        ),
        dp.FormattingRule(
            style={"backgroundColor": WBColor.GREEN.value},
            condition=("==", models.MailEvent.EventType.CLICKED),
        ),
        dp.FormattingRule(
            style={"backgroundColor": WBColor.GREEN_LIGHT.value},
            condition=("==", models.MailEvent.EventType.OPENED),
        ),
        dp.FormattingRule(
            style={"backgroundColor": WBColor.YELLOW_LIGHT.value},
            condition=("==", models.MailEvent.EventType.DELIVERED),
        ),
        dp.FormattingRule(
            style={"backgroundColor": WBColor.RED.value},
            condition=("==", models.MailEvent.EventType.BOUNCED),
        ),
        dp.FormattingRule(
            style={"backgroundColor": WBColor.RED_LIGHT.value},
            condition=("==", models.MailEvent.EventType.DEFERRED),
        ),
        dp.FormattingRule(
            style={"backgroundColor": WBColor.GREY.value},
            condition=("==", models.MailEvent.EventType.CREATED),
        ),
        dp.FormattingRule(
            style={"backgroundColor": WBColor.RED_DARK.value},
            condition=("==", models.MailEvent.EventType.REJECTED),
        ),
    ],
)


class MailDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="mass_mail", label=_("Mass Mail")),
                dp.Field(key="subject", label=_("Subject")),
                dp.Field(key="from_email", label=_("From")),
                dp.Field(key="to_email", label=_("To")),
                dp.Field(key="last_send", label=_("Last Sent")),
                dp.Field(key="created", label=_("Created")),
                dp.Field(key="status", label=_("Latest Status")),
            ],
            legends=[EVENTTYPE_LEGENDS],
            formatting=[EVENTTYPE_FORMATTING],
        )

    def get_instance_display(self) -> Display:
        fields = [
            [repeat_field(2, "subject")],
            ["from_email", "to_email"],
            ["cc_email", "bcc_email"],
            ["created", "."],
        ]
        instance = None
        try:
            instance = self.view.get_object()
        except AssertionError:
            pass

        if instance and instance.mass_mail:
            fields.append([repeat_field(2, "mass_mail")])
        else:
            fields.append([repeat_field(2, "template")])
            fields.append([repeat_field(2, "body")])
        fields.append([repeat_field(2, "mailevent_section")])
        return create_simple_display(
            fields, [create_simple_section("mailevent_section", _("Events"), [["mailevent"]], "mailevent")]
        )


class MailStatusMassMailDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="entry", label=_("Recipient"), width=Unit.PIXEL(350)),
                dp.Field(key="address", label=_("Mail Address"), width=Unit.PIXEL(200)),
                dp.Field(key="status", label=_("Latest Status"), width=Unit.PIXEL(200)),
            ],
            legends=[EVENTTYPE_LEGENDS],
            formatting=[EVENTTYPE_FORMATTING],
        )


class MailTemplateDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(fields=[dp.Field(key="title", label=_("Title"))])

    def get_instance_display(self) -> Display:
        return create_simple_display([["title"], ["template"]])


class MailEventDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="timestamp", label=_("Date")),
                dp.Field(key="mail", label=_("Mail")) if "mail_id" not in self.view.kwargs else (),
                dp.Field(key="event_type", label=_("Type")),
                dp.Field(key="reject_reason", label=_("Rejection Reason")),
                dp.Field(key="recipient", label=_("Recipient")),
                dp.Field(key="click_url", label=_("URL")),
                dp.Field(key="ip", label=_("IP")),
                dp.Field(key="user_agent", label=_("User Agent")),
                dp.Field(key="description", label=_("Description")),
            ]
        )
