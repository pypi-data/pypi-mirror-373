from typing import TYPE_CHECKING

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from django.db.models import QuerySet
from wbcore import viewsets

from wbmailing.models import Mail, MailEvent

if TYPE_CHECKING:
    from plotly.graph_objs._figure import Figure


class MailStatusBarChartViewSet(viewsets.ChartViewSet):
    IDENTIFIER = "wbmailing:mailstatus-barchart"
    queryset = MailEvent.objects.all()

    def get_queryset(self) -> QuerySet[Mail]:
        mass_mail_id = self.kwargs["mass_mail_id"]

        return super().get_queryset().filter(mail__mass_mail_id=mass_mail_id)

    def get_plotly(self, queryset: QuerySet[Mail]) -> "Figure":
        df = pd.DataFrame(queryset.values("event_type"))
        df["count"] = 1

        df = df.groupby(["event_type"])["count"].count().reset_index().sort_values(by="count")
        fig = px.bar(df, x="count", y="event_type", orientation="h")
        fig.update_layout(
            yaxis={"showticklabels": True, "title": None},
            xaxis={"title": "Number"},
            title={"text": "Mail Status", "x": 0.5},
        )
        return fig


class MailClickBarChartViewSet(viewsets.ChartViewSet):
    IDENTIFIER = "wbmailing:mailclick-barchart"
    queryset = MailEvent.objects.all()

    def get_queryset(self) -> QuerySet[MailEvent]:
        mass_mail_id = self.kwargs["mass_mail_id"]

        return super().get_queryset().filter(mail__mass_mail_id=mass_mail_id, event_type=MailEvent.EventType.CLICKED)

    def get_plotly(self, queryset: QuerySet[MailEvent]) -> "Figure":
        df = pd.DataFrame(queryset.values("click_url"))
        df["count"] = 1
        df = df.groupby(["click_url"])["count"].count().reset_index().sort_values(by="count")
        fig = go.Figure(layout=dict(template="plotly"))  # noqa THis is necessary to prevent some racing condition
        fig = px.bar(df, x="count", y="click_url", text="click_url", orientation="h")
        fig.update_layout(
            yaxis={"visible": False, "showticklabels": False},
            xaxis={"title": "Number of clicks"},
            title={"text": "Clicked URLs", "x": 0.5},
        )
        return fig


class AbstractRawDataChartViewSet(viewsets.ChartViewSet):
    queryset = MailEvent.objects.all()
    ANALYTICS_PROPERTY: str

    def get_queryset(self) -> QuerySet[MailEvent]:
        mass_mail_id = self.kwargs["mass_mail_id"]

        return super().get_queryset().filter(mail__mass_mail_id=mass_mail_id, event_type=MailEvent.EventType.OPENED)

    def get_plotly(self, queryset: QuerySet[MailEvent]) -> "Figure":
        df = pd.DataFrame(queryset.values(self.ANALYTICS_PROPERTY))
        df["count"] = 1
        df = df.groupby(self.ANALYTICS_PROPERTY)["count"].count().reset_index().sort_values(by="count")
        fig = go.Figure()
        if not df.empty:
            fig = px.bar(df, x=self.ANALYTICS_PROPERTY, y="count")
            fig.update_layout(
                xaxis={"showticklabels": True, "title": None},
                yaxis={"showticklabels": True, "title": "Number"},
            )
        return fig


class ClientsBarChartViewSet(AbstractRawDataChartViewSet):
    IDENTIFIER = "wbmailing:client-barchart"
    ANALYTICS_PROPERTY = "raw_data__Client__Name"

    def get_plotly(self, queryset: QuerySet[MailEvent]) -> "Figure":
        fig = super().get_plotly(queryset)
        fig.update_layout(title={"text": "Platforms", "x": 0.5})
        return fig


class CountryBarChartViewSet(AbstractRawDataChartViewSet):
    IDENTIFIER = "wbmailing:country-barchart"
    ANALYTICS_PROPERTY = "raw_data__Geo__Country"

    def get_plotly(self, queryset: QuerySet[MailEvent]) -> "Figure":
        fig = super().get_plotly(queryset)
        fig.update_layout(title={"text": "Countries", "x": 0.5})
        return fig


class RegionBarChartViewSet(AbstractRawDataChartViewSet):
    IDENTIFIER = "wbmailing:region-barchart"
    ANALYTICS_PROPERTY = "raw_data__Geo__Region"

    def get_plotly(self, queryset: QuerySet[MailEvent]) -> "Figure":
        fig = super().get_plotly(queryset)
        fig.update_layout(title={"text": "Regions", "x": 0.5})
        return fig
