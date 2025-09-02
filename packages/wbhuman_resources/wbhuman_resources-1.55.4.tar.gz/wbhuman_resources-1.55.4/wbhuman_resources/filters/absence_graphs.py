from datetime import timedelta

import pandas as pd
from django.utils.timezone import localdate
from django.utils.translation import gettext_lazy as _
from dynamic_preferences.registries import global_preferences_registry
from psycopg.types.range import TimestamptzRange
from wbcore import filters as wb_filters

from wbhuman_resources.models import AbsenceRequestPeriods, DayOffCalendar, Position


def current_year_date_range(*args, **kwargs):
    d = localdate()
    return TimestamptzRange(
        (localdate() - pd.tseries.offsets.Week(weekday=0)).date(),
        max((d + pd.tseries.offsets.YearEnd(1)).date(), d + timedelta(days=60)),
    )


def monday_of_current_week(*args, **kwargs):
    today = localdate()
    return today - timedelta(days=today.weekday())


def get_calendar_default(field, request, view, **kwargs) -> int | None:
    if (profile := request.user.profile) and (employee := getattr(profile, "human_resources", None)):
        return employee.calendar.id
    if calendar := global_preferences_registry.manager()["wbhuman_resources__employee_default_calendar"]:
        return calendar.id
    try:
        return DayOffCalendar.objects.first().id
    except AttributeError:
        return None


class AbsenceRequestPlannerFilter(wb_filters.FilterSet):
    calendar = wb_filters.ModelChoiceFilter(
        label=_("Calendar"),
        required=True,
        clearable=False,
        queryset=DayOffCalendar.objects.all(),
        endpoint=DayOffCalendar.get_representation_endpoint(),
        value_key=DayOffCalendar.get_representation_value_key(),
        label_key=DayOffCalendar.get_representation_label_key(),
        initial=get_calendar_default,
        method=lambda queryset, label, value: queryset,
    )

    date = wb_filters.DateRangeFilter(
        label=_("Date Range"),
        method=lambda queryset, label, value: queryset,
        required=True,
        clearable=False,
        initial=current_year_date_range,
    )
    only_employee_with_absence_periods = wb_filters.BooleanFilter(
        initial=False,
        label=_("Only Employee With Absence periods"),
        method=lambda queryset, label, value: queryset,
    )

    position = wb_filters.ModelChoiceFilter(
        label=_("Position"),
        queryset=Position.objects.all(),
        endpoint=Position.get_representation_endpoint(),
        value_key=Position.get_representation_value_key(),
        label_key=Position.get_representation_label_key(),
        method=lambda queryset, label, value: queryset,
    )

    class Meta:
        model = AbsenceRequestPeriods
        fields = {}


class AbsenceTableFilter(AbsenceRequestPlannerFilter):
    date_gte = date_lte = None
    date = wb_filters.DateFilter(
        label=_("Week Day"),
        method=lambda queryset, label, value: queryset,
        initial=monday_of_current_week,
        required=True,
        help_text="Change this date to any day on the week you are interested in seeing the presence table",
    )
