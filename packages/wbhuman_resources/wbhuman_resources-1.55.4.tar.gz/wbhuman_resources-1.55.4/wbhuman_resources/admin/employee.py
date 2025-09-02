from django.contrib import admin

from ..models.employee import (
    BalanceHourlyAllowance,
    EmployeeHumanResource,
    EmployeeYearBalance,
    Position,
)
from .calendars import EmployeeWeeklyOffPeriodsInLine


class PositionInline(admin.TabularInline):
    model = Position
    extra = 0


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("name", "height", "manager")

    raw_id_fields = ["groups", "manager"]
    autocomplete_fields = ["groups", "manager"]


class BalanceHourlyAllowanceTabularAdmin(admin.TabularInline):
    model = BalanceHourlyAllowance
    fk_name = "balance"


@admin.register(EmployeeYearBalance)
class EmployeeYearBalanceAdmin(admin.ModelAdmin):
    inlines = [BalanceHourlyAllowanceTabularAdmin]


class EmployeeYearBalanceInline(admin.TabularInline):
    model = EmployeeYearBalance
    fields = (
        "year",
        "balance",
        "daily_hours",
        "number_mandatory_days_off",
        "total_vacation_hourly_usage",
        "total_vacation_hourly_balance",
        "balance_in_days",
        "number_mandatory_days_off_in_days",
        "total_vacation_hourly_usage_in_days",
        "total_vacation_hourly_balance_in_days",
    )
    readonly_fields = [
        "balance",
        "daily_hours",
        "number_mandatory_days_off",
        "total_vacation_hourly_usage",
        "total_vacation_hourly_balance",
        "balance_in_days",
        "number_mandatory_days_off_in_days",
        "total_vacation_hourly_usage_in_days",
        "total_vacation_hourly_balance_in_days",
    ]
    extra = 0
    ordering = ("-year",)
    show_change_link = True

    def _number_mandatory_days_off(self, obj):
        return obj._number_mandatory_days_off

    def _total_vacation_hourly_usage(self, obj):
        return obj._total_vacation_hourly_usage

    def _total_vacation_hourly_balance(self, obj):
        return obj._total_vacation_hourly_balance

    def _balance_in_days(self, obj):
        return obj._balance_in_days

    def _number_mandatory_days_off_in_days(self, obj):
        return obj._number_mandatory_days_off_in_days

    def _total_vacation_hourly_usage_in_days(self, obj):
        return obj._total_vacation_hourly_usage_in_days

    def _total_vacation_hourly_balance_in_days(self, obj):
        return obj._total_vacation_hourly_balance_in_days


@admin.register(EmployeeHumanResource)
class EmployeeHumanResourceAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "",
            {
                "fields": (
                    "profile",
                    "is_active",
                    "extra_days_frequency",
                    "occupancy_rate",
                    "contract_type",
                    "position",
                    "enrollment_at",
                    "calendar",
                )
            },
        ),
    )
    raw_id_fields = ("profile",)
    search_fields = ("profile__computed_str",)
    list_display = ("profile", "contract_type", "position", "calendar")
    inlines = (EmployeeYearBalanceInline, EmployeeWeeklyOffPeriodsInLine)
