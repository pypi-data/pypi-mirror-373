from rest_framework.reverse import reverse
from wbcore.metadata.configs.endpoints import EndpointViewConfig

from wbmailing.models import Mail


class MailStatusMassMailEndpointConfig(EndpointViewConfig):
    PK_FIELD = "mail_id"

    def get_endpoint(self, **kwargs):
        return None

    def get_instance_endpoint(self, **kwargs):
        endpoint = reverse(
            "wbmailing:mail-list",
        )
        if self.instance and (mass_mail_id := self.view.kwargs.get("mass_mail_id", None)):
            obj = self.view.get_object()
            mail = Mail.objects.filter(mass_mail=mass_mail_id, to_email=obj).latest("created")
            return f"{endpoint}{mail.id}"
        return endpoint


class MailEventMailEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return None


class MailEventMassMailEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return None
