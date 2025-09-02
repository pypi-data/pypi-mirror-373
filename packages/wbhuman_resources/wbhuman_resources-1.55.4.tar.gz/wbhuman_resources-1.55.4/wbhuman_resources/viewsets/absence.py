import wbcore.serializers as wb_serializers
from django.contrib.messages import info, warning
from django.db.models import Case, CharField, F, Q, Sum, Value, When
from django.db.models.functions import Concat, Extract
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext as _
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.response import Response
from wbcore import viewsets
from wbcore.contrib.agenda.models import CalendarItem
from wbcore.contrib.icons import WBIcon
from wbcore.filters import DjangoFilterBackend
from wbcore.utils.strings import format_number

from wbhuman_resources.filters import (
    AbsenceRequestEmployeeHumanResourceFilterSet,
    AbsenceRequestFilter,
    AbsenceTypeCountEmployeeModelFilterSet,
)
from wbhuman_resources.models import (
    AbsenceRequest,
    AbsenceRequestPeriods,
    AbsenceRequestType,
    EmployeeHumanResource,
)
from wbhuman_resources.serializers import (
    AbsenceRequestCrossBorderCountryModelSerializer,
    AbsenceRequestModelSerializer,
    AbsenceRequestPeriodsModelSerializer,
    AbsenceRequestTypeModelSerializer,
    AbsenceRequestTypeRepresentationSerializer,
    EmployeeAbsenceDaysModelSerializer,
)
from wbhuman_resources.viewsets.buttons import AbsenceRequestButtonConfig
from wbhuman_resources.viewsets.display import (
    AbsenceRequestCrossBorderCountryDisplayConfig,
    AbsenceRequestDisplayConfig,
    AbsenceRequestEmployeeHumanResourceDisplayConfig,
    AbsenceRequestPeriodsAbsenceRequestDisplayConfig,
    AbsenceRequestTypeDisplayConfig,
    AbsenceTypeCountEmployeeDisplayConfig,
)
from wbhuman_resources.viewsets.endpoints import (
    AbsenceRequestCrossBorderCountryEndpointConfig,
    AbsenceRequestEmployeeHumanResourceEndpointConfig,
    AbsenceRequestEndpointConfig,
    AbsenceRequestPeriodsAbsenceRequestEndpointConfig,
    AbsenceTypeCountEmployeeEndpointConfig,
)
from wbhuman_resources.viewsets.titles import (
    AbsenceRequestEmployeeBalanceTitleConfig,
    AbsenceTypeCountEmployeeTitleConfig,
)

from ..models.absence import can_validate_or_deny_request
from ..serializers.absence import (
    CurrentUserDefaultPeriodDateTimeRange,
    get_lower_time_choices,
    get_upper_time_choices,
)
from .mixins import EmployeeViewMixin


class AbsenceRequestTypeRepresentationViewSet(viewsets.RepresentationViewSet):
    IDENTIFIER = "wbhuman_resources:absencerequesttyperepresentation"
    queryset = AbsenceRequestType.objects.all()
    serializer_class = AbsenceRequestTypeRepresentationSerializer


class AbsenceRequestCrossBorderCountryModelViewSet(viewsets.ModelViewSet):
    queryset = AbsenceRequestType.crossborder_countries.through.objects.all()
    serializer_class = AbsenceRequestCrossBorderCountryModelSerializer
    ordering = ordering_fields = search_fields = ["geography_repr"]

    endpoint_config_class = AbsenceRequestCrossBorderCountryEndpointConfig
    display_config_class = AbsenceRequestCrossBorderCountryDisplayConfig

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(absencerequesttype=self.kwargs["absencerequesttype_id"])
            .annotate(geography_repr=F("geography__name"))
            .select_related("geography")
        )


class AbsenceRequestModelViewSet(EmployeeViewMixin, viewsets.ModelViewSet):
    queryset = AbsenceRequest.objects.all()
    serializer_class = AbsenceRequestModelSerializer

    ordering_fields = [
        "employee__profile__computed_str",
        "period__startswith",
        "created",
        "_total_hours_in_days",
        "_total_vacation_hours_in_days",
    ]
    ordering = ["-period__startswith"]
    search_fields = ["employee__profile__computed_str", "notes", "reason"]

    filterset_class = AbsenceRequestFilter

    display_config_class = AbsenceRequestDisplayConfig
    endpoint_config_class = AbsenceRequestEndpointConfig
    button_config_class = AbsenceRequestButtonConfig

    @cached_property
    def can_administrate(self) -> bool:
        if "pk" in self.kwargs and (obj := self.get_object()):
            return can_validate_or_deny_request(obj, self.request.user)
        return False

    def get_serializer_class(self):
        if employee := getattr(self.request.user.profile, "human_resources", None):

            class Serializer(AbsenceRequestModelSerializer):
                period = wb_serializers.DateTimeRangeField(
                    default_timezone=employee.calendar.timezone,
                    default=CurrentUserDefaultPeriodDateTimeRange(),
                    lower_time_choices=get_lower_time_choices,
                    upper_time_choices=get_upper_time_choices,
                )

            return Serializer
        return AbsenceRequestModelSerializer

    def add_messages(
        self,
        request,
        queryset=None,
        paginated_queryset=None,
        instance=None,
        initial=False,
    ):
        if instance:
            if instance.status != AbsenceRequest.Status.CANCELLED:
                qs = CalendarItem.objects.filter(
                    is_cancelled=False, period__overlap=instance.period, entities=instance.employee.profile
                ).exclude(id=instance.id)
                activities_title = qs.values_list("title", flat=True)
                if len(activities_title) > 0:
                    message = _("<p>During this absence, you already have these events:</p><ul>")
                    for activity_title in activities_title:
                        message += f"<li>{activity_title}</li>"
                    message += "</ul>"
                    warning(request, message)
            if instance.type.is_vacation:
                if instance.status in [
                    AbsenceRequest.Status.DRAFT,
                    AbsenceRequest.Status.PENDING,
                ]:
                    other_pending_hours = (
                        AbsenceRequestPeriods.objects.exclude(request__id=instance.id)
                        .filter(
                            request__status__in=[AbsenceRequest.Status.PENDING, AbsenceRequest.Status.DRAFT],
                            request__type__is_vacation=True,
                            employee=instance.employee,
                        )
                        .aggregate(s=Sum("_total_hours"))["s"]
                        or 0.0
                    )

                    current_balance = instance.employee.get_or_create_balance(instance.period.lower.year)[0]
                    available_hourly_balance = current_balance.total_vacation_hourly_balance - instance.total_hours
                    available_hourly_balance_in_days = (
                        available_hourly_balance / instance.employee.calendar.get_daily_hours()
                    )
                    message = _(
                        "After this request, you will have {} days ({} hours) left for the balance {}</b>"
                    ).format(available_hourly_balance_in_days, available_hourly_balance, current_balance.year)
                    if other_pending_hours > 0:
                        message += _(
                            " (not including <b>{pending_hours}</b> hours from other pending/draft absence requests)"
                        ).format(pending_hours=other_pending_hours)
                    if available_hourly_balance < 0:
                        warning(request, message, extra_tags="auto_close=0")
                    else:
                        info(request, message)
                day_offs = instance.employee.calendar.days_off.filter(
                    date__gte=instance.period.lower.date(), date__lte=instance.period.upper.date()
                )
                if day_offs:
                    day_offs_messages = [
                        _("{holiday} not counted ({title})").format(
                            holiday=holiday.date.strftime("%d.%m.%Y"), title=holiday.title
                        )
                        for holiday in day_offs
                    ]
                    info(request, ", ".join(day_offs_messages))

    def get_queryset(self):
        qs = AbsenceRequest.objects.none()
        if self.is_administrator:
            qs = super().get_queryset()
        elif employee := getattr(self.request.user.profile, "human_resources", None):
            qs = super().get_queryset().filter(employee__in=employee.get_managed_employees())
        when_statements = []
        for type in AbsenceRequestType.objects.all():
            try:
                when_statements.append(When(type=type, then=Value(WBIcon[type.icon].icon)))
            except KeyError:
                when_statements.append(When(type=type, then=Value(type.icon)))

        qs = qs.annotate(
            department=F("employee__position__id"), type_icon=Case(*when_statements, default=Value(None))
        ).select_related(
            "type",
            "employee",
        )
        return qs

    def get_aggregates(self, queryset, paginated_queryset):
        current_year = timezone.now().year

        qs = AbsenceRequestPeriods.objects.filter(request__in=queryset, date__year=current_year)

        qs_vacation = qs.filter(
            Q(request__type__is_vacation=True) & Q(request__status=AbsenceRequest.Status.APPROVED.name)
        )
        return {
            "_total_hours_in_days": {
                "Σ": format_number(queryset.aggregate(s=Sum(F("_total_hours_in_days")))["s"]),
                f"Σ {current_year}": format_number(qs.aggregate(s=Sum(F("_total_hours")))["s"]),
            },
            "_total_vacation_hours_in_days": {
                "Σ": format_number(queryset.aggregate(s=Sum(F("_total_vacation_hours_in_days")))["s"]),
                f"Σ {current_year}": format_number(qs_vacation.aggregate(s=Sum(F("_total_hours")))["s"]),
            },
        }

    @action(detail=True, methods=["PATCH"])
    def increaseday(self, request, pk=None):
        absence_request = get_object_or_404(AbsenceRequest, id=pk)
        if absence_request.type.is_extensible and (number_days := int(request.POST.get("number_days", 1))):
            for i in range(number_days):
                if next_extensible_period := absence_request.next_extensible_period:
                    absence_request.period = next_extensible_period
            absence_request.save()
        return Response({"send": True})


class AbsenceRequestTypeModelViewSet(viewsets.ModelViewSet):
    IDENTIFIER = "wbhuman_resources:absencerequesttype"
    queryset = AbsenceRequestType.objects.all()
    serializer_class = AbsenceRequestTypeModelSerializer
    display_config_class = AbsenceRequestTypeDisplayConfig


# Employee Subs Viewsets ####


class AbsenceTypeCountEmployeeModelViewSet(viewsets.ModelViewSet):
    READ_ONLY = True
    queryset = AbsenceRequestPeriods.objects.all()
    serializer_class = EmployeeAbsenceDaysModelSerializer

    filter_backends = (filters.OrderingFilter, DjangoFilterBackend)
    ordering_fields = ["year", "hours_count", "day_count"]
    ordering = ["-year"]

    filterset_class = AbsenceTypeCountEmployeeModelFilterSet
    title_config_class = AbsenceTypeCountEmployeeTitleConfig
    display_config_class = AbsenceTypeCountEmployeeDisplayConfig
    endpoint_config_class = AbsenceTypeCountEmployeeEndpointConfig

    def get_queryset(self):
        employee = get_object_or_404(EmployeeHumanResource, pk=self.kwargs["employee_id"])
        employee_daily_hours = employee.calendar.get_daily_hours()
        qs = (
            AbsenceRequestPeriods.objects.filter(
                request__employee=employee,
                request__status=AbsenceRequest.Status.APPROVED.name,
            )
            .annotate(
                year=Extract("date", "year"),
                absence_type=F("request__type__id"),
            )
            .values("year", "absence_type")
            .annotate(
                hours_count=Sum("_total_hours"),
                days_count=F("hours_count") / Value(employee_daily_hours),
                id=Concat(
                    Value(self.kwargs["employee_id"]),
                    F("year"),
                    Value("."),
                    F("absence_type"),
                    output_field=CharField(),
                ),
            )
        )
        return qs

    def get_aggregates(self, queryset, paginated_queryset):
        return {
            "days_count": {
                "Σ": format_number(queryset.aggregate(s=Sum(F("days_count")))["s"], decimal=1),
            },
            "hours_count": {
                "Σ": format_number(queryset.aggregate(s=Sum(F("hours_count")))["s"], decimal=1),
            },
        }


class AbsenceRequestEmployeeHumanResourceModelViewset(AbsenceRequestModelViewSet):
    title_config_class = AbsenceRequestEmployeeBalanceTitleConfig
    display_config_class = AbsenceRequestEmployeeHumanResourceDisplayConfig
    endpoint_config_class = AbsenceRequestEmployeeHumanResourceEndpointConfig
    filterset_class = AbsenceRequestEmployeeHumanResourceFilterSet

    ordering = ["-period__startswith"]

    def get_queryset(self):
        employee = EmployeeHumanResource.objects.get(id=self.kwargs["employee_id"])
        return super().get_queryset().filter(employee=employee)


class AbsenceRequestPeriodsAbsenceRequestModelViewSet(viewsets.ModelViewSet):
    display_config_class = AbsenceRequestPeriodsAbsenceRequestDisplayConfig
    endpoint_config_class = AbsenceRequestPeriodsAbsenceRequestEndpointConfig
    queryset = AbsenceRequestPeriods.objects.all()
    serializer_class = AbsenceRequestPeriodsModelSerializer

    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ["date"]
    ordering = ["date"]

    def get_queryset(self):
        return super().get_queryset().filter(request__id=self.kwargs["request_id"])
