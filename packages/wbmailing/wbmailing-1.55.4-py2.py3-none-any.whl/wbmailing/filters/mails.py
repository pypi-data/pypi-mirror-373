from django.apps import apps
from django.utils.translation import gettext_lazy as _
from wbcore import filters as wb_filters

from wbmailing import models


class MassMailFilterSet(wb_filters.FilterSet):
    is_factsheet_massmail = wb_filters.BooleanFilter(
        label=_("Is Factsheet Mass Mail"), method="boolean_is_factsheet_massmail", initial=False
    )

    def boolean_is_factsheet_massmail(self, queryset, name, value):
        if apps.is_installed("wbreport"):
            if value is True:
                return queryset.filter(mailing_lists__reports__isnull=False).distinct()
            elif value is False:
                return queryset.filter(mailing_lists__reports__isnull=True).distinct()
        return queryset

    class Meta:
        model = models.MassMail
        fields = {
            "subject": ["exact", "icontains"],
            "from_email": ["exact", "icontains"],
            "template": ["exact"],
            "mailing_lists": ["exact"],
            "created": ["gte", "exact", "lte"],
            "creator": ["exact"],
            "status": ["exact"],
        }


class MailFilter(wb_filters.FilterSet):
    never_open = wb_filters.BooleanFilter(label=_("Never Opened"), method="boolean_never_open")

    event_type = wb_filters.MultipleChoiceFilter(
        label=_("Events"), method="filter_events", choices=models.MailEvent.EventType.choices
    )
    rejected_reason = wb_filters.MultipleChoiceFilter(
        label=_("Rejection Reasons"), method="filter_rejected_reason", choices=models.MailEvent.RejectReason.choices
    )
    is_massmail_mail = wb_filters.BooleanFilter(label=_("Mass Mail"), method="boolean_is_massmail")
    status = wb_filters.ChoiceFilter(label=_("Status"), choices=models.MailEvent.EventType.choices)

    class Meta:
        model = models.Mail
        fields = {
            "mass_mail": ["exact"],
            "from_email": ["exact"],
            "to_email": ["exact"],
            "created": ["gte", "exact", "lte"],
        }

    def boolean_is_massmail(self, queryset, name, value):
        if value is True:
            return queryset.filter(mass_mail__isnull=False)
        elif value is False:
            return queryset.filter(mass_mail__isnull=True)
        return queryset

    def boolean_never_open(self, queryset, name, value):
        if value:
            return queryset.exclude(events__event_type=models.MailEvent.EventType.OPENED)
        return queryset

    def filter_events(self, queryset, name, value):
        if value:
            return queryset.filter(events__event_type=value)
        return queryset

    def filter_rejected_reason(self, queryset, name, value):
        if value:
            return queryset.filter(events__reject_reason=value)
        return queryset
