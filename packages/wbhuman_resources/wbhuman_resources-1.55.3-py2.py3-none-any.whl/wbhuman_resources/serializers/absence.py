from dataclasses import dataclass
from datetime import date

from django.contrib.messages import info
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.reverse import reverse
from wbcore import serializers as wb_serializers
from wbcore.contrib.authentication.serializers import GroupRepresentationSerializer
from wbcore.contrib.geography.serializers import CountryRepresentationSerializer

from wbhuman_resources.models import (
    AbsenceRequest,
    AbsenceRequestPeriods,
    AbsenceRequestType,
    EmployeeHumanResource,
)

from .calendars import DefaultDailyPeriodRepresentationSerializer
from .employee import (
    EmployeeHumanResourceRepresentationSerializer,
    EmployeeYearBalanceRepresentationSerializer,
    PositionRepresentationSerializer,
)


class AbsenceRequestTypeModelSerializer(wb_serializers.ModelSerializer):
    _extra_notify_groups = GroupRepresentationSerializer(source="extra_notify_groups", many=True)

    @wb_serializers.register_only_instance_resource()
    def crossborder_countries_additional_resources(self, instance, request, user, **kwargs):
        return {
            "crossbordercountries": reverse(
                "wbhuman_resources:absencerequesttype-crossbordercountry-list",
                args=[instance.id],
                request=request,
            )
        }

    class Meta:
        model = AbsenceRequestType
        fields = [
            "id",
            "title",
            "is_vacation",
            "is_timeoff",
            "is_extensible",
            "auto_approve",
            "days_in_advance",
            "is_country_necessary",
            "extra_notify_groups",
            "_extra_notify_groups",
            "icon",
            "color",
            "_additional_resources",
        ]


class AbsenceRequestTypeRepresentationSerializer(wb_serializers.RepresentationSerializer):
    endpoint = "wbhuman_resources:absencerequesttyperepresentation-list"
    _detail = wb_serializers.HyperlinkField(reverse_name="wbhuman_resources:absencerequesttype-detail")

    class Meta:
        model = AbsenceRequestType
        fields = [
            "id",
            "title",
            "_detail",
        ]


class AbsenceRequestCrossBorderCountryModelSerializer(wb_serializers.ModelSerializer):
    geography_repr = wb_serializers.CharField(read_only=True)
    _geography = CountryRepresentationSerializer(source="geography")

    class Meta:
        model = AbsenceRequestType.crossborder_countries.through
        fields = ("id", "geography_repr", "_geography", "geography", "absencerequesttype")


@dataclass
class CurrentUserDefaultPeriodDateTimeRange:
    requires_context = True
    user_attr = "profile.human_resources"

    def __call__(self, serializer_instance):
        employee = wb_serializers.CurrentUserDefault("profile.human_resources")(serializer_instance)
        if employee:
            return employee.calendar.get_default_fullday_period(date.today())


def get_lower_time_choices(field, request):
    if (profile := request.user.profile) and (employee := getattr(profile, "human_resources", None)):
        return employee.calendar.get_period_start_choices()
    return []


def get_upper_time_choices(field, request):
    if (profile := request.user.profile) and (employee := getattr(profile, "human_resources", None)):
        return employee.calendar.get_period_end_choices()
    return []


class AbsenceRequestModelSerializer(wb_serializers.ModelSerializer):
    type_icon = wb_serializers.IconSelectField(read_only=True)
    _type = AbsenceRequestTypeRepresentationSerializer(source="type")
    employee = wb_serializers.PrimaryKeyRelatedField(
        default=wb_serializers.CurrentUserDefault(user_attr="profile.human_resources"),
        queryset=EmployeeHumanResource.active_internal_employees.all(),
        read_only=lambda view: not view.request.user.has_perm("wbhuman_resources.administrate_absencerequest"),
    )
    _employee = EmployeeHumanResourceRepresentationSerializer(source="employee")
    period = wb_serializers.DateTimeRangeField(
        default=CurrentUserDefaultPeriodDateTimeRange(),
        lower_time_choices=get_lower_time_choices,
        upper_time_choices=get_upper_time_choices,
    )

    created = wb_serializers.DateTimeField(read_only=True)
    reason = wb_serializers.TextField(label="Reason for refusal", read_only=lambda view: not view.can_administrate)

    _total_hours = wb_serializers.FloatField(
        label=_("Total Hours"),
        required=False,
        read_only=True,
        help_text=_("The total number of hours this request spans (i.e. only actual working days)"),
    )
    _total_vacation_hours = wb_serializers.FloatField(
        label=_("Vacation Hours"),
        required=False,
        read_only=True,
        help_text=_("The number of vacation hours this request uses"),
    )

    _total_hours_in_days = wb_serializers.FloatField(
        label=_("Total Days"),
        required=False,
        read_only=True,
        help_text=_("The total number of days this request spans (i.e. only actual working days)"),
    )
    _total_vacation_hours_in_days = wb_serializers.FloatField(
        label=_("Vacation Days"),
        required=False,
        read_only=True,
        help_text=_("The number of vacation days this request uses"),
    )

    department = wb_serializers.PrimaryKeyRelatedField(read_only=True)
    _department = PositionRepresentationSerializer(source="department")

    _crossborder_country = CountryRepresentationSerializer(source="crossborder_country")

    @wb_serializers.register_only_instance_resource()
    def additional_resources(self, instance, request, user, **kwargs):
        res = {}
        res["periods"] = reverse(
            "wbhuman_resources:request-periods-list",
            args=[instance.id],
            request=request,
        )
        if instance and instance.type.is_extensible and instance.status == AbsenceRequest.Status.APPROVED.name:
            if not instance.next_extensible_period:
                info(
                    request,
                    _(
                        "This request cannot be extended because the next available date is already taken. Please amend this request first"
                    ),
                )
            else:
                res["increase_days"] = reverse(
                    "wbhuman_resources:absencerequest-increaseday",
                    args=[instance.id],
                    request=request,
                )
        return res

    def validate(self, data):
        errors = {}
        obj = self.instance
        request_type = data.get("type", obj.type if obj else None)
        if not request_type:
            raise serializers.ValidationError({"type": [_("A type needs to be provided")]})
        # check crossborder rules
        try:
            request_type.validate_country(data.get("crossborder_country", obj.crossborder_country if obj else None))
        except ValueError as e:
            errors["crossborder_country"] = e.args[0]

        # If the user does not have the permission to administrate all the vacation requests,
        # then we need to set the profile here, because this is, in this case, a read only field.
        # if obj already exist the owner employee is not updated, important for keep the same employee when the manager update the object
        if (
            data
            and (request := self.context.get("request"))
            and (user_employee := getattr(request.user.profile, "human_resources", None))
        ):
            if not request.user.has_perm("wbhuman_resources.administrate_absencerequest") and not obj:
                data["employee"] = user_employee

            employee = data.get("employee", obj.employee if obj else None)
            period = data.get("period", obj.period if obj else None)

            # Check if the period is a valid datetime range
            if period.lower >= period.upper:
                errors["period"] = [gettext("End date cannot be before start date")]

            # If requester is not a manager of the request's employee, we check if the request can be taken given the time rules
            if not user_employee.is_manager_of(employee) and not EmployeeHumanResource.is_administrator(request.user):
                now = timezone.now()
                if period.lower < now or period.upper < now:
                    errors["period"] = [
                        gettext("You cannot save or modify an absence already started or already finished")
                    ]
                if (period.lower.date() - now.date()).days < request_type.days_in_advance:
                    errors["period"] = [
                        gettext("The request needs to start at least {days_in_advance} days from now").format(
                            days_in_advance=request_type.days_in_advance
                        )
                    ]

            # Check if overlapping requests exists
            if (
                AbsenceRequest.objects.exclude(
                    status__in=[AbsenceRequest.Status.CANCELLED, AbsenceRequest.Status.DENIED]
                )
                .filter(
                    models.Q(employee=employee)
                    & ~models.Q(id=obj.id if obj else -1)  # TODO: Remove later - Not really needed (probably)
                    & models.Q(period__overlap=period)
                )
                .exists()
            ):
                errors["non_field_errors"] = [
                    _("Overlaping requests already exists at the specified periods. Please change the dates.")
                ]
            if len(errors.keys()) > 0:
                raise serializers.ValidationError(errors)

        return data

    class Meta:
        model = AbsenceRequest
        fields = [
            "id",
            "type_icon",
            "status",
            "employee",
            "_employee",
            "period",
            "type",
            "_type",
            "notes",
            "reason",
            "_total_hours",
            "_total_vacation_hours",
            "_total_hours_in_days",
            "_total_vacation_hours_in_days",
            "created",
            "attachment",
            "department",
            "_department",
            "_additional_resources",
            "is_cancelled",
            "_crossborder_country",
            "crossborder_country",
        ]


class EmployeeAbsenceDaysModelSerializer(wb_serializers.ModelSerializer):
    year = wb_serializers.YearField(read_only=True)
    absence_type = wb_serializers.ChoiceField(read_only=True, choices=AbsenceRequestType.get_choices())
    hours_count = wb_serializers.FloatField(read_only=True)
    days_count = wb_serializers.FloatField(read_only=True)
    id = wb_serializers.PrimaryKeyCharField()

    class Meta:
        model = AbsenceRequestPeriods
        fields = ["id", "absence_type", "year", "hours_count", "days_count"]


class AbsenceRequestPeriodsModelSerializer(wb_serializers.ModelSerializer):
    _balance = EmployeeYearBalanceRepresentationSerializer(source="balance")
    _default_period = DefaultDailyPeriodRepresentationSerializer(source="default_period")
    _total_hours = wb_serializers.FloatField(read_only=True, required=False)

    class Meta:
        model = AbsenceRequestPeriods
        fields = [
            "id",
            "request",
            "employee",
            "default_period",
            "_default_period",
            "date",
            "timespan",
            "_total_hours",
            "balance",
            "_balance",
            "consecutive_hours_count",
        ]
        read_only_fields = fields


class IncreaseDaySerializer(wb_serializers.Serializer):
    number_days = wb_serializers.IntegerField(label=_("Increase absence by"), default=1)
