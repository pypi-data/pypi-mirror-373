from django.apps import apps
from django.db.models import Exists, OuterRef
from django.utils.translation import gettext_lazy as _
from wbcore import filters as wb_filters
from wbcore.contrib.directory.models import EmailContact, Entry

from wbmailing import models


class MailingListFilterSet(wb_filters.FilterSet):
    not_factsheet_mailinglist = wb_filters.BooleanFilter(
        label=_("No Factsheet Mailing Lists"), method="boolean_not_factsheet_mailinglist", initial=True
    )
    negative_entry = wb_filters.ModelChoiceFilter(
        label=_("Unsubscribed mailing lists for user"),
        queryset=Entry.objects.all(),
        endpoint=Entry.get_representation_endpoint(),
        value_key=Entry.get_representation_value_key(),
        label_key=Entry.get_representation_label_key(),
        method="get_notsubscribed_mailing_list_for_entry",
    )

    def get_notsubscribed_mailing_list_for_entry(self, queryset, name, value):
        if value:
            already_subscribed_subquery = models.MailingListEmailContactThroughModel.objects.filter(
                mailing_list=OuterRef("pk"),
                email_contact__in=value.emails.all(),
                status__in=[models.MailingListEmailContactThroughModel.Status.SUBSCRIBED],
            )
            return queryset.annotate(already_subscribed_subquery=Exists(already_subscribed_subquery)).filter(
                already_subscribed_subquery=False
            )

        return queryset

    def boolean_not_factsheet_mailinglist(self, queryset, name, value):
        if apps.is_installed("wbreport"):
            if value is False:
                return queryset.filter(reports__isnull=False).distinct()
            elif value is True:
                return queryset.filter(reports__isnull=True).distinct()
        return queryset

    class Meta:
        model = models.MailingList
        fields = {"email_contacts": ["exact"], "is_public": ["exact"]}


class MailingListSubscriberChangeRequestFilterSet(wb_filters.FilterSet):
    class Meta:
        model = models.MailingListSubscriberChangeRequest
        fields = {
            "email_contact": ["exact"],
            "mailing_list": ["exact"],
            "requester": ["exact"],
            "created": ["gte", "exact", "lte"],
        }


class MailStatusMassMailFilterSet(wb_filters.FilterSet):
    status = wb_filters.ChoiceFilter(label=_("Status"), choices=models.MailEvent.EventType.choices)

    class Meta:
        model = EmailContact
        fields = {"entry": ["exact"]}


class MailingListEmailContactThroughModelModelFilterSet(wb_filters.FilterSet):
    expiration_date = wb_filters.DateTimeRangeFilter(
        label=_("Expiration Date"),
        method=wb_filters.DateRangeFilter.base_date_range_filter_method,
    )
    is_pending_request_change = wb_filters.BooleanFilter(
        label=_("Pending Change"), lookup_expr="exact", field_name="is_pending_request_change"
    )

    class Meta:
        model = models.MailingListEmailContactThroughModel
        fields = {"status": ["exact"]}


class EmailContactMailingListFilterSet(MailingListEmailContactThroughModelModelFilterSet):
    class Meta:
        model = models.MailingListEmailContactThroughModel
        fields = {"email_contact": ["exact"], "status": ["exact"]}
