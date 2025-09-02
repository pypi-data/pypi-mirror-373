from calendar import day_name
from datetime import date, time

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.utils.translation import gettext as _
from wbcore import viewsets
from wbcore.pandas import fields as pf
from wbcore.pandas.views import PandasAPIViewSet
from wbcore.utils.date import get_date_interval_from_request

from wbhuman_resources.filters import AbsenceRequestPlannerFilter, AbsenceTableFilter
from wbhuman_resources.models import (
    AbsenceRequest,
    AbsenceRequestPeriods,
    AbsenceRequestType,
    DayOffCalendar,
    EmployeeHumanResource,
    Position,
)
from wbhuman_resources.viewsets.display import AbsenceTablePandasDisplayConfig
from wbhuman_resources.viewsets.endpoints import (
    AbsenceRequestPlannerEndpointConfig,
    AbsenceTablePandasEndpointConfig,
)
from wbhuman_resources.viewsets.titles import (
    AbsenceRequestPlannerTitleConfig,
    AbsenceTablePandasTitleConfig,
)

from .utils import (
    current_day_range,
    current_month_range,
    current_week_range,
    current_year_range,
)


def update_layoute(fig, start, end):
    fig.layout.xaxis.rangeselector = None
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                active=1,
                x=0.57,
                y=1.2,
                buttons=[
                    dict(
                        label=_("Current Day"),
                        method="relayout",
                        args=[
                            {
                                "xaxis.range": current_day_range(),
                                "xaxis.dtick": 3600000,
                            },
                        ],
                    ),
                    dict(
                        label=_("Current Week"),
                        method="relayout",
                        args=[
                            {
                                "xaxis.range": current_week_range(),
                                "xaxis.dtick": "D1",
                            },
                        ],
                    ),
                    dict(
                        label=_("Current Month"),
                        method="relayout",
                        args=[
                            {
                                "xaxis.range": current_month_range(),
                                "xaxis.dtick": "D3",
                            },
                        ],
                    ),
                    dict(
                        label=_("Current Year"),
                        method="relayout",
                        args=[
                            {
                                "xaxis.range": current_year_range(),
                                "xaxis.dtick": 86400000.0 * 14,
                                "xaxis.tickformat": "%b %d",
                            },
                        ],
                    ),
                    dict(
                        label=_("All"),
                        method="relayout",
                        args=[
                            {"xaxis.range": [start, end]},
                        ],
                    ),
                ],
            )
        ],
        yaxis=dict(
            title="",
            titlefont=dict(color="#000000"),
            tickfont=dict(size=11, family="Courier", color="#000000"),
            anchor="x",
            side="left",
            showline=False,
            linewidth=0.5,
            linecolor="black",
            showgrid=True,
            gridcolor="lightgray",
            gridwidth=1,
            showspikes=True,
            spikecolor="black",
            spikethickness=1,
        ),
        xaxis=dict(
            title="",
            titlefont=dict(color="#000000"),
            tickfont=dict(color="#000000"),
            showline=False,
            linewidth=0.5,
            linecolor="black",
            showgrid=True,
            gridcolor="lightgray",
            gridwidth=2,
            rangeslider=dict(visible=True),
            range=current_week_range(),
            dtick="D1",
            type="date",
            showspikes=True,
            spikemode="across",
            spikecolor="black",
            spikesnap="cursor",
            spikethickness=1,
        ),
        spikedistance=1000,
        hoverdistance=100,
    )

    return fig


def _get_types_color_map():
    type_dict = dict(AbsenceRequestType.objects.values_list("title", "color"))
    type_dict["Day Off"] = "silver"
    type_dict["Holiday"] = "lightblue"
    return type_dict


def _get_status_pattern_map():
    return {
        "APPROVED": "",
        "DRAFT": ".",
        "PENDING": "x",
    }


class AbsenceRequestPlanner(viewsets.ChartViewSet):
    IDENTIFIER = "wbhuman_resources:absenceplanner"

    filterset_class = AbsenceRequestPlannerFilter
    queryset = AbsenceRequestPeriods.objects.all()

    title_config_class = AbsenceRequestPlannerTitleConfig
    endpoint_config_class = AbsenceRequestPlannerEndpointConfig

    def get_plotly(self, queryset):
        start, end = get_date_interval_from_request(self.request)
        calendar = get_object_or_404(DayOffCalendar, pk=self.request.GET.get("calendar", None))
        only_employee_with_absence_periods = (
            self.request.GET.get("only_employee_with_absence_periods", "false") == "true"
        )
        employees = EmployeeHumanResource.active_internal_employees.all()

        if position_id := self.request.GET.get("position", None):
            position = get_object_or_404(Position, pk=position_id)
            employees = employees.filter(position__in=position.get_descendants(include_self=True))

        if queryset.exists() and start and end and employees.exists():
            df = EmployeeHumanResource.get_employee_absence_periods_df(
                calendar, start, end, employees, only_employee_with_absence_periods=only_employee_with_absence_periods
            )

            employees_map = dict(employees.values_list("id", "computed_str"))
            df["employee"] = df.employee.map(employees_map)
            fig = px.timeline(
                df,
                x_start="start",
                x_end="end",
                y=df.employee,
                color="type",
                template="seaborn",
                color_discrete_map=_get_types_color_map(),
                pattern_shape="status",
                pattern_shape_map=_get_status_pattern_map(),
                hover_name="employee",
                hover_data={
                    "start": True,
                    "end": True,
                    "employee": False,
                    "status": False,
                    "type": False,
                },
            )
            now = timezone.now().astimezone(calendar.timezone)
            default_calendar_period = calendar.get_default_fullday_period(now.date())
            valid_now = min(
                max([now, default_calendar_period.lower]), default_calendar_period.upper
            )  # we make sure that the "now" vertical line is within the range of a default calendar day
            fig.add_vline(x=valid_now, line_width=3, line_dash="dash", line_color="red")
            fig = update_layoute(fig, start, end)

            def _time_to_decimal(ts):
                return (ts.hour * 60 + ts.minute) / 60

            rangebreaks = [
                {"pattern": "hour", "bounds": [_time_to_decimal(hours_range[0]), _time_to_decimal(hours_range[1])]}
                for hours_range in calendar.get_unworked_time_range(start_time=time(4, 0, 1))
            ]
            fig.update_xaxes(rangebreaks=rangebreaks)

            return fig
        return go.Figure()


class AbsenceTablePandasViewSet(PandasAPIViewSet):
    IDENTIFIER = "wbhuman_resources:absence_table"

    queryset = AbsenceRequestPeriods.objects.filter(
        Q(employee__in=EmployeeHumanResource.active_internal_employees.all())
        & Q(request__status=AbsenceRequest.Status.APPROVED.name)
    )

    filterset_class = AbsenceTableFilter

    pandas_fields = pf.PandasFields(
        fields=(
            pf.PKField(key="employee", label=_("ID")),
            pf.PKField(key="employee_repr", label=_("Employee"), help_text=_("Test")),
            pf.CharField(key="position", label=_("Department")),
            pf.FloatField(key="monday", label=_("Monday")),
            pf.FloatField(key="tuesday", label=_("Tuesday")),
            pf.FloatField(key="wednesday", label=_("Wednesday")),
            pf.FloatField(key="thursday", label=_("Thursday")),
            pf.FloatField(key="friday", label=_("Friday")),
            pf.FloatField(key="saturday", label=_("Saturday")),
            pf.FloatField(key="sunday", label=_("Sunday")),
        )
    )
    display_config_class = AbsenceTablePandasDisplayConfig
    title_config_class = AbsenceTablePandasTitleConfig
    endpoint_config_class = AbsenceTablePandasEndpointConfig

    ordering_fields = [
        "employee_repr",
        "position",
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
    ]
    ordering = ["position"]
    search_fields = ["employee_repr", "position"]

    @property
    def start_and_end(self) -> tuple[date, date] | None:
        if date_repr := self.request.GET.get("date", None):
            return current_week_range(parse_date(date_repr))
        return None

    def get_dataframe(self, request, queryset, **kwargs) -> pd.DataFrame:
        def _rename_columns(df: pd.DataFrame) -> pd.DataFrame:
            # Rename the columns from datetime.date to the week day name representation (e.g. Monday)
            rename_map = {col: day_name[col.weekday()].lower() for col in df.columns if not isinstance(col, str)}
            return df.rename(columns=rename_map)

        def _get_position(employee_id: int) -> Position | None:
            employee = EmployeeHumanResource.objects.get(id=employee_id)
            if pos := employee.position:
                return pos.get_root().name
            return None

        def _custom_agg(group: pd.DataFrame) -> int:
            default_periods = calendar.default_periods.count()

            if default_periods:
                if len(group) == default_periods:
                    if group["type"].eq("Home Office").sum() == default_periods:
                        # Remote
                        return 3
                    elif group["type"].eq("Home Office").sum() > 0:
                        # Partially Remote
                        return 2
                    else:
                        # Absent
                        return -1
                elif len(group) > 0:
                    # Partially Present
                    return 1
            return 0

        if self.start_and_end:
            start, end = self.start_and_end
            calendar = get_object_or_404(DayOffCalendar, pk=self.request.GET.get("calendar", None))
            employees = EmployeeHumanResource.active_internal_employees.all()

            if position_id := self.request.GET.get("position", None):
                position = get_object_or_404(Position, pk=position_id)
                employees = employees.filter(position__in=position.get_descendants(include_self=True))

            df = EmployeeHumanResource.get_employee_absence_periods_df(calendar, start, end, employees)
            df = df[["date", "employee", "period", "type"]]
            df = df.groupby(["date", "employee"]).apply(_custom_agg).unstack(fill_value=0)  # Present
            df.reset_index(inplace=True)
            df.set_index("date", inplace=True)
            df = _rename_columns(df.reindex(pd.date_range(start, end), fill_value=0).transpose()).reset_index()
            df["position"] = df.employee.apply(lambda x: _get_position(x))
            df["employee_repr"] = df.employee.map(dict(employees.values_list("id", "computed_str")))
            df = df.sort_values(by="employee_repr", ascending=False)
            return df.where(pd.notnull(df), None)
        return pd.DataFrame()
