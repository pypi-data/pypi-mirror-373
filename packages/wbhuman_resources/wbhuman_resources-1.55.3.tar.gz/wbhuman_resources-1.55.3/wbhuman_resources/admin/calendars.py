from django.contrib import admin

from ..models import (
    DayOff,
    DayOffCalendar,
    DefaultDailyPeriod,
    EmployeeWeeklyOffPeriods,
)


@admin.register(DayOffCalendar)
class DayOffCalendarModelAdmin(admin.ModelAdmin):
    pass


@admin.register(DayOff)
class DayOffAdmin(admin.ModelAdmin):
    list_display = ["date", "title", "count_as_holiday", "calendar"]
    ordering = ["date"]


@admin.register(DefaultDailyPeriod)
class DefaultDailyPeriodAdmin(admin.ModelAdmin):
    list_display = ["lower_time", "upper_time", "title", "total_hours"]
    ordering = ["lower_time"]


class EmployeeWeeklyOffPeriodsInLine(admin.TabularInline):
    model = EmployeeWeeklyOffPeriods
    fields = [
        "period",
        "weekday",
    ]
    fk_name = "employee"
    extra = 0
    raw_id_fields = ["employee"]
    ordering = ("weekday", "period__lower_time")
