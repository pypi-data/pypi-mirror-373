from rest_framework.reverse import reverse
from wbcore.metadata.configs.endpoints import EndpointViewConfig


class MailingListSubscriberRequestMailingListEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbmailing:mailing_list-mailinglistsubscriberchangerequest-list",
            args=[self.view.kwargs["mailing_list_id"]],
            request=self.request,
        )


class EmailContactMailingListEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return None

    def get_create_endpoint(self, **kwargs):
        return reverse(
            "wbmailing:mailing_list-mailinglistsubscriberchangerequest-list",
            args=[self.view.kwargs["mailing_list_id"]],
            request=self.request,
        )


class MailingListEntryEndpointConfig(EndpointViewConfig):
    PK_FIELD = "mailing_list"

    def get_instance_endpoint(self, **kwargs):
        return reverse(
            "wbmailing:mailinglist-list",
            args=[],
            request=self.request,
        )

    def get_delete_endpoint(self, **kwargs):
        return None

    def get_create_endpoint(self, **kwargs):
        if getattr(self.view, "primary_email", None):
            return reverse(
                "wbmailing:entry-mailinglistsubscriberchangerequest-list",
                args=[self.view.kwargs["entry_id"]],
                request=self.request,
            )
        return None


class MailMailingListChartEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbmailing:mailing_list-maileventchart-list",
            args=[self.view.kwargs["mailing_list_id"]],
            request=self.request,
        )


class MailingListSubscriberRequestEntryEndpointConfig(EndpointViewConfig):
    def get_instance_endpoint(self, **kwargs):
        if getattr(self.view, "primary_email", None):
            return super().get_instance_endpoint(**kwargs)
        return None

    def get_create_endpoint(self, **kwargs):
        return self.get_instance_endpoint(**kwargs)
