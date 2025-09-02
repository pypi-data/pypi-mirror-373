from rest_framework.reverse import reverse
from wbcore import serializers as wb_serializers

from wbhuman_resources.models import (
    DayOff,
    DefaultDailyPeriod,
    EmployeeWeeklyOffPeriods,
)
from wbhuman_resources.models.calendars import DayOffCalendar


class DayOffCalendarRepresentationSerializer(wb_serializers.RepresentationSerializer):
    class Meta:
        model = DayOffCalendar
        fields = ("id", "title")


class DefaultDailyPeriodRepresentationSerializer(wb_serializers.RepresentationSerializer):
    class Meta:
        model = DefaultDailyPeriod
        fields = ("id", "lower_time", "upper_time", "title", "total_hours")


class EmployeeWeeklyOffPeriodsRepresentationSerializer(wb_serializers.RepresentationSerializer):
    class Meta:
        model = EmployeeWeeklyOffPeriods
        fields = ("id", "computed_str")


class DayOffRepresentationSerializer(wb_serializers.RepresentationSerializer):
    class Meta:
        model = DayOff
        fields = ("id", "title", "date")


class DayOffCalendarModelSerializer(wb_serializers.ModelSerializer):
    timezone = wb_serializers.TimeZoneField()

    @wb_serializers.register_resource()
    def additional_resources(self, instance, request, user):
        return {
            "days_off": reverse(
                "wbhuman_resources:calendar-dayoff-list",
                args=[instance.id],
                request=request,
            ),
            "default_periods": reverse(
                "wbhuman_resources:calendar-defaultperiod-list",
                args=[instance.id],
                request=request,
            ),
        }

    class Meta:
        model = DayOffCalendar
        fields = ("id", "title", "resource", "timezone", "_additional_resources")


class DefaultDailyPeriodModelSerializer(wb_serializers.ModelSerializer):
    _calendar = DayOffCalendarRepresentationSerializer(source="calendar")

    class Meta:
        model = DefaultDailyPeriod
        fields = ("id", "lower_time", "upper_time", "timespan", "title", "total_hours", "calendar", "_calendar")


class DayOffModelSerializer(wb_serializers.ModelSerializer):
    _calendar = DayOffCalendarRepresentationSerializer(source="calendar")

    class Meta:
        model = DayOff
        fields = ("id", "title", "date", "count_as_holiday", "calendar", "_calendar")
