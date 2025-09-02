from django.utils.translation import gettext as _
from wbcore.metadata.configs.titles import TitleViewConfig

from wbmailing import models


class MassMailTitleConfig(TitleViewConfig):
    def get_instance_title(self):
        return _("Mass Mail: {{subject}}")

    def get_list_title(self):
        return _("Mass Mails")

    def get_create_title(self):
        return _("New Mass Mail")


class MailTitleConfig(TitleViewConfig):
    def get_instance_title(self):
        return _("Mail: {{subject}}")

    def get_list_title(self):
        return _("Mails")

    def get_create_title(self):
        return _("Write E-Mail")


class MailStatusMassMailTitleConfig(TitleViewConfig):
    def get_instance_title(self):
        return _("Mail: {{subject}}")

    def get_list_title(self):
        massmail = models.MassMail.objects.get(id=self.view.kwargs["mass_mail_id"])
        return _("Mails' Status for {}").format(massmail.subject)


class MailTemplateTitleConfig(TitleViewConfig):
    def get_instance_title(self):
        return _("Mail Template: {{title}}")

    def get_list_title(self):
        return _("Mail Templates")


class MailEventMailTitleConfig(TitleViewConfig):
    def get_list_title(self):
        mail = models.Mail.objects.get(id=self.view.kwargs["mail_id"])
        emails = ", ".join([email.address for email in mail.to_email.all()])
        return _("Event for Mail {} to {} ({})").format(mail.subject, emails, mail.created)


class MailEventMassMailTitleConfig(TitleViewConfig):
    def get_list_title(self):
        massmail = models.MassMail.objects.get(id=self.view.kwargs["mass_mail_id"])
        return _("Event for Mass Mail {}").format(str(massmail))
