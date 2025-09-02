from wbcore import viewsets

from wbhuman_resources.filters import DayOffFilter
from wbhuman_resources.models import (
    DayOff,
    DayOffCalendar,
    DefaultDailyPeriod,
    EmployeeWeeklyOffPeriods,
)
from wbhuman_resources.serializers import (
    DayOffCalendarModelSerializer,
    DayOffCalendarRepresentationSerializer,
    DayOffModelSerializer,
    DayOffRepresentationSerializer,
    DefaultDailyPeriodModelSerializer,
    DefaultDailyPeriodRepresentationSerializer,
    EmployeeWeeklyOffPeriodsRepresentationSerializer,
)
from wbhuman_resources.viewsets.display import (
    DayOffCalendarDisplayConfig,
    DayOffDayOffCalendarDisplayConfig,
    DayOffDisplayConfig,
    DefaultDailyPeriodDayOffCalendarDisplayConfig,
)
from wbhuman_resources.viewsets.endpoints import (
    DayOffDayOffCalendarEndpointConfig,
    DefaultDailyPeriodDayOffCalendar,
)


class DefaultDailyPeriodRepresentationViewSet(viewsets.RepresentationViewSet):
    queryset = DefaultDailyPeriod.objects.all()
    serializer_class = DefaultDailyPeriodRepresentationSerializer

    search_fields = ("title",)


class EmployeeWeeklyOffPeriodsRepresentationViewSet(viewsets.RepresentationViewSet):
    queryset = EmployeeWeeklyOffPeriods.objects.all()
    serializer_class = EmployeeWeeklyOffPeriodsRepresentationSerializer

    search_fields = ("computed_str",)


class DayOffRepresentationViewSet(viewsets.RepresentationViewSet):
    queryset = DayOff.objects.all()
    serializer_class = DayOffRepresentationSerializer

    search_fields = ("title",)


class DayOffCalendarRepresentationViewSet(viewsets.RepresentationViewSet):
    queryset = DayOffCalendar.objects.all()
    serializer_class = DayOffCalendarRepresentationSerializer

    search_fields = ("title",)


class DayOffModelViewSet(viewsets.ModelViewSet):
    queryset = DayOff.objects.select_related("calendar")
    serializer_class = DayOffModelSerializer

    ordering_fields = ["title", "date"]
    ordering = ["date"]
    search_fields = ["title"]

    filterset_class = DayOffFilter

    display_config_class = DayOffDisplayConfig


class DayOffCalendarModelViewSet(viewsets.ModelViewSet):
    queryset = DayOffCalendar.objects.all()
    serializer_class = DayOffCalendarModelSerializer

    search_fields = ("title",)
    filterset_fields = {"title": ["exact", "iexact"]}

    display_config_class = DayOffCalendarDisplayConfig


# Subviewsets


class DayOffDayOffCalendarModelViewSet(DayOffModelViewSet):
    display_config_class = DayOffDayOffCalendarDisplayConfig
    endpoint_config_class = DayOffDayOffCalendarEndpointConfig

    def get_queryset(self):
        return super().get_queryset().filter(calendar=self.kwargs["calendar_id"])


class DefaultDailyPeriodDayOffCalendarModelViewSet(viewsets.ModelViewSet):
    queryset = DefaultDailyPeriod.objects.all()
    serializer_class = DefaultDailyPeriodModelSerializer

    ordering = ["lower_time"]

    display_config_class = DefaultDailyPeriodDayOffCalendarDisplayConfig
    endpoint_config_class = DefaultDailyPeriodDayOffCalendar

    def get_queryset(self):
        return super().get_queryset().filter(calendar=self.kwargs["calendar_id"])
