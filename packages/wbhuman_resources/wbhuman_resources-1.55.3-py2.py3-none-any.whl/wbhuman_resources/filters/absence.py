from datetime import date, timedelta

import pandas as pd
from django.utils.timezone import localdate
from django.utils.translation import gettext_lazy as _
from psycopg.types.range import TimestamptzRange
from wbcore import filters as wb_filters
from wbcore.contrib.agenda.filters import CalendarItemPeriodBaseFilterSet

from wbhuman_resources.models import (
    AbsenceRequest,
    AbsenceRequestPeriods,
    AbsenceRequestType,
    Position,
)


def current_year_date_start(*args, **kwargs):
    d = localdate()
    return date(d.year, 1, 1)


def current_year_date_end(*args, **kwargs):
    d = localdate()
    return max((d + pd.tseries.offsets.YearEnd(1)).date(), d + timedelta(days=60))


class AbsenceRequestFilter(CalendarItemPeriodBaseFilterSet):
    conference_room = boolean_conference_room = None
    department = wb_filters.ModelChoiceFilter(
        label=_("Department"),
        queryset=Position.objects.all(),
        endpoint=Position.get_representation_endpoint(),
        value_key=Position.get_representation_value_key(),
        label_key=Position.get_representation_label_key(),
        method="filter_position",
    )
    is_active_employee = wb_filters.BooleanFilter(
        label=_("Is Employee Active"), method="boolean_is_active_employee", initial=True
    )
    _total_hours_in_days__gte = wb_filters.NumberFilter(
        lookup_expr="gte", label="Total hours", field_name="_total_hours_in_days"
    )
    _total_vacation_hours_in_days__gte = wb_filters.NumberFilter(
        lookup_expr="gte", label="Total hours", field_name="_total_vacation_hours_in_days"
    )
    _total_hours_in_days__lte = wb_filters.NumberFilter(
        lookup_expr="lte", label="Total hours", field_name="_total_hours_in_days"
    )
    _total_vacation_hours_in_days__lte = wb_filters.NumberFilter(
        lookup_expr="lte", label="Total hours", field_name="_total_vacation_hours_in_days"
    )

    def get_default_period(self):
        return TimestamptzRange(lower=current_year_date_start(), upper=current_year_date_end())

    def boolean_is_active_employee(self, queryset, name, value):
        if value:
            return queryset.filter(employee__is_active=True)
        #     return queryset.filter(employee__in=EmployeeHumanResource.active_internal_employees.all())
        return queryset

    def filter_position(self, queryset, name, value):
        if value:
            return queryset.filter(department__in=value.get_descendants(include_self=True)).distinct()
        return queryset

    class Meta:
        model = AbsenceRequest
        fields = {
            "employee": ["exact"],
            "status": ["exact"],
            "type": ["exact"],
            "created": ["gte", "exact", "lte"],
        }


class AbsenceTypeCountEmployeeModelFilterSet(wb_filters.FilterSet):
    year = wb_filters.YearFilter(field_name="year", lookup_expr="exact")

    absence_type = wb_filters.ModelChoiceFilter(
        label=_("Type"),
        queryset=AbsenceRequestType.objects.all(),
        endpoint=AbsenceRequestType.get_representation_endpoint(),
        value_key=AbsenceRequestType.get_representation_value_key(),
        label_key=AbsenceRequestType.get_representation_label_key(),
        method="filter_absence_type",
    )

    def filter_absence_type(self, queryset, label, value):
        if value:
            return queryset.filter(request__type=value)
        return queryset

    class Meta:
        model = AbsenceRequestPeriods
        fields = {}


class AbsenceRequestEmployeeHumanResourceFilterSet(AbsenceRequestFilter):
    department = is_active_employee = None

    class Meta:
        model = AbsenceRequest
        fields = {
            "status": ["exact"],
            "type": ["exact"],
            "created": ["gte", "exact", "lte"],
        }
