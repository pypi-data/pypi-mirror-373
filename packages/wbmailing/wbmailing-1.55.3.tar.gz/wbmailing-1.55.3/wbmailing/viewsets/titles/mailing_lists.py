from django.utils.translation import gettext as _
from wbcore.contrib.directory.models import Entry
from wbcore.metadata.configs.titles import TitleViewConfig

from wbmailing import models


class MailingListTitleConfig(TitleViewConfig):
    def get_instance_title(self):
        return _("Mailing List: {{title}}")

    def get_list_title(self):
        return _("Mailing Lists")

    def get_create_title(self):
        return _("New Mailing List")


class MailingListSubscriberChangeRequestTitleConfig(TitleViewConfig):
    def get_instance_title(self):
        return _("Mailing List Subscriber Change Request")

    def get_list_title(self):
        return _("Mailing List Subscriber Change Requests")

    def get_create_title(self):
        return _("New Mailing List Subscriber Change Request")


class EmailContactMailingListTitleConfig(TitleViewConfig):
    def get_instance_title(self):
        return _("Email Contact: {{address}}")

    def get_list_title(self):
        mailinglist = models.MailingList.objects.get(id=self.view.kwargs["mailing_list_id"])
        return _("Subscribed Emails for {}").format(mailinglist.title)


class MailMailingListChartTitleConfig(TitleViewConfig):
    def get_list_title(self):
        mailinglist = models.MailingList.objects.get(id=self.view.kwargs["mailing_list_id"])
        return _("Mail Penetration for {}").format(mailinglist.title)


class UnsubscribedEmailContactMailingListTitleConfig(EmailContactMailingListTitleConfig):
    def get_list_title(self):
        mailinglist = models.MailingList.objects.get(id=self.view.kwargs["mailing_list_id"])
        return _("Unsubscribed Emails for {}").format(mailinglist.title)


class MailingListEntryTitleConfig(MailingListTitleConfig):
    def get_list_title(self):
        entry = Entry.objects.get(id=self.view.kwargs["entry_id"])
        return _("Subscribed Mailing Lists of {}").format(entry.computed_str)


class MailingListSubscriberRequestEntryTitleConfig(MailingListSubscriberChangeRequestTitleConfig):
    def get_list_title(self):
        entry = Entry.objects.get(id=self.view.kwargs["entry_id"])
        return _("Mailing Subscription Requests for {}").format(entry.computed_str)

    def get_create_title(self):
        entry = Entry.objects.get(id=self.view.kwargs["entry_id"])
        return _("New Mailing Subscription Request for {}").format(entry.computed_str)
