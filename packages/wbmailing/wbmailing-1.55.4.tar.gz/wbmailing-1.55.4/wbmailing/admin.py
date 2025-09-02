from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import (
    Mail,
    MailEvent,
    MailingList,
    MailingListEmailContactThroughModel,
    MailingListSubscriberChangeRequest,
    MailTemplate,
    MassMail,
)


class MailingListEmailContactThroughInlineAdmin(admin.TabularInline):
    model = MailingListEmailContactThroughModel
    fk_name = "mailing_list"
    autocomplete_fields = ["email_contact"]


@admin.register(MailingList)
class MailingListAdmin(admin.ModelAdmin):
    autocomplete_fields = ["email_contacts"]
    search_fields = ["title"]
    inlines = [
        MailingListEmailContactThroughInlineAdmin,
    ]


@admin.register(MassMail)
class MassMailAdmin(admin.ModelAdmin):
    autocomplete_fields = ["creator"]

    def send_test_mail(self, request, queryset):
        for mass_mail in queryset:
            mass_mail.send_test_mail(request.user)

    actions = [send_test_mail]


@admin.register(MailingListSubscriberChangeRequest)
class MailingListSubscriberChangeRequestAdmin(admin.ModelAdmin):
    list_display = ("email_contact", "mailing_list", "status")
    autocomplete_fields = ["email_contact", "requester"]


admin.site.register(MailEvent)


class MailEventInline(admin.TabularInline):
    model = MailEvent
    fields = ("timestamp", "event_type", "reject_reason", "recipient", "user_agent", "tags", "description")
    readonly_fields = ("timestamp", "event_type", "reject_reason", "recipient", "user_agent", "tags", "description")
    extra = 0
    can_delete = False


@admin.register(Mail)
class MailAdmin(admin.ModelAdmin):
    def send_mails(self, request, queryset):
        for mail in queryset:
            mail.resend()

    send_mails.short_description = _("Send Emails")
    actions = [send_mails]
    search_fields = ["mass_mail__subject", "from_email", "to_email__address", "subject", "message_ids"]
    autocomplete_fields = ["to_email", "cc_email", "bcc_email"]

    inlines = [MailEventInline]


@admin.register(MailTemplate)
class MailTemplateAdmin(admin.ModelAdmin):
    pass
