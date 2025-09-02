from typing import Type

import pandas as pd
import plotly.graph_objects as go
from django.db.models.expressions import F
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from rest_framework import filters
from wbcore import viewsets
from wbcore.filters import DjangoFilterBackend
from wbcore.pandas import fields as pf
from wbcore.pandas.views import PandasAPIViewSet
from wbcore.serializers.serializers import ModelSerializer
from wbcore.utils.strings import format_number

from wbhuman_resources.filters import (
    KPIEvaluationFilterSet,
    KPIEvaluationPandasFilter,
    KPIFilterSet,
)
from wbhuman_resources.models import KPI, Evaluation
from wbhuman_resources.serializers import (
    EvaluationModelSerializer,
    EvaluationRepresentationSerializer,
    KPIModelSerializer,
    KPIRepresentationSerializer,
)
from wbhuman_resources.viewsets.buttons import KPIButtonConfig
from wbhuman_resources.viewsets.display import (
    KPIDisplayConfig,
    KPIEvaluationDisplayConfig,
    KPIEvaluationPandasDisplayConfig,
)
from wbhuman_resources.viewsets.endpoints import (
    EvaluationGraphEndpointConfig,
    KPIEndpointConfig,
    KPIEvaluationEndpointConfig,
    KPIEvaluationPandasEndpointConfig,
)
from wbhuman_resources.viewsets.titles import (
    EvaluationGraphTitleConfig,
    KPIEvaluationPandasTitleConfig,
)


class KPIRepresentationViewSet(viewsets.RepresentationViewSet):
    queryset = KPI.objects.all()
    serializer_class = KPIRepresentationSerializer


class KPIModelViewSet(viewsets.ModelViewSet):
    queryset = KPI.objects.all()
    serializer_class = KPIModelSerializer
    display_config_class = KPIDisplayConfig
    endpoint_config_class = KPIEndpointConfig
    button_config_class = KPIButtonConfig
    filter_backends = (
        filters.SearchFilter,
        filters.OrderingFilter,
        DjangoFilterBackend,
    )
    filterset_class = KPIFilterSet
    ordering = ["last_update", "period"]
    ordering_fields = ["name", "evaluated_persons", "parameters", "period"]
    search_fields = ["name", "evaluated_persons__computed_str"]

    def get_serializer_class(self) -> Type[ModelSerializer]:
        if pk := self.kwargs.get("pk", None):
            kpi = get_object_or_404(KPI, pk=pk)
            handler = kpi.get_handler()
            return handler.get_serializer()
        return super().get_serializer_class()

    def get_queryset(self) -> QuerySet[KPI]:
        queryset = super().get_queryset()
        if pk := self.kwargs.get("pk", None):
            kpi = get_object_or_404(KPI, pk=pk)
            handler = kpi.get_handler()
            queryset = handler.annotate_parameters(queryset)
        queryset = queryset.annotate(
            parameters=F("additional_data__list_data"),
        )
        if KPI.is_administrator(self.request.user):
            return queryset
        return queryset.filter(evaluated_persons=self.request.user.profile)


class EvaluationRepresentationViewSet(viewsets.RepresentationViewSet):
    queryset = Evaluation.objects.all()
    serializer_class = EvaluationRepresentationSerializer


class KPIEvaluationModelViewSet(viewsets.ModelViewSet):
    serializer_class = EvaluationModelSerializer
    display_config_class = KPIEvaluationDisplayConfig
    endpoint_config_class = KPIEvaluationEndpointConfig
    queryset = Evaluation.objects.all()
    filter_backends = (
        filters.SearchFilter,
        filters.OrderingFilter,
        DjangoFilterBackend,
    )
    filterset_class = KPIEvaluationFilterSet
    ordering = ["-evaluated_period"]
    ordering_fields = ["person", "evaluated_score", "evaluation_date", "evaluated_period"]

    def get_queryset(self):
        queryset = super().get_queryset().filter(kpi__id=self.kwargs["kpi_id"]).annotate(goal=F("kpi__goal"))
        if KPI.is_administrator(self.request.user):
            return queryset
        return queryset.filter(person=self.request.user.profile)

    def get_aggregates(self, queryset, paginated_queryset):
        if queryset.exists():
            kpi = get_object_or_404(KPI, pk=self.kwargs["kpi_id"])
            person_ids = kpi.evaluated_persons.all().values_list("id", flat=True)
            evaluation = queryset.filter(person__id__in=person_ids).order_by("evaluation_date").last()
            evaluated_score = kpi.get_handler().evaluate(kpi, evaluation_date=evaluation.evaluation_date)
            return {
                "evaluated_score": {"Σ": format_number(evaluated_score)},
            }
        return {}


class EvaluationGraphChartViewset(viewsets.ChartViewSet):
    filter_backends = (DjangoFilterBackend,)
    queryset = Evaluation.objects.all()
    endpoint_config_class = EvaluationGraphEndpointConfig
    title_config_class = EvaluationGraphTitleConfig
    # filterset_class = EvaluationGraphFilter

    def get_queryset(self):
        queryset = super().get_queryset().filter(kpi__id=self.kwargs["kpi_id"]).annotate(goal=F("kpi__goal"))
        if KPI.is_administrator(self.request.user):
            return queryset
        return queryset.filter(person=self.request.user.profile)

    def get_dataframe_period(self, kpi_id):
        kpi = KPI.objects.get(id=kpi_id)
        list_date = list(
            pd.date_range(
                start=kpi.period.lower,
                end=kpi.period.upper,
                freq=KPI.Interval.get_frequence_correspondance(kpi.evaluated_intervals),
            )
        )
        list_date = [_date.date() for _date in list_date]

        df_date = pd.DataFrame(list_date, columns=["evaluation_date"])
        df_goal = df_date.copy()
        df_goal["goal"] = kpi.goal
        df_date = df_date.set_index("evaluation_date")
        return df_date, df_goal["goal"]

    def get_plotly(self, queryset):
        fig = go.Figure()
        if queryset.exists():
            kpi = KPI.objects.get(id=self.kwargs["kpi_id"])
            activity_type = kpi.additional_data.get("list_data").pop(0) if kpi.additional_data.get("list_data") else ""
            parameters = kpi.additional_data.get("list_data")

            df = pd.DataFrame(
                queryset.values(
                    "evaluation_date", "person__first_name", "person__last_name", "evaluated_score", "goal"
                )
            )
            df["Name"] = df["person__first_name"] + " " + df["person__last_name"]
            df["Name"] = df["Name"].fillna("Group")
            df = df.set_index(["Name", "evaluation_date"]).evaluated_score.unstack("Name")
            df_date, goal = self.get_dataframe_period(self.kwargs["kpi_id"])

            df = df.merge(df_date, on=["evaluation_date"], how="outer")
            df = df.sort_values(by=["evaluation_date"]).fillna("")
            pd.options.plotting.backend = "plotly"
            fig = df.plot.line(labels=dict(value="#KPI", variable="Name"), markers=True)
            fig.update_traces(hovertemplate=None)
            fig.update_layout(
                title=gettext("<b>Parameters</b>: {}<br>{} ").format(parameters, activity_type),
                hovermode="x",
                xaxis_rangeslider_visible=True,
                autosize=True,
            )
            fig.update_xaxes(title="")
            fig.add_trace(  # goal line
                go.Scatter(
                    x=df.index,
                    y=goal,
                    name=gettext("Goal"),
                    mode="lines",
                    line=dict(color="Green", width=4, dash="dot"),
                )
            )
            fig.add_trace(  # diagonal line
                go.Scatter(
                    x=df.index,
                    y=(goal / len(df)).cumsum().round(2),
                    mode="lines",
                    name=gettext("Progress expected to reach goal"),
                    line=dict(color="springgreen", width=3, dash="dot"),
                )
            )
        return fig


class KPIEvaluationPandasViewSet(PandasAPIViewSet):
    IDENTIFIER = "wbcommission:kpievaluationpandas"
    queryset = Evaluation.objects.all()

    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )

    search_fields = ["kpi__name", "person__computed_str"]
    ordering_fields = [
        "evaluated_period",
        "evaluation_date",
    ]

    display_config_class = KPIEvaluationPandasDisplayConfig
    title_config_class = KPIEvaluationPandasTitleConfig
    endpoint_config_class = KPIEvaluationPandasEndpointConfig
    filterset_class = KPIEvaluationPandasFilter

    def get_queryset(self):
        queryset = super().get_queryset().annotate(goal=F("kpi__goal"), kpi_name=F("kpi__name"))
        if KPI.is_administrator(self.request.user):
            return queryset
        return queryset.filter(kpi__evaluated_persons=self.request.user.profile)

    def get_pandas_fields(self, request):
        fields = [
            pf.PKField("id", label=_("ID")),
            pf.CharField(key="person", label=_("Person")),
            pf.CharField(key="kpi", label=_("KPI")),
            pf.CharField(key="kpi_name", label=_("KPI")),
            pf.CharField(key="period", label=_("Period")),
            pf.DateField(key="evaluation_date", label=_("Evaluation Date")),
            pf.IntegerField(key="goal", label=_("Goal")),
            pf.IntegerField(key="evaluated_score", label=_("Evaluated Score")),
            pf.CharField(key="progression", label=_("Progression")),
        ]
        return pf.PandasFields(fields=tuple(fields))

    def get_dataframe(self, request, queryset, **kwargs):
        df = pd.DataFrame()
        if queryset.exists():
            df = pd.DataFrame(
                queryset.order_by("evaluation_date").values(
                    "kpi",
                    "kpi_name",
                    "kpi__period",
                    "evaluation_date",
                    "goal",
                    "person__computed_str",
                    "evaluated_score",
                )
            )
            df["kpi__period"] = df["kpi__period"].apply(
                lambda x: f"{x.lower.strftime('%d.%m.%Y')} - {x.upper.strftime('%d.%m.%Y')}"
            )

            df["person__computed_str"] = df["person__computed_str"].fillna("Group").astype(str)
            df = df.rename(columns={"kpi__period": "period", "person__computed_str": "person"})
            df = df.pivot_table(
                index=["person", "kpi"],
                values=["kpi_name", "evaluation_date", "period", "goal", "evaluated_score"],
                aggfunc="last",
            )
            if "evaluated_score" in df.columns:
                df["progression"] = ((df["evaluated_score"] / df["goal"]) * 100).round(2).astype(str) + "%"
            else:
                df["progression"] = "0%"

            df = df.reset_index()
            df["id"] = df.index
        return df
