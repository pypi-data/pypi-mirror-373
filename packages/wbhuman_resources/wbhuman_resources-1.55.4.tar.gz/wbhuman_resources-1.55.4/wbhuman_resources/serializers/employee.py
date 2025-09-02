from django.utils.translation import gettext_lazy as _
from rest_framework.reverse import reverse
from wbcore import serializers as wb_serializers
from wbcore.contrib.authentication.serializers import GroupRepresentationSerializer
from wbcore.contrib.directory.models import Person
from wbcore.contrib.directory.serializers import PersonRepresentationSerializer

from wbhuman_resources.models import (
    EmployeeHumanResource,
    EmployeeWeeklyOffPeriods,
    EmployeeYearBalance,
    Position,
)

from .calendars import (
    DayOffCalendarRepresentationSerializer,
    DefaultDailyPeriodRepresentationSerializer,
)


class PositionRepresentationSerializer(wb_serializers.RepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbhuman_resources:position-detail")

    class Meta:
        model = Position
        fields = ("id", "computed_str", "height", "level", "_detail")


class EmployeeYearBalanceRepresentationSerializer(wb_serializers.RepresentationSerializer):
    class Meta:
        model = EmployeeYearBalance
        fields = ("id", "computed_str")


class EmployeeHumanResourceRepresentationSerializer(wb_serializers.RepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbhuman_resources:employee-detail")

    class Meta:
        model = EmployeeHumanResource
        fields = ("id", "computed_str", "is_active", "_detail")


class EmployeeWeeklyOffPeriodsModelSerializer(wb_serializers.ModelSerializer):
    _employee = EmployeeHumanResourceRepresentationSerializer(source="calendar")
    _period = DefaultDailyPeriodRepresentationSerializer(source="period")

    class Meta:
        model = EmployeeWeeklyOffPeriods
        fields = ("id", "employee", "period", "weekday", "_employee", "_period", "computed_str")


class PositionModelSerializer(wb_serializers.ModelSerializer):
    _parent = PositionRepresentationSerializer(source="parent")
    _manager = PersonRepresentationSerializer(source="manager", filter_params={"is_internal_profile": True})
    _groups = GroupRepresentationSerializer(source="groups", many=True)

    class Meta:
        model = Position
        read_only_fields = ["groups", "_groups"]
        fields = [
            "id",
            "name",
            "color",
            "computed_str",
            "level",
            "height",
            "parent",
            "_parent",
            "manager",
            "_manager",
            "_groups",
            "groups",
        ]


class EmployeeBalanceModelSerializer(wb_serializers.ModelSerializer):
    _profile = PersonRepresentationSerializer(source="profile")
    _position = PositionRepresentationSerializer(source="position")
    _calendar = DayOffCalendarRepresentationSerializer(source="calendar")

    available_vacation_balance_previous_year = wb_serializers.FloatField(
        label=_("Available Vacation Balance from previous year"),
        read_only=True,
        help_text=_(
            "Available Vacation Balance from previous year. Can only be used until a certain point the next year."
        ),
    )
    available_vacation_balance_current_year = wb_serializers.FloatField(
        label=_("Available Vacation Balance from current year"),
        read_only=True,
        help_text=_("Available Vacation Balance from the current year balance."),
    )

    available_vacation_balance_next_year = wb_serializers.FloatField(
        label=_("Available Vacation Balance from next year"),
        read_only=True,
        help_text=_("Available Vacation Balance from the next year balance."),
    )

    took_long_vacations = wb_serializers.BooleanField(
        label=_("Long Vacation"),
        help_text=_("True if the user took at least one long vacation in a row"),
        read_only=True,
        default=False,
    )

    extra_days_per_period = wb_serializers.FloatField(read_only=True, label=_("Extra days per period"))

    @wb_serializers.register_resource()
    def additional_resources(self, instance, request, user):
        additional_resources = dict()

        additional_resources["periods_count_per_type"] = reverse(
            "wbhuman_resources:employee-absencecount-list",
            args=[instance.id],
            request=request,
        )
        additional_resources["absencerequest"] = reverse(
            "wbhuman_resources:employee-absencerequest-list",
            args=[instance.id],
            request=request,
        )

        if (view := request.parser_context["view"]) and view.is_administrator:
            additional_resources["employeeyearbalance"] = reverse(
                "wbhuman_resources:employee-employeeyearbalance-list",
                args=[instance.id],
                request=request,
            )
        return additional_resources

    class Meta:
        model = EmployeeHumanResource
        percent_fields = ["occupancy_rate"]
        fields = [
            "id",
            "profile",
            "computed_str",
            "position",
            "_position",
            "is_active",
            "enrollment_at",
            "_profile",
            "extra_days_frequency",
            "extra_days_per_period",
            "occupancy_rate",
            "contract_type",
            "available_vacation_balance_previous_year",
            "available_vacation_balance_current_year",
            "available_vacation_balance_next_year",
            "took_long_vacations",
            "calendar",
            "_calendar",
            "_additional_resources",
        ]


class EmployeeModelSerializer(wb_serializers.ModelSerializer):
    _direct_manager = PersonRepresentationSerializer(
        source="direct_manager", filter_params={"is_internal_profile": True}
    )
    _position = PositionRepresentationSerializer(source="position")
    _calendar = DayOffCalendarRepresentationSerializer(source="calendar")
    _profile = PersonRepresentationSerializer(source="profile")

    position_manager = wb_serializers.PrimaryKeyRelatedField(read_only=True)
    _position_manager = PersonRepresentationSerializer(
        source="position_manager", filter_params={"is_internal_profile": True}
    )
    top_position_repr = wb_serializers.CharField(read_only=True, default="")
    primary_email = wb_serializers.CharField(default="", label=_("Primary Email"), allow_null=True, read_only=True)
    primary_address = wb_serializers.CharField(default="", label=_("Primary Address"), allow_null=True, read_only=True)
    primary_telephone = wb_serializers.TelephoneField(label=_("Primary Telephone"), allow_null=True, read_only=True)

    @wb_serializers.register_resource()
    def extra_additional_resources(self, instance, request, user):
        res = dict()

        if instance.is_active and (view := request.parser_context["view"]):
            if view.is_administrator:
                res["deactivate"] = reverse(
                    "wbhuman_resources:employee-deactivate",
                    args=[instance.id],
                    request=request,
                )

            if (
                view.is_administrator or instance in view.employee.get_managed_employees()
            ) and instance.balances.exists():
                res["balance_and_usage"] = reverse(
                    "wbhuman_resources:employeebalance-detail",
                    args=[instance.id],
                    request=request,
                )
        return res

    class Meta:
        fields = [
            "id",
            "_profile",
            "profile",
            "position",
            "_position",
            "_position_manager",
            "position_manager",
            "top_position_repr",
            "primary_telephone",
            "primary_email",
            "primary_address",
            "direct_manager",
            "_direct_manager",
            "calendar",
            "_calendar",
            "enrollment_at",
            "occupancy_rate",
            "contract_type",
            "is_active",
            "extra_days_frequency",
            "_additional_resources",
        ]
        model = EmployeeHumanResource


class DeactivateEmployeeSerializer(wb_serializers.Serializer):
    substitute = wb_serializers.PrimaryKeyRelatedField(
        queryset=Person.objects.all(), label=_("Substitution Person"), many=False
    )
    _substitute = PersonRepresentationSerializer(source="substitute")


class EmployeeYearBalanceModelSerializer(EmployeeYearBalanceRepresentationSerializer):
    _employee = EmployeeHumanResourceRepresentationSerializer(source="employee")
    _balance = wb_serializers.FloatField(read_only=True, label="Given yearly balance (in hours)")
    _number_mandatory_days_off = wb_serializers.FloatField(read_only=True, label="Mandatory days off (in hours)")
    _total_vacation_hourly_usage = wb_serializers.FloatField(read_only=True, label="Hourly usage (in hours)")
    actual_total_vacation_hourly_balance = wb_serializers.FloatField(
        read_only=True, label="Hourly available balance (in hours)"
    )

    _balance_in_days = wb_serializers.FloatField(read_only=True, label="Given yearly balance (in days)")
    _number_mandatory_days_off_in_days = wb_serializers.FloatField(
        read_only=True, label="Mandatory days off (in days)"
    )
    _total_vacation_hourly_usage_in_days = wb_serializers.FloatField(read_only=True, label="Hourly usage (in days)")
    actual_total_vacation_hourly_balance_in_days = wb_serializers.FloatField(
        read_only=True, label="Hourly available balance (in days)"
    )

    class Meta:
        model = EmployeeYearBalance
        fields = [
            "id",
            "employee",
            "_employee",
            "extra_balance",
            "year",
            "_balance",
            "_number_mandatory_days_off",
            "_total_vacation_hourly_usage",
            "actual_total_vacation_hourly_balance",
            "_balance_in_days",
            "_number_mandatory_days_off_in_days",
            "_total_vacation_hourly_usage_in_days",
            "actual_total_vacation_hourly_balance_in_days",
            "_additional_resources",
        ]
        read_only_fields = fields
