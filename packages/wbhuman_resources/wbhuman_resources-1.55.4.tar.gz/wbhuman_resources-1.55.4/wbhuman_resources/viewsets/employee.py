from django.db.models import F, OuterRef, Subquery
from rest_framework.decorators import action
from rest_framework.response import Response
from wbcore import viewsets
from wbcore.contrib.directory.models import Person
from wbcore.utils.date import current_month_date_end

from wbhuman_resources.filters import (
    EmployeeBalanceFilterSet,
    EmployeeFilterSet,
    PositionFilterSet,
)
from wbhuman_resources.models import (
    EmployeeHumanResource,
    EmployeeWeeklyOffPeriods,
    EmployeeYearBalance,
    Position,
    deactivate_profile_as_task,
)
from wbhuman_resources.serializers import (
    EmployeeBalanceModelSerializer,
    EmployeeHumanResourceRepresentationSerializer,
    EmployeeModelSerializer,
    EmployeeWeeklyOffPeriodsModelSerializer,
    EmployeeYearBalanceModelSerializer,
    EmployeeYearBalanceRepresentationSerializer,
    PositionModelSerializer,
    PositionRepresentationSerializer,
)
from wbhuman_resources.viewsets.buttons import (
    EmployeeButtonConfig,
    YearBalanceEmployeeHumanResourceButtonConfig,
)
from wbhuman_resources.viewsets.display import (
    EmployeeBalanceDisplayConfig,
    EmployeeDisplayConfig,
    PositionDisplayConfig,
    WeeklyOffPeriodEmployeeHumanResourceDisplayConfig,
    YearBalanceEmployeeHumanResourceDisplayConfig,
)
from wbhuman_resources.viewsets.endpoints import (
    EmployeeBalanceEndpointConfig,
    WeeklyOffPeriodEmployeeHumanResourceEndpointConfig,
    YearBalanceEmployeeHumanResourceEndpointConfig,
)
from wbhuman_resources.viewsets.titles import (
    EmployeeBalanceTitleConfig,
    EmployeeTitleConfig,
)

from .mixins import EmployeeViewMixin


class PositionRepresentationViewSet(viewsets.RepresentationViewSet):
    ordering_fields = ordering = ("name",)
    search_fields = ("name",)
    filterset_fields = {"height": ["exact"], "level": ["exact"]}
    queryset = Position.objects.all()
    serializer_class = PositionRepresentationSerializer


class EmployeeHumanResourceRepresentationViewSet(viewsets.RepresentationViewSet):
    ordering_fields = ordering = ("profile__computed_str",)
    search_fields = ("profile__computed_str",)

    queryset = EmployeeHumanResource.active_employees.select_related("profile")
    serializer_class = EmployeeHumanResourceRepresentationSerializer


class EmployeeYearBalanceRepresentationViewSet(viewsets.RepresentationViewSet):
    ordering_fields = ordering = "-year"

    queryset = EmployeeYearBalance.objects.all()
    serializer_class = EmployeeYearBalanceRepresentationSerializer


class PositionModelViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.select_related(
        "parent",
        "manager",
    )
    serializer_class = PositionModelSerializer

    filterset_class = PositionFilterSet
    ordering_fields = ordering = ["name"]
    search_fields = ["name"]

    display_config_class = PositionDisplayConfig


class EmployeeBalanceModelViewSet(EmployeeViewMixin, viewsets.ModelViewSet):
    queryset = EmployeeHumanResource.objects.all()
    serializer_class = EmployeeBalanceModelSerializer

    filterset_class = EmployeeBalanceFilterSet
    ordering_fields = [
        "profile__computed_str",
        "contract_type",
        "is_active",
        "position__name",
        "extra_days_frequency",
        "extra_days_per_period",
        "took_long_vacations",
        "available_vacation_balance_previous_year",
        "available_vacation_balance_current_year",
        "available_vacation_balance_next_year",
    ]
    ordering = ["profile__computed_str"]
    search_fields = ["profile__computed_str"]

    title_config_class = EmployeeBalanceTitleConfig
    display_config_class = EmployeeBalanceDisplayConfig
    endpoint_config_class = EmployeeBalanceEndpointConfig

    def get_queryset(self):
        qs = EmployeeHumanResource.objects.none()
        if self.is_administrator:
            qs = super().get_queryset()
        if employee := getattr(self.request.user.profile, "human_resources", None):
            qs = employee.get_managed_employees()
        return (
            EmployeeHumanResource.annotated_queryset(qs, current_month_date_end())
            .filter(balances__isnull=False)
            .distinct()
        ).select_related(
            "profile",
            "position",
            "calendar",
        )


class EmployeeModelViewSet(EmployeeViewMixin, viewsets.ModelViewSet):
    queryset = EmployeeHumanResource.objects.all()
    serializer_class = EmployeeModelSerializer

    ordering_fields = [
        "profile__computed_str",
        "position__name",
        "top_position_repr",
        "primary_telephone",
        "primary_email",
        "primary_address",
    ]
    ordering = ["profile__computed_str"]
    search_fields = ["profile__computed_str", "primary_telephone", "primary_email", "primary_address"]

    filterset_class = EmployeeFilterSet

    title_config_class = EmployeeTitleConfig
    display_config_class = EmployeeDisplayConfig
    button_config_class = EmployeeButtonConfig

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(
                top_position_repr=F("position__parent__name"),
                position_manager=F("position__manager"),
                primary_email=Subquery(
                    Person.objects.filter(id=OuterRef("profile")).annotate_all().values("primary_email")[:1]
                ),
                primary_address=Subquery(
                    Person.objects.filter(id=OuterRef("profile")).annotate_all().values("primary_address")[:1]
                ),
                primary_telephone=Subquery(
                    Person.objects.filter(id=OuterRef("profile")).annotate_all().values("primary_telephone")[:1]
                ),
            )
            .select_related(
                "direct_manager",
                "position",
                "calendar",
                "profile",
            )
            .prefetch_related("balances", "position__manager")
        )

    @action(detail=True, methods=["PATCH"])
    def deactivate(self, request, pk=None):
        if pk and EmployeeHumanResource.is_administrator(self.request.user):
            deactivate_profile_as_task.delay(request.user.id, pk, request.POST.get("substitute", None))
        return Response({"send": True})


# Employee Subs Viewsets


class WeeklyOffPeriodEmployeeHumanResourceModelViewSet(viewsets.ModelViewSet):
    display_config_class = WeeklyOffPeriodEmployeeHumanResourceDisplayConfig
    endpoint_config_class = WeeklyOffPeriodEmployeeHumanResourceEndpointConfig

    serializer_class = EmployeeWeeklyOffPeriodsModelSerializer
    queryset = EmployeeWeeklyOffPeriods.objects.all()

    def get_queryset(self):
        return super().get_queryset().filter(employee=self.kwargs["employee_id"])


class YearBalanceEmployeeHumanResourceModelViewset(viewsets.ModelViewSet):
    display_config_class = YearBalanceEmployeeHumanResourceDisplayConfig
    endpoint_config_class = YearBalanceEmployeeHumanResourceEndpointConfig
    button_config_class = YearBalanceEmployeeHumanResourceButtonConfig

    ordering = ["-year"]
    serializer_class = EmployeeYearBalanceModelSerializer
    queryset = EmployeeYearBalance.objects.all()

    def get_queryset(self):
        return super().get_queryset().filter(employee=self.kwargs["employee_id"])
