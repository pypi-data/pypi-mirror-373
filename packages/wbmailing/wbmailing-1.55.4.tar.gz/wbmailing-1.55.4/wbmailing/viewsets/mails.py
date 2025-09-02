import pandas as pd
import plotly.graph_objects as go
from django.contrib.messages import info
from django.db.models import CharField, Count, OuterRef, Q, Subquery, Value
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django.utils.translation import gettext
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from wbcore import viewsets
from wbcore.contrib.directory.models import EmailContact
from wbcore.filters import DjangoFilterBackend
from wbcore.utils.strings import format_number

from wbmailing import models, serializers
from wbmailing.filters import MailFilter, MailStatusMassMailFilterSet, MassMailFilterSet
from wbmailing.models import MailEvent
from wbmailing.viewsets.buttons import (
    MailButtonConfig,
    MailStatusMassMailButtonConfig,
    MassMailButtonConfig,
)
from wbmailing.viewsets.display import (
    MailDisplayConfig,
    MailEventDisplayConfig,
    MailStatusMassMailDisplayConfig,
    MailTemplateDisplayConfig,
    MassMailDisplayConfig,
)
from wbmailing.viewsets.endpoints import (
    MailEventMailEndpointConfig,
    MailEventMassMailEndpointConfig,
    MailMailingListChartEndpointConfig,
    MailStatusMassMailEndpointConfig,
)
from wbmailing.viewsets.titles import (
    MailEventMailTitleConfig,
    MailEventMassMailTitleConfig,
    MailMailingListChartTitleConfig,
    MailStatusMassMailTitleConfig,
    MailTemplateTitleConfig,
    MailTitleConfig,
    MassMailTitleConfig,
)


class MailTemplateRepresentationViewSet(viewsets.RepresentationViewSet):
    IDENTIFIER = "wbmailing:mailtemplate"

    filter_backends = (
        filters.OrderingFilter,
        filters.SearchFilter,
    )
    ordering_fields = ordering = ("title",)
    search_fields = ("title",)

    queryset = models.MailTemplate.objects.all()
    serializer_class = serializers.MailTemplateRepresentationSerializer


class MailRepresentationViewSet(viewsets.RepresentationViewSet):
    IDENTIFIER = "wbmailing:mail"
    queryset = models.Mail.objects.all()
    serializer_class = serializers.MailRepresentationSerializer


class MassMailRepresentationViewSet(viewsets.RepresentationViewSet):
    IDENTIFIER = "wbmailing:massmail"

    filter_backends = (
        filters.OrderingFilter,
        filters.SearchFilter,
    )
    ordering_fields = ("subject",)
    search_fields = ("subject",)
    queryset = models.MassMail.objects.all()
    serializer_class = serializers.MassMailRepresentationSerializer


class MailMailingListChartViewSet(viewsets.ChartViewSet):
    IDENTIFIER = "mailing:maileventchart"

    queryset = models.Mail.objects.all()

    title_config_class = MailMailingListChartTitleConfig
    endpoint_config_class = MailMailingListChartEndpointConfig

    def get_plotly(self, queryset):
        mass_mail_name_map = dict(models.MassMail.objects.values_list("id", "subject"))
        fig = go.Figure()
        if queryset.exists():
            df = pd.DataFrame(queryset.values("mass_mail", "CLICKED", "DELIVERED", "OPENED"))
            df["TOTAL"] = 1
            df = df.groupby("mass_mail").sum()
            total = df["TOTAL"]
            del df["TOTAL"]
            df["FAILED"] = total - df["DELIVERED"]
            df.index.name = None
            df = df.divide(total.values, axis=0)
            df["title"] = df.index
            df.title = df.title.map(mass_mail_name_map)
            df.index = range(df.shape[0])
            for col in df.columns:
                if col != "title":
                    fig.add_trace(
                        go.Scatter(
                            x=df.index,
                            y=df[col],
                            mode="lines",
                            name=str(models.MailEvent.EventType[col].label),
                            marker_color=models.MailEvent.EventType.get_color(col),
                        )
                    )
            fig.update_layout(
                xaxis=dict(tickmode="array", tickvals=df.index, ticktext=df.title), yaxis=dict(tickformat=".1%")
            )
        return fig

    def get_queryset(self):
        return models.Mail.objects.filter(
            mass_mail__isnull=False, mass_mail__mailing_lists=self.kwargs["mailing_list_id"]
        ).annotate(
            CLICKED=Coalesce(
                Subquery(
                    MailEvent.objects.filter(mail=OuterRef("pk"), event_type=MailEvent.EventType.CLICKED)
                    .annotate(c=Count("event_type"))
                    .values("c")[:1]
                ),
                0,
            ),
            OPENED=Coalesce(
                Subquery(
                    MailEvent.objects.filter(mail=OuterRef("pk"), event_type=MailEvent.EventType.OPENED)
                    .annotate(c=Count("event_type"))
                    .values("c")[:1]
                ),
                0,
            ),
            DELIVERED=Coalesce(
                Subquery(
                    MailEvent.objects.filter(mail=OuterRef("pk"), event_type=MailEvent.EventType.DELIVERED)
                    .annotate(c=Count("event_type"))
                    .values("c")[:1]
                ),
                0,
            ),
        )


class MassMailModelViewSet(viewsets.ModelViewSet):
    queryset = models.MassMail.objects.select_related("creator", "template").prefetch_related(
        "mailing_lists",
        "excluded_mailing_lists",
    )

    filterset_class = MassMailFilterSet
    ordering_fields = (
        "created",
        "subject",
        "from_email",
        "template__title",
        "creator__computed_str",
        "sent",
        "opened",
    )
    ordering = ("-created",)
    search_fields = ("subject",)

    display_config_class = MassMailDisplayConfig
    title_config_class = MassMailTitleConfig
    button_config_class = MassMailButtonConfig

    def get_serializer_class(self):
        if getattr(self, "action", None) == "list":
            return serializers.MassMailListSerializer
        return serializers.MassMailModelSerializer

    @action(methods=["GET", "PATCH"], detail=True)
    def sendtestmail(self, request, pk=None):
        mass_mail = self.get_object()
        email = request.POST.get("to_test_email", request.user.email)

        mass_mail.send_test_mail(email)

        return Response({"__notification": {"title": gettext("Mail sent.")}}, status=status.HTTP_200_OK)


class MailModelViewSet(viewsets.ModelViewSet):
    queryset = models.Mail.objects.select_related(
        "mass_mail",
        "template",
    ).prefetch_related(
        "to_email",
        "cc_email",
        "bcc_email",
    )
    serializer_class = serializers.MailModelSerializer
    filterset_class = MailFilter

    ordering_fields = ("created", "subject", "mass_mail__subject", "from_email", "last_send")
    ordering = "-last_send"
    search_fields = ("subject", "from_email", "mass_mail__subject", "to_email__address")

    display_config_class = MailDisplayConfig
    title_config_class = MailTitleConfig
    button_config_class = MailButtonConfig

    def get_queryset(self):
        user = self.request.user
        emails = user.profile.emails.values("address")
        qs = super().get_queryset()
        if not user.has_perm("wbmailing:view_all_mails") and not user.is_superuser:
            qs = qs.annotate(
                is_in_charge_to_email=Coalesce(
                    Subquery(
                        EmailContact.objects.filter(mail_to=OuterRef("pk"))
                        .filter(Q(entry__relationship_managers=user.profile) | Q(address__in=emails))
                        .values("mail_to")
                        .annotate(number_of_charges=Count("*"))
                        .values("number_of_charges")[:1]
                    ),
                    0,
                ),
                is_in_charge_cc_email=Coalesce(
                    Subquery(
                        EmailContact.objects.filter(mail_cc=OuterRef("pk"))
                        .filter(Q(entry__relationship_managers=user.profile) | Q(address__in=emails))
                        .values("mail_cc")
                        .annotate(number_of_charges=Count("*"))
                        .values("number_of_charges")[:1]
                    ),
                    0,
                ),
                is_in_charge_bcc_email=Coalesce(
                    Subquery(
                        EmailContact.objects.filter(mail_bcc=OuterRef("pk"))
                        .filter(Q(entry__relationship_managers=user.profile) | Q(address__in=emails))
                        .values("mail_bcc")
                        .annotate(number_of_charges=Count("*"))
                        .values("number_of_charges")[:1]
                    ),
                    0,
                ),
            ).filter(
                Q(is_in_charge_to_email__gt=0)
                | Q(is_in_charge_cc_email__gt=0)
                | Q(is_in_charge_bcc_email__gt=0)
                | Q(mass_mail__isnull=False)
            )
        return self.annotate(qs)

    @action(methods=["GET", "PATCH"], detail=True)
    def resend(self, request, pk=None):
        mail = self.get_object()
        mail.resend()
        return Response({"__notification": {"title": gettext("Mail sent.")}}, status=status.HTTP_200_OK)

    @classmethod
    def annotate(cls, qs):
        return qs.annotate(
            status=Coalesce(
                Subquery(
                    models.MailEvent.objects.filter(mail=OuterRef("pk"))
                    .order_by("-timestamp")
                    .values("event_type")[:1]
                ),
                None,
            )
        )


class MailStatusMassMailModelViewSet(viewsets.ModelViewSet):
    IDENTIFIER = "wbmailing:massmail"

    queryset = EmailContact.objects.select_related("entry")
    serializer_class = serializers.MailStatusMassMailModelSerializer
    filterset_class = MailStatusMassMailFilterSet

    ordering_fields = ("address", "entry__computed_str")
    ordering = ("address",)
    search_fields = ("address", "entry__computed_str")

    display_config_class = MailStatusMassMailDisplayConfig
    title_config_class = MailStatusMassMailTitleConfig
    endpoint_config_class = MailStatusMassMailEndpointConfig
    button_config_class = MailStatusMassMailButtonConfig

    def add_messages(
        self,
        request,
        queryset=None,
        paginated_queryset=None,
        instance=None,
        initial=False,
    ):
        df = pd.DataFrame(
            MailEvent.objects.filter(mail__mass_mail=self.kwargs["mass_mail_id"]).values(
                "event_type",
                "recipient",
                "timestamp",
            ),
            columns=["event_type", "recipient", "timestamp"],
        )
        df = df.sort_values(by="timestamp", ascending=False).groupby("recipient").first().reset_index()
        total_mails = df.shape[0]
        if not df.empty and total_mails:
            nb_created = df[df["event_type"] == MailEvent.EventType.CREATED.value].shape[0]
            nb_queued = df[df["event_type"] == MailEvent.EventType.QUEUED.value].shape[0]
            nb_opened = df[df["event_type"] == MailEvent.EventType.OPENED.value].shape[0]
            nb_clicked = df[df["event_type"] == MailEvent.EventType.CLICKED.value].shape[0]
            nb_delivered = df[df["event_type"] == MailEvent.EventType.DELIVERED.value].shape[0]
            nb_received = nb_opened + nb_delivered + nb_clicked
            msg = f"""
            <p> Total Sent: {total_mails}</p>
            <p> Total Received: {format_number(nb_received / total_mails):.2%}</p>
            <ul>
                <li> Only Created: {format_number(nb_created / total_mails):.2%} </li>
                <li> Only Queued: {format_number(nb_queued / total_mails):.2%} </li>
                <li> Delivered: {format_number(nb_delivered / total_mails):.2%} </li>
                <li> Opened: {format_number(nb_opened / total_mails):.2%} </li>
                <li> Clicked: {format_number(nb_clicked / total_mails):.2%} </li>
                <li> Not Received: {format_number(1 - nb_received / total_mails):.2%} </li>
            </ul>
            """
            info(request, msg, extra_tags="auto_close=0")

    @cached_property
    def mass_mail(self):
        return get_object_or_404(models.MassMail, id=self.kwargs["mass_mail_id"])

    @cached_property
    def included_mailing_list_ids(self):
        return self.mass_mail.mailing_lists.values_list("id")

    @cached_property
    def excluded_mailing_list_ids(self):
        return self.mass_mail.excluded_mailing_lists.values_list("id")

    def get_queryset(self):
        mass_mail = self.mass_mail
        return (
            models.MassMail.get_emails(self.included_mailing_list_ids, self.excluded_mailing_list_ids)
            .annotate(
                mail_id=Subquery(
                    models.Mail.objects.filter(mass_mail=mass_mail, to_email__id=OuterRef("id"))
                    .order_by("-created")
                    .values("id")[:1],
                    output_field=CharField(),
                ),
                status=Coalesce(
                    Subquery(
                        models.MailEvent.objects.filter(recipient=OuterRef("address"), mail__mass_mail=mass_mail)
                        .order_by("-timestamp")
                        .values("event_type")[:1]
                    ),
                    Value("NOT_SENT"),
                ),
            )
            .select_related("entry")
        )

    @action(methods=["PATCH"], detail=False)
    def resendbouncedmails(self, request, mass_mail_id=None):
        mass_mail = models.MassMail.objects.get(id=mass_mail_id)
        unsent_emails = MailModelViewSet.annotate(mass_mail.mails.all()).filter(
            status__in=[
                models.MailEvent.EventType.BOUNCED,
                models.MailEvent.EventType.REJECTED,
                models.MailEvent.EventType.DEFERRED,
                models.MailEvent.EventType.UNKNOWN,
            ]
        )
        for mail in unsent_emails.all():
            mail.resend()
        return Response(
            {"__notification": {"title": gettext("Unsent emails resent with success")}}, status=status.HTTP_200_OK
        )


class MailTemplateModelViewSet(viewsets.ModelViewSet):
    IDENTIFIER = "wbmailing:mailtemplate"

    queryset = models.MailTemplate.objects.all()
    serializer_class = serializers.MailTemplateModelSerializer

    display_config_class = MailTemplateDisplayConfig
    title_config_class = MailTemplateTitleConfig


class MailEventModelViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.MailEventModelSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    queryset = MailEvent.objects.select_related("mail")

    filterset_fields = {
        "timestamp": ["gte", "exact", "lte"],
        "event_type": ["exact"],
        "reject_reason": ["exact"],
        "recipient": ["exact"],
        "click_url": ["exact", "icontains"],
        "description": ["exact", "icontains"],
    }

    ordering_fields = ("timestamp",)
    ordering = ("-timestamp",)
    search_fields = ("description",)

    display_config_class = MailEventDisplayConfig


class MailEventMailModelViewSet(MailEventModelViewSet):
    endpoint_config_class = MailEventMailEndpointConfig
    title_config_class = MailEventMailTitleConfig

    def get_queryset(self):
        return models.MailEvent.objects.filter(mail_id=self.kwargs["mail_id"])


class MailEventMassMailMailModelViewSet(MailEventModelViewSet):
    title_config_class = MailEventMassMailTitleConfig
    endpoint_config_class = MailEventMassMailEndpointConfig

    def get_queryset(self):
        return models.MailEvent.objects.filter(mail__mass_mail=self.kwargs["mass_mail_id"])
