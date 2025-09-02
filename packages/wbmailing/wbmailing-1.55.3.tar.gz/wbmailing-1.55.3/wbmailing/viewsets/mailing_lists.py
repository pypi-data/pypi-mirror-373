from django.contrib.messages import warning
from django.contrib.postgres.aggregates import StringAgg
from django.db.models import Count, Exists, F, OuterRef, Q, Subquery
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic import View
from rest_framework.decorators import action
from rest_framework.response import Response
from wbcore import serializers as wb_serializers
from wbcore import viewsets
from wbcore.contrib.directory.models import Company, EmailContact, Entry

from wbmailing import models, serializers
from wbmailing.filters import (
    EmailContactMailingListFilterSet,
    MailingListEmailContactThroughModelModelFilterSet,
    MailingListFilterSet,
)
from wbmailing.models import (
    MailingListEmailContactThroughModel,
    MailingListSubscriberChangeRequest,
)
from wbmailing.viewsets.buttons import (
    MailingListButtonConfig,
    MailingListEmailContactThroughModelButtonConfig,
    MailingListSubcriptionRequestButtonConfig,
)
from wbmailing.viewsets.display import (
    EmailContactMailingListDisplayConfig,
    MailingListDisplayConfig,
    MailingListEntryDisplayConfig,
    MailingListSubscriberChangeRequestDisplayConfig,
    MailingListSubscriberRequestEntryDisplayConfig,
    MailingListSubscriberRequestMailingListDisplayConfig,
)
from wbmailing.viewsets.endpoints import (
    EmailContactMailingListEndpointConfig,
    MailingListEntryEndpointConfig,
    MailingListSubscriberRequestEntryEndpointConfig,
    MailingListSubscriberRequestMailingListEndpointConfig,
)
from wbmailing.viewsets.titles import (
    EmailContactMailingListTitleConfig,
    MailingListEntryTitleConfig,
    MailingListSubscriberChangeRequestTitleConfig,
    MailingListSubscriberRequestEntryTitleConfig,
    MailingListTitleConfig,
)


class MailingListRepresentationViewSet(viewsets.RepresentationViewSet):
    IDENTIFIER = "wbmailing:mailinglist"

    ordering_fields = ("title",)
    search_fields = ("title",)
    queryset = models.MailingList.objects.all()
    serializer_class = serializers.MailingListRepresentationSerializer
    filterset_class = MailingListFilterSet


class MailingListModelViewSet(viewsets.ModelViewSet):
    IDENTIFIER = "wbmailing:mailinglist"

    queryset = models.MailingList.objects.all()

    def get_serializer_class(self):
        if getattr(self, "action", None) == "list":
            return serializers.MailingListListSerializer
        return serializers.MailingListModelSerializer

    filterset_class = MailingListFilterSet

    ordering_fields = ordering = ("title",)
    search_fields = ("title",)

    display_config_class = MailingListDisplayConfig
    title_config_class = MailingListTitleConfig
    button_config_class = MailingListButtonConfig

    def get_queryset(self):
        qs = self.filter_queryset(
            models.MailingList.objects.annotate(
                nb_subscribers=Coalesce(
                    Subquery(
                        MailingListEmailContactThroughModel.objects.filter(
                            mailing_list=OuterRef("pk"), status=MailingListEmailContactThroughModel.Status.SUBSCRIBED
                        )
                        .values("mailing_list")
                        .annotate(c=Count("mailing_list"))
                        .values("c")[:1]
                    ),
                    0,
                )
            )
        )
        qs = qs.prefetch_related("email_contacts")
        return qs


class MailingListSubscriberChangeRequestModelViewSet(viewsets.ModelViewSet):
    queryset = (
        models.MailingListSubscriberChangeRequest.objects.select_related("email_contact")
        .select_related("mailing_list")
        .select_related("requester")
        .select_related("approver")
    ).annotate(entry_repr=F("email_contact__entry__computed_str"))

    serializer_class = serializers.MailingListSubscriberChangeRequestModelSerializer

    search_fields = ("email_contact__address", "mailing_list__title")
    ordering_fields = ("email_contact__address", "mailing_list__title", "created")
    ordering = ("-created",)
    filterset_fields = {
        "email_contact": ["exact"],
        "mailing_list": ["exact"],
        "requester": ["exact"],
        "created": ["gte", "exact", "lte"],
        "status": ["exact"],
    }

    display_config_class = MailingListSubscriberChangeRequestDisplayConfig
    title_config_class = MailingListSubscriberChangeRequestTitleConfig
    button_config_class = MailingListSubcriptionRequestButtonConfig

    def add_messages(self, request, instance=None, **kwargs):
        if instance:
            _type = (
                "subscribed"
                if instance.type == MailingListSubscriberChangeRequest.Type.SUBSCRIBING
                else "unsubscribed"
            )
            warning(
                request,
                f"Upon approval, This change request will {_type} {instance.email_contact.address} to {instance.mailing_list.title}",
            )

    @action(detail=False, methods=["GET"])
    def approveall(self, request, pk=None):
        for request in models.MailingListSubscriberChangeRequest.objects.filter(
            status=models.MailingListSubscriberChangeRequest.Status.PENDING
        ).all():
            request.approve()
            request.save()
        return Response({"send": True})


class MailingListSubscriberRequestMailingListModelViewSet(MailingListSubscriberChangeRequestModelViewSet):
    IDENTIFIER = "wbmailing:mailing_list-mailinglistsubscriberchangerequest"

    display_config_class = MailingListSubscriberRequestMailingListDisplayConfig
    endpoint_config_class = MailingListSubscriberRequestMailingListEndpointConfig

    def get_queryset(self):
        return super().get_queryset().filter(mailing_list__id=self.kwargs["mailing_list_id"])


class MailingListEmailContactThroughModelModelViewSet(viewsets.ModelViewSet):
    queryset = MailingListEmailContactThroughModel.objects.select_related(
        "email_contact",
        "mailing_list",
    )
    search_fields = ["email_contact__address", "email_contact__entry__computed_str"]
    button_config_class = MailingListEmailContactThroughModelButtonConfig
    serializer_class = serializers.MailingListEmailContactThroughModelModelSerializer

    ordering = ["email_contact__address", "mailing_list__title"]
    ordering_fields = ["email_contact__address", "status", "mailing_list__title"]

    filterset_class = MailingListEmailContactThroughModelModelFilterSet

    @action(detail=True, methods=["GET", "PATCH"])
    def removeexpirationdate(self, request, mailing_list_id=None, pk=None, **kwargs):
        through = get_object_or_404(MailingListEmailContactThroughModel, id=pk)
        if (qs := through.requests.filter(expiration_date__isnull=False)).exists():
            last_request = qs.latest("created")
            last_request.expiration_date = None
            last_request.save()
        return Response({"send": True})

    @action(detail=True, methods=["GET", "PATCH"])
    def delete(self, request, mailing_list_id=None, pk=None, **kwargs):
        through = get_object_or_404(MailingListEmailContactThroughModel, id=pk)
        through.delete()
        return Response({"send": True})

    @action(detail=True, methods=["GET", "PATCH"])
    def unsubscribe(self, request, pk=None, **kwargs):
        through = get_object_or_404(MailingListEmailContactThroughModel, id=pk)
        if through.status == MailingListEmailContactThroughModel.Status.SUBSCRIBED:
            through.change_state(
                reason=_("Unsubscribed by {}").format(str(request.user)),
                requester=request.user.profile,
                approver=request.user.profile,
                automatically_approve=True,
            )
        return Response({"send": True})

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(
                expiration_date=MailingListEmailContactThroughModel.get_expired_date_subquery(),
                in_charge=StringAgg(F("email_contact__entry__relationship_managers__computed_str"), delimiter=", "),
                is_pending_request_change=Exists(
                    MailingListSubscriberChangeRequest.objects.filter(
                        relationship=OuterRef("pk"), status=MailingListSubscriberChangeRequest.Status.PENDING
                    )
                ),
                is_public=F("mailing_list__is_public"),
            )
        )


class EmailContactMailingListModelViewSet(MailingListEmailContactThroughModelModelViewSet):
    filterset_class = EmailContactMailingListFilterSet

    display_config_class = EmailContactMailingListDisplayConfig
    title_config_class = EmailContactMailingListTitleConfig
    endpoint_config_class = EmailContactMailingListEndpointConfig

    def get_queryset(self):
        return super().get_queryset().filter(mailing_list=self.kwargs["mailing_list_id"])


class MailingListEntryModelViewSet(MailingListEmailContactThroughModelModelViewSet):
    filterset_fields = {"mailing_list": ["exact"], "status": ["exact"]}

    display_config_class = MailingListEntryDisplayConfig
    title_config_class = MailingListEntryTitleConfig
    endpoint_config_class = MailingListEntryEndpointConfig

    @cached_property
    def casted_entry(self):
        return get_object_or_404(Entry, id=self.kwargs["entry_id"]).get_casted_entry()

    @cached_property
    def primary_email(self):
        return EmailContact.objects.filter(entry=self.kwargs["entry_id"], primary=True).first()

    def add_messages(self, request, instance=None, **kwargs):
        if not self.primary_email:
            warning(
                request,
                "This person does not have a primary email. Adds one first before adding them to a mailing list.",
            )

    def get_queryset(self):
        qs = super().get_queryset()
        entry = self.casted_entry
        if isinstance(entry, Company):
            email_contacts = EmailContact.objects.filter(
                Q(entry=entry) | Q(entry__in=entry.employees.all())
            ).distinct()
            qs = qs.filter(email_contact__in=email_contacts)
        else:
            qs = qs.filter(email_contact__entry=entry)
        return qs


class MailingListSubscriberRequestEntryModelViewSet(MailingListSubscriberChangeRequestModelViewSet):
    IDENTIFIER = "wbmailing:entry-mailinglistsubscriberchangerequest"
    display_config_class = MailingListSubscriberRequestEntryDisplayConfig
    title_config_class = MailingListSubscriberRequestEntryTitleConfig
    endpoint_config_class = MailingListSubscriberRequestEntryEndpointConfig

    @cached_property
    def primary_email(self) -> EmailContact | None:
        try:
            return EmailContact.objects.filter(entry=self.kwargs["entry_id"], primary=True).first()
        except KeyError:
            return None

    def get_serializer_class(self):
        if self.primary_email:

            class Serializer(serializers.MailingListSubscriberChangeRequestModelSerializer):
                email_contact = wb_serializers.PrimaryKeyRelatedField(
                    queryset=EmailContact.objects.filter(entry=self.kwargs["entry_id"]),
                    label=_("Email"),
                    many=False,
                    default=self.primary_email,
                )

        else:

            class Serializer(serializers.MailingListSubscriberChangeRequestModelSerializer):
                email_contact = wb_serializers.PrimaryKeyRelatedField(label=_("No Emails"), read_only=True)

        return Serializer

    def get_queryset(self):
        return super().get_queryset().filter(email_contact__entry__id=self.kwargs["entry_id"])


#################
# TODO Old system
#################


class ManageMailingListSubscriptions(View):
    def get(self, request, email_contact_id, *args, **kwargs):
        email_contact = get_object_or_404(EmailContact, id=email_contact_id)
        context = {
            "title": _("Manage Mailing List Subscriptions"),
            "email_contact": email_contact,
            "mailing_lists": models.MailingList.get_subscribed_mailing_lists(email_contact),
        }
        return render(request, "mailing/manage_mailing_list_subscriptions.html", context=context)


class UnsubscribeView(View):
    def get(self, request, email_contact_id, mailing_list_id, *args, **kwargs):
        email_contact = get_object_or_404(EmailContact, id=email_contact_id)
        mailing_list = get_object_or_404(models.MailingList, id=mailing_list_id)
        mailing_list.unsubscribe(
            email_contact, reason=_("The user requested to be unsubscribed."), automatically_approve=True
        )
        return redirect(
            "wbmailing:manage_mailing_list_subscriptions",
            email_contact_id=email_contact_id,
        )
