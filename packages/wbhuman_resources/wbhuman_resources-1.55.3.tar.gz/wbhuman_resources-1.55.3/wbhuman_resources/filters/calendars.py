from django.utils.translation import gettext_lazy as _
from wbcore import filters as wb_filters
from wbcore.filters.defaults import current_year_date_range

from wbhuman_resources.models import DayOff


class DayOffFilter(wb_filters.FilterSet):
    date = wb_filters.DateRangeFilter(
        label=_("Date Range"),
        required=True,
        clearable=False,
        method=wb_filters.DateRangeFilter.base_date_range_filter_method,
        initial=current_year_date_range,
    )

    def start_filter(self, queryset, name, value):
        if value:
            return queryset.filter(date__gte=value)
        return queryset

    def end_filter(self, queryset, name, value):
        if value:
            return queryset.filter(date__lte=value)
        return queryset

    class Meta:
        model = DayOff
        fields = {"count_as_holiday": ["exact"], "calendar": ["exact"]}
