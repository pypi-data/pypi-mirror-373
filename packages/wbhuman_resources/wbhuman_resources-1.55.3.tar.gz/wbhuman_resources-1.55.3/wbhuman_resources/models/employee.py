import math
import operator
from datetime import date, datetime, timedelta
from functools import reduce
from typing import Generator, List, Optional, Tuple, Type, TypeVar

import pandas as pd
from celery import shared_task
from colorfield.fields import ColorField
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import (
    Case,
    Count,
    Exists,
    ExpressionWrapper,
    F,
    OuterRef,
    Q,
    QuerySet,
    Subquery,
    Sum,
    Value,
    When,
)
from django.db.models.fields import FloatField
from django.db.models.functions import Ceil, Coalesce
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.db.utils import ProgrammingError
from django.dispatch import receiver
from django.utils.timezone import make_naive
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from dynamic_preferences.registries import global_preferences_registry
from mptt.models import MPTTModel, TreeForeignKey
from psycopg.types.range import TimestamptzRange
from wbcore.contrib.directory.models import (
    Company,
    EmployerEmployeeRelationship,
    Person,
)
from wbcore.contrib.directory.models import Position as CRMPosition
from wbcore.contrib.directory.signals import deactivate_profile
from wbcore.contrib.notifications.dispatch import send_notification
from wbcore.contrib.notifications.utils import create_notification_type
from wbcore.models import WBModel
from wbcore.models.fields import YearField
from wbcore.utils.models import ComplexToStringMixin

from .absence import AbsenceRequest, AbsenceRequestPeriods
from .calendars import DayOff, DayOffCalendar, DefaultDailyPeriod
from .preferences import (
    default_vacation_days_per_year,
    get_is_external_considered_as_internal,
    get_main_company,
    get_previous_year_balance_expiration_date,
    long_vacation_number_of_days,
)

User = get_user_model()


class ActiveEmployeeManager(models.Manager):
    """Custom Manager for filtering directly Active Employees. Exclude objects without reverse related field user_account and profile"""

    def __init__(self, only_internal=False, **kwargs):
        self.only_internal = only_internal
        super().__init__(**kwargs)

    def get_queryset(self) -> "models.QuerySet[EmployeeHumanResource]":
        contract_type_condition = (
            Q(contract_type=EmployeeHumanResource.ContractType.INTERNAL)
            if (self.only_internal and not get_is_external_considered_as_internal())
            else Q(contract_type__isnull=False)
        )
        return (
            super()
            .get_queryset()
            .filter(
                Q(is_active=True)
                & Q(profile__isnull=False)
                & Q(profile__user_account__isnull=False)
                & contract_type_condition
            )
        )


SelfEmployeeHumanResource = TypeVar("SelfEmployeeHumanResource", bound="EmployeeHumanResource")


class EmployeeHumanResource(ComplexToStringMixin, WBModel):
    """
    Stores a single Employee entry, related to :model:`directory.Person`.
    """

    class ContractType(models.TextChoices):
        INTERNAL = "INTERNAL", _("Internal")
        EXTERNAL = "EXTERNAL", _("External")

    class ExtraDaysBalanceFrequency(models.TextChoices):
        MONTHLY = "MONTHLY", _("Monthly")
        YEARLY = "YEARLY", _("Yearly")

        def get_pandas_frequency(self) -> str:
            """
            Return the pandas frequency representation of this frequency
            """
            if self.value == self.MONTHLY:
                return "M"
            if self.value == self.YEARLY:
                return "Y"

        def get_date_range(self, _d: datetime) -> tuple[datetime, datetime]:
            """
            Return a tuple of datetime range representing this frequency
            """
            if self.value == self.MONTHLY:
                return ((_d - pd.tseries.offsets.MonthBegin(1)).to_pydatetime(), _d)
            if self.value == self.YEARLY:
                return (
                    (_d - pd.tseries.offsets.YearEnd(1)).to_pydatetime() + timedelta(days=1),
                    (_d + pd.tseries.offsets.YearBegin(1)).to_pydatetime() - timedelta(days=1),
                )

        def get_yearly_periods_count(self) -> int:
            """
            Return the number of yearly periods defined by this frequency
            """
            if self.value == self.MONTHLY:
                return 12
            if self.value == self.YEARLY:
                return 1

        def get_period_index(self, _d: datetime) -> int:
            """
            Get the period index
            """
            if self.value == self.MONTHLY:
                return _d.month
            if self.value == self.YEARLY:
                return 1

    profile = models.OneToOneField(
        "directory.Person",
        related_name="human_resources",
        on_delete=models.CASCADE,
        verbose_name=_("Employee"),
        help_text=_("The CRM profile related to this employee"),
    )
    is_active = models.BooleanField(
        verbose_name=_("Is active"),
        help_text=_(
            "If false, the employee will be considered as not active but his absence requests will be preserved"
        ),
        default=True,
    )
    extra_days_frequency = models.CharField(
        max_length=16,
        default=ExtraDaysBalanceFrequency.YEARLY,
        choices=ExtraDaysBalanceFrequency.choices,
        verbose_name=_("Extra Days Frequency"),
        help_text=_(
            "The frequency at which an additional number of vacation days is enabled for this employee (defaults to yearly)"
        ),
    )

    occupancy_rate = models.FloatField(
        verbose_name=_("Occupation Rate"),
        help_text=_("The occupation rate in percent, 100% being employed fulltime"),
        default=1,
    )

    contract_type = models.CharField(
        max_length=16,
        default=ContractType.INTERNAL,
        choices=ContractType.choices,
        verbose_name=_("Employee Type"),
        help_text=_(
            "If Internal, the employee is considered a full-time employee and thus has employee access to the system."
        ),
    )
    position = models.ForeignKey(
        "wbhuman_resources.Position",
        related_name="employees",
        on_delete=models.SET_NULL,
        verbose_name=_("Position"),
        limit_choices_to=models.Q(height=0),
        null=True,
        blank=True,
        help_text=_("The position this employee belongs to"),
    )
    direct_manager = models.ForeignKey(
        "directory.Person",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Direct Manager"),
        related_name="managed_employees",
    )
    calendar = models.ForeignKey(
        to="wbhuman_resources.DayOffCalendar",
        related_name="employees",
        on_delete=models.PROTECT,
    )
    weekly_off_periods = models.ManyToManyField(
        to="wbhuman_resources.DefaultDailyPeriod",
        through="wbhuman_resources.EmployeeWeeklyOffPeriods",
        through_fields=("employee", "period"),
        related_name="employees_off",
        verbose_name=_("Weekly off periods"),
    )
    objects = models.Manager()
    active_internal_employees = ActiveEmployeeManager(only_internal=True)
    active_employees = ActiveEmployeeManager()

    enrollment_at = models.DateField(verbose_name=_("Enrolled at"))
    disenrollment_at = models.DateField(verbose_name="Disenroll at", blank=True, null=True)

    class Meta:
        verbose_name = _("Employee Human Resource")
        verbose_name_plural = _("Employee Human Resources")
        permissions = [("administrate_employeehumanresource", "Can administrate Employee Human Resource")]
        notification_types = [
            create_notification_type(
                code="wbhuman_resources.employeehumanresource.deactivate",
                title="Deactivate Employee Notification",
                help_text="Notify the requester when an employee has been successfully deactivated",
            ),
            create_notification_type(
                code="wbhuman_resources.employeehumanresource.vacation",
                title="Vacation Notification",
                help_text="Notifies you when there are Vacation days that you still have to take",
            ),
            create_notification_type(
                code="wbhuman_resources.employeehumanresource.birthday",
                title="Birthday Notification",
                help_text="Notifies you when today one of your colleagues is celebrating their birthday",
            ),
        ]

    def unassign_position_groups(self):
        """
        Un-assign the employee to the belonged human resource groups
        """
        if (user := getattr(self.profile, "user_account", None)) and self.position:
            for position in self.position.get_ancestors(include_self=True):
                for group in position.groups.all():
                    user.groups.remove(group)

    def assign_position_groups(self):
        """
        Assign the employee to the position permission group
        """
        if (user := getattr(self.profile, "user_account", None)) and self.position:
            for position in self.position.get_ancestors(include_self=True):
                for group in position.groups.difference(user.groups.all()):
                    user.groups.add(group)

    def deactivate(
        self, substitute: Optional[models.Model] = None, disenrollment_date: date | None = None
    ) -> List[str]:
        """
        Utility method to deactivate/disenroll an employee

        Trigger a signal "deactivate_profile" that every module can implement in order to define module level business logic for employee disenrollment.

        Args:
            substitute:
            disenrollment_date:

        Returns:
            A list of message feedback received from the potential receivers
        """
        if not disenrollment_date:
            disenrollment_date = date.today()
        # send signal to deactivate employee
        self.disenrollment_at = disenrollment_date
        res = deactivate_profile.send(self.__class__, instance=self.profile, substitute_profile=substitute)

        self.is_active = False
        self.save()
        self.profile.user_account.is_active = False
        self.profile.user_account.save()
        self.assign_vacation_allowance_from_range(
            self.enrollment_at, self.disenrollment_at
        )  # recompute and close possible open balance
        try:
            main_company = Company.objects.get(id=get_main_company())
            self.profile.employers.remove(main_company)
        except Company.DoesNotExist:
            pass
        return [msg for _, msg in res]

    def get_managed_employees(self, include_self: bool | None = True) -> "QuerySet[SelfEmployeeHumanResource]":
        """
        Returns all the direct managed employees, from the current position and all its descendants
        Args:
            include_self: Set to False if the returned queryset needs to exclude the employee. Default to False

        Returns:
            A queryset of EmployeeHumanResources
        """
        if (user := self.profile.user_account) and user.has_perm("wbhuman_resources.administrate_absencerequest"):
            qs = EmployeeHumanResource.active_employees.all()
        else:
            conditions = [Q(direct_manager=self.profile), Q(id=self.id)] + [
                Q(position__in=position.get_descendants(include_self=True))
                for position in self.profile.managed_positions.all()
            ]
            qs = EmployeeHumanResource.active_employees.filter(reduce(operator.or_, conditions))
        if not include_self:
            qs = qs.exclude(id=self.id)
        return qs.distinct()

    def get_managers(self, only_direct_manager: bool = False) -> Generator[SelfEmployeeHumanResource, None, None]:
        """
        Returns the direct manager of this employee and the potential global manager. Prioritize the direct manager, and if not available, the next position manager in the company hierarchy

        Returns:
            A generator yielding managers
        """
        if direct_manager := self.direct_manager:
            yield direct_manager
        elif main_position := self.position:
            if (
                next_position_with_manager := main_position.get_ancestors(ascending=True, include_self=True)
                .filter(manager__isnull=False)
                .first()
            ):
                yield next_position_with_manager.manager
        if not only_direct_manager:
            global_manager_permission = Permission.objects.get(
                codename="administrate_employeehumanresource", content_type=ContentType.objects.get_for_model(self)
            )
            for global_manager_user in global_manager_permission.user_set.filter(profile__isnull=False):
                yield global_manager_user.profile

    def is_manager_of(self, administree: SelfEmployeeHumanResource, include_self: bool = False) -> bool:
        """
        Return true if self is the manager of administree
        Args:
            administree: The employee to check hierarchy against

        Returns:
            A boolean
        """
        return self.get_managed_employees(include_self=include_self).filter(id=administree.id).exists()

    def compute_str(self) -> str:
        return f"{self.profile.first_name} {self.profile.last_name}"

    def __str__(self) -> str:
        return self.computed_str

    def save(self, *args, **kwargs):
        if not self.calendar:
            self.calendar = global_preferences_registry.manager()["wbhuman_resources__employee_default_calendar"]
        if not self.enrollment_at:
            self.enrollment_at = date.today()
        super().save(*args, **kwargs)

    def extract_workable_periods(
        self, start: datetime, end: datetime, count: int = None
    ) -> Generator[Tuple[datetime, datetime, DefaultDailyPeriod], None, None]:
        """
        Utility function that returns the day off for an employee, including the calendar day off and the possible weekly day off
        Args:
            start_date: lower bound range
            end_date:  upper bound range
            count: if specified, will stop the iteration at the specified index
        Returns:
            a list of datetime range representing each a period where the employee if off
        """
        cursor = start.date()
        index = 0
        while cursor <= end.date() and (not count or index < count):
            for period in self.calendar.default_periods.order_by("lower_time"):
                lower_datetime = period.get_lower_datetime(cursor)
                upper_datetime = period.get_upper_datetime(cursor)
                if (
                    lower_datetime >= start
                    and upper_datetime <= end
                    and not EmployeeWeeklyOffPeriods.objects.filter(
                        weekday=cursor.weekday(), period=period, employee=self
                    ).exists()
                    and not self.calendar.days_off.filter(date=cursor, count_as_holiday=True).exists()
                ):
                    yield cursor, period
                    index += 1
            cursor += timedelta(days=1)

    def assign_vacation_allowance_from_range(self, from_date: date, to_date: date):
        """
        Assign the proper monthly allowance from the given range if it doesn't yet exist.

        Assign partial allowance if the date range don't span a full period. Check also if the given range don't over span the enrollment and disenrollment employee's date

        Args:
            from_date: start date range
            to_date: end date range
        """
        from_date = max(self.enrollment_at, from_date)
        if self.disenrollment_at:
            to_date = min(self.disenrollment_at, to_date)
        periods = self.calendar.default_periods.order_by("lower_time")
        if periods.exists():
            # Convert to datetime
            from_datetime = periods.first().get_lower_datetime(from_date)
            to_datetime = periods.last().get_upper_datetime(to_date)

            frequency = self.ExtraDaysBalanceFrequency[self.extra_days_frequency]

            period_base_allowance = (
                default_vacation_days_per_year()
                * self.calendar.get_daily_hours()
                / frequency.get_yearly_periods_count()
            )
            for _d in pd.date_range(from_datetime, to_datetime, freq=frequency.get_pandas_frequency()):
                current_year_balance = self.get_or_create_balance(_d.year)[0]
                [start_period, end_period] = frequency.get_date_range(_d)
                total_workable_periods_count = len(list(self.extract_workable_periods(start_period, end_period)))
                actual_workable_periods_count = len(
                    list(self.extract_workable_periods(max(start_period, from_datetime), min(end_period, to_datetime)))
                )
                if actual_workable_periods_count and total_workable_periods_count:
                    BalanceHourlyAllowance.objects.get_or_create(
                        balance=current_year_balance,
                        period_index=frequency.get_period_index(_d),
                        defaults={
                            "hourly_allowance": period_base_allowance
                            * actual_workable_periods_count
                            / total_workable_periods_count
                        },
                    )

    def get_or_create_balance(self, year: int) -> tuple["EmployeeYearBalance", bool]:
        """
        Wrapper around get_or_create

        Args:
            year: lookup year argument

        Returns:
            A tuple of EmployeeYearBalance and bool. Boolean is true if the balance was actually created.
        """
        return EmployeeYearBalance.objects.get_or_create(employee=self, year=year)

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbhuman_resources:employee"

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbhuman_resources:employeehumanresourcerepresentation-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{ computed_str }}"

    @classmethod
    def annotated_queryset(
        cls, qs: QuerySet[SelfEmployeeHumanResource], end_of_month: date
    ) -> QuerySet[SelfEmployeeHumanResource]:
        """
        Utility classmethod to annotate the employee queryset with a set of usage and balance statistics variables

        Args:
            qs: The queryset to annotate
            end_of_month: Date at which the absence periods will be exclude from the balance usage

        Returns:
            The annotated queryset
        """
        long_vacation_days = long_vacation_number_of_days()
        vacation_days_per_year = default_vacation_days_per_year()
        return qs.annotate(
            x1=Case(
                When(
                    extra_days_frequency=EmployeeHumanResource.ExtraDaysBalanceFrequency.YEARLY.name,
                    then=F("occupancy_rate") * vacation_days_per_year * 2,
                ),
                default=F("occupancy_rate") * vacation_days_per_year / 6,
                output_field=FloatField(),
            ),
            extra_days_per_period=Ceil("x1") / 2,
            daily_hours=Coalesce(
                Subquery(
                    DefaultDailyPeriod.objects.filter(calendar=OuterRef("calendar"))
                    .values("calendar")
                    .annotate(s=Sum("total_hours"))
                    .values("s")[:1]
                ),
                0.0,
            ),
            available_vacation_balance_previous_year=Coalesce(
                Subquery(
                    EmployeeYearBalance.objects.filter(employee=OuterRef("pk"), year=end_of_month.year - 1).values(
                        "actual_total_vacation_hourly_balance_in_days"
                    )[:1]
                ),
                0.0,
            ),
            available_vacation_balance_current_year=Coalesce(
                Subquery(
                    EmployeeYearBalance.objects.filter(employee=OuterRef("pk"), year=end_of_month.year).values(
                        "actual_total_vacation_hourly_balance_in_days"
                    )[:1]
                ),
                0.0,
            ),
            available_vacation_balance_next_year=Coalesce(
                Subquery(
                    EmployeeYearBalance.objects.filter(employee=OuterRef("pk"), year=end_of_month.year + 1).values(
                        "actual_total_vacation_hourly_balance_in_days"
                    )[:1]
                ),
                0.0,
            ),
            long_vacation_in_hours=Value(long_vacation_days) * F("daily_hours") * F("occupancy_rate"),
            took_long_vacations=Exists(
                AbsenceRequestPeriods.objects.filter(
                    consecutive_hours_count__gte=OuterRef("long_vacation_in_hours"),
                    request__employee__id=OuterRef("pk"),
                    request__status=AbsenceRequest.Status.APPROVED,
                    request__type__is_timeoff=True,
                    date__year=end_of_month.year,
                )
            ),
        )

    @classmethod
    def get_administrators(cls) -> QuerySet[User]:
        """
        Utility classmethod that returns the HR module administrators

        Returns:
            The administrator user accounts (as queryset)
        """
        return (
            get_user_model()
            .objects.filter(is_active=True, profile__isnull=False)
            .filter(
                Q(groups__permissions__codename="administrate_absencerequest")
                | Q(user_permissions__codename="administrate_absencerequest")
            )
            .distinct()
        )

    @classmethod
    def is_administrator(cls, user: "User") -> bool:
        """
        Check if the given user account has administrator privilege

        Args:
            user: User to check

        Returns:
            True if user is an administrator
        """
        return cls.get_administrators().filter(id=user.id).exists() or (user.is_superuser and user.is_active)

    @classmethod
    def get_employee_absence_periods_df(
        cls,
        calendar: "DayOffCalendar",
        start: date,
        end: date,
        employees: QuerySet[SelfEmployeeHumanResource],
        only_employee_with_absence_periods: bool = False,
    ) -> pd.DataFrame:
        """
        Utility function that gets the subsequent absence dataframe from absence periods, employee weekly off period and days off and concat
        a unique dataframe containing all the employees non working periods.

        Args:
            calendar: The calendar to use as base calendar
            start: The start filter
            end: The end filter
            employees: A queryset of employees to get the off periods from
            only_employee_with_absence_periods: True if we want to clean rows from employees without at least one absence request during that date range

        Returns:
                A dataframe whose columns are [employee, employee_repr, period, start, end, date, type, status]
        """
        periods_map = dict()

        def _get_timespan(period_id, val_date):
            if period_id not in periods_map:
                periods_map[period_id] = DefaultDailyPeriod.objects.get(id=period_id)
            period = periods_map[period_id]
            return (
                make_naive(period.get_lower_datetime(val_date), timezone=calendar.timezone),
                make_naive(period.get_upper_datetime(val_date), timezone=calendar.timezone),
            )

        df_periods = AbsenceRequestPeriods.get_periods_as_df(start, end, employee__in=employees)
        if only_employee_with_absence_periods:
            employees = employees.filter(id__in=df_periods.employee.unique())
        df_employee_weekly_off_periods = EmployeeWeeklyOffPeriods.get_employee_weekly_periods_df(
            start, end, employee__in=employees
        )
        df_day_offs = calendar.get_day_off_per_employee_df(start, end, employees)

        df = pd.concat(
            [df_periods, df_employee_weekly_off_periods, df_day_offs],
            axis=0,
            ignore_index=True,
        )

        df[["start", "end"]] = (
            df[["period", "date"]].apply(lambda x: _get_timespan(x["period"], x["date"]), axis=1).apply(pd.Series)
        )
        df["start"] = pd.to_datetime(df["start"])
        df["end"] = pd.to_datetime(df["end"])
        df["employee_repr"] = df.employee.map(dict(employees.values_list("id", "computed_str")))
        return df

    @classmethod
    def get_end_of_month_employee_balance_report_df(
        cls, active_employees: QuerySet[SelfEmployeeHumanResource], end_of_month: date, convert_in_days: bool = True
    ) -> pd.DataFrame:
        """
        A utility function that generate a statistics vacation usage dataframe for a list of employees.

        Args:
            active_employees: A queryset of employees
            end_of_month: The last date for periods to be used in the report
            convert_in_days: True if the resulting statistics needs to be converted into days from hours

        Returns:
            A dataframe with columns ["Employee", "Total Balance", "End of Month Usage", "Available Balance End of Month"
        """

        final_columns_name_mapping = {
            "employee": "Employee",
            "total_balance": "Total Balance",
            "current_year_usage": "End of Month Usage",
            "eod_remaining_absence_days": "Available Balance End of Month",
        }

        df_balances_current_year = (
            pd.DataFrame(
                EmployeeYearBalance.objects.get_queryset_at_date(to_date=end_of_month, today=end_of_month)
                .filter(year=end_of_month.year, employee__in=active_employees)
                .values("employee", "_balance", "_daily_hours")
            )
            .set_index("employee")
            .rename(columns={"_balance": "current_year_available_balance"})
        )
        df_balances_previous_year = (
            pd.DataFrame(
                EmployeeYearBalance.objects.get_queryset_at_date(to_date=end_of_month, today=end_of_month)
                .filter(year=end_of_month.year - 1, employee__in=active_employees)
                .values("employee", "_total_vacation_hourly_balance")
            )
            .set_index("employee")
            .rename(columns={"_total_vacation_hourly_balance": "previous_year_available_balance"})
        )

        df_usage_current_year = (
            pd.DataFrame(
                AbsenceRequestPeriods.vacation_objects.filter(
                    employee__in=active_employees, date__year=end_of_month.year, date__lte=end_of_month
                ).values("employee", "_total_hours")
            )
            .groupby("employee")
            .sum()
            .rename(columns={"_total_hours": "current_year_usage"})
        )
        df_usage_previous_year = (
            pd.DataFrame(
                EmployeeYearBalance.objects.get_queryset_at_date(
                    from_date=date(end_of_month.year, 1, 1), to_date=end_of_month, today=end_of_month
                )
                .filter(year=end_of_month.year - 1, employee__in=active_employees)
                .values("employee", "_total_vacation_hourly_usage")
            )
            .set_index("employee")
            .rename(columns={"_total_vacation_hourly_usage": "previous_year_usage"})
        )

        df = pd.concat(
            [df_balances_current_year, df_balances_previous_year, df_usage_current_year, df_usage_previous_year],
            axis=1,
        ).fillna(0)

        df["total_balance"] = (
            df.current_year_available_balance + df.previous_year_available_balance + df.previous_year_usage
        )
        df["eod_remaining_absence_days"] = df.total_balance - df.current_year_usage
        if convert_in_days:
            df[["total_balance", "current_year_usage", "eod_remaining_absence_days"]] = df[
                ["total_balance", "current_year_usage", "eod_remaining_absence_days"]
            ].divide(df["_daily_hours"], axis=0)
        df = df[df["total_balance"] != 0].reset_index()
        df.employee = df.employee.map(dict(active_employees.values_list("id", "computed_str")))

        df = df.rename(columns=final_columns_name_mapping)
        return df.drop(columns=df.columns.difference(final_columns_name_mapping.values()))


class EmployeeYearBalanceDefaultManager(models.Manager):
    def _annotate_queryset(
        self, qs, from_date: date | None = None, to_date: date | None = None, today: date | None = None
    ):
        """
        Intermediary private method to annotate the balance queryset with the usage variables

        Args:
            qs: Balance queryset
            from_date: Optional, All periods before this date will be excluded from the usage
            to_date: Optional, All periods after this date will be excluded from the usage
            today: Optional, Date at which the statisticis needs to be considered. Usefull particularly to define if the previous year balance available is usable.

        Returns:
            The annotated queryset
        """
        if not today:
            today = date.today()
        try:
            latest_date_for_last_year_vacation_availibility = get_previous_year_balance_expiration_date(today.year)
            base_periods = AbsenceRequestPeriods.vacation_objects.filter(balance=OuterRef("pk"))
            base_mandatory_days_off = DayOff.objects.filter(
                calendar=OuterRef("employee__calendar"), date__year=OuterRef("year"), count_as_holiday=False
            )
            if to_date:
                base_periods = base_periods.filter(date__lte=to_date)
                base_mandatory_days_off = base_mandatory_days_off.filter(date__lte=to_date)

            if from_date:
                base_periods = base_periods.filter(date__gte=from_date)
                base_mandatory_days_off = base_mandatory_days_off.filter(date__gte=from_date)
            return qs.annotate(
                _given_balance=ExpressionWrapper(
                    Coalesce(
                        Subquery(
                            BalanceHourlyAllowance.objects.filter(balance=OuterRef("pk"))
                            .values("balance")
                            .annotate(s=Sum("hourly_allowance"))
                            .values("s")[:1]
                        ),
                        0,
                    ),
                    output_field=FloatField(),
                ),
                _balance=F("extra_balance") + Ceil("_given_balance"),
                _daily_hours=Coalesce(
                    Subquery(
                        DefaultDailyPeriod.objects.filter(calendar=OuterRef("employee__calendar"))
                        .values("calendar")
                        .annotate(s=Sum("total_hours"))
                        .values("s")[:1]
                    ),
                    0.0,
                ),
                _number_mandatory_days_off_in_days=ExpressionWrapper(
                    Coalesce(Subquery(base_mandatory_days_off.annotate(c=Count("date__year")).values("c")[:1]), 0.0),
                    output_field=FloatField(),
                ),
                _number_mandatory_days_off=F("_number_mandatory_days_off_in_days") * F("_daily_hours"),
                _total_vacation_hourly_usage=Coalesce(
                    Subquery(base_periods.values("balance").annotate(s=Sum("_total_hours")).values("s")[:1]),
                    0.0,
                ),
                _total_vacation_hourly_balance=F("_balance")
                - F("_total_vacation_hourly_usage")
                - F("_number_mandatory_days_off"),
                today=Value(today),
                actual_total_vacation_hourly_balance=Case(
                    When(
                        Q(year__lt=today.year) & Q(today__gte=latest_date_for_last_year_vacation_availibility),
                        then=0.0,
                    ),
                    default=F("_total_vacation_hourly_balance"),
                ),
                _balance_in_days=Case(When(_daily_hours=0, then=None), default=F("_balance") / F("_daily_hours")),
                _total_vacation_hourly_usage_in_days=Case(
                    When(_daily_hours=0, then=None), default=F("_total_vacation_hourly_usage") / F("_daily_hours")
                ),
                _total_vacation_hourly_balance_in_days=Case(
                    When(_daily_hours=0, then=None), default=F("_total_vacation_hourly_balance") / F("_daily_hours")
                ),
                actual_total_vacation_hourly_balance_in_days=Case(
                    When(_daily_hours=0, then=None),
                    default=F("actual_total_vacation_hourly_balance") / F("_daily_hours"),
                ),
            )
        except ProgrammingError:
            return qs

    def get_queryset(self):
        """
        Default Manager queryset
        """
        return self._annotate_queryset(super().get_queryset())

    def get_queryset_at_date(
        self, from_date: date | None = None, to_date: date | None = None, today: date | None = None
    ):
        """
        Default Manager queryset
        """
        return self._annotate_queryset(super().get_queryset(), from_date=from_date, to_date=to_date, today=today)


class BalanceHourlyAllowance(models.Model):
    balance = models.ForeignKey(
        "wbhuman_resources.EmployeeYearBalance",
        on_delete=models.CASCADE,
        verbose_name="Balance",
        related_name="monthly_allowances",
    )
    period_index = models.PositiveIntegerField()
    hourly_allowance = models.FloatField()

    class Meta:
        verbose_name = _("Monthly Allowance")
        verbose_name_plural = _("Monthly Allowance")
        unique_together = ("balance", "period_index")
        indexes = [
            models.Index(fields=["balance"]),
            models.Index(fields=["balance", "period_index"]),
        ]


class EmployeeYearBalance(ComplexToStringMixin, models.Model):
    employee = models.ForeignKey(
        EmployeeHumanResource,
        related_name="balances",
        on_delete=models.CASCADE,
        verbose_name=_("Employee"),
        help_text=_("The employee having that year balance"),
    )
    year = YearField(verbose_name=_("Year"))
    extra_balance = models.FloatField(
        default=0,
        verbose_name=_("Extra Balance (in hours)"),
        help_text=_("The yearly extra balance (in hours)"),
    )

    objects = EmployeeYearBalanceDefaultManager()

    def compute_str(self):
        return "Balance {}: {}".format(self.year, self.employee)

    class Meta:
        verbose_name = _("Employee Year Balance")
        verbose_name_plural = _("Employee Year Balances")
        unique_together = ("employee", "year")
        indexes = [
            models.Index(fields=["employee", "year"]),
        ]

    @property
    @admin.display(description="Yearly allowance (in hours)")
    def balance(self) -> float:
        given_balance = self.monthly_allowances.aggregate(s=Sum("hourly_allowance"))["s"] or 0.0
        return getattr(self, "_balance", math.ceil(given_balance) + self.extra_balance)

    @property
    @admin.display(description="Daily hours")
    def daily_hours(self) -> float:
        return getattr(self, "_daily_hours", self.employee.calendar.get_daily_hours())

    @property
    @admin.display(description="Mandatory days off (In days)")
    def number_mandatory_days_off_in_days(self) -> float:
        return getattr(
            self,
            "_number_mandatory_days_off",
            self.employee.calendar.days_off.filter(date__year=self.year, count_as_holiday=False).count(),
        )

    @property
    @admin.display(description="Mandatory Hours off")
    def number_mandatory_days_off(self) -> float:
        return getattr(
            self, "_number_mandatory_days_off_in_days", self.number_mandatory_days_off_in_days * self.daily_hours
        )

    @property
    @admin.display(description="Total vacation hourly usage")
    def total_vacation_hourly_usage(self) -> float:
        return getattr(
            self,
            "_total_vacation_hourly_usage",
            self.periods.filter(
                request__type__is_vacation=True, request__status=AbsenceRequest.Status.APPROVED
            ).aggregate(s=Sum("_total_hours"))["s"]
            or 0.0,
        )

    @property
    @admin.display(description="Total available yearly balance")
    def total_vacation_hourly_balance(self) -> float:
        return getattr(
            self,
            "_total_vacation_hourly_balance",
            self.balance - self.total_vacation_hourly_usage - self.number_mandatory_days_off,
        )

    @property
    @admin.display(description="Yearly allowance (in days)")
    def balance_in_days(self) -> float:
        return getattr(self, "_balance_in_days", self.balance / self.daily_hours)

    @property
    @admin.display(description="Total vacation hourly usage (in days)")
    def total_vacation_hourly_usage_in_days(self) -> float:
        return getattr(
            self, "_total_vacation_hourly_usage_in_days", self.total_vacation_hourly_usage / self.daily_hours
        )

    @property
    @admin.display(description="Total available yearly balance (in days)")
    def total_vacation_hourly_balance_in_days(self) -> float:
        return getattr(
            self, "_total_vacation_hourly_balance_in_days", self.total_vacation_hourly_balance / self.daily_hours
        )

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbhuman_resources:employeeyearbalancerepresentation-list"


class EmployeeWeeklyOffPeriods(ComplexToStringMixin, models.Model):
    employee = models.ForeignKey(
        "wbhuman_resources.EmployeeHumanResource",
        related_name="default_periods_relationships",
        on_delete=models.CASCADE,
        verbose_name=_("Employee"),
    )

    period = models.ForeignKey(
        "wbhuman_resources.DefaultDailyPeriod",
        related_name="employees_relationships",
        on_delete=models.CASCADE,
        verbose_name=_("Off Period"),
    )
    weekday = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(6)]
    )  # Valid weekday from python convention (e.g. Monday is 0)

    def compute_str(self) -> str:
        return "{} off on the {} in {}".format(
            self.employee.profile.full_name, self.period.title, date(1, 1, self.weekday + 1).strftime("%A")
        )

    def get_timespan(self, val_date: date) -> TimestamptzRange:
        """
        Get the combined datetime range for this employee weekly off period given a date

        Args:
            val_date: A date

        Returns:
            The datetime range spanning this periods on that valuation date
        """
        return TimestamptzRange(
            lower=self.period.get_lower_datetime(val_date), upper=self.period.get_upper_datetime(val_date)
        )

    class Meta:
        verbose_name = _("Employee Weekly off Period")
        verbose_name_plural = _("Employee Weekly off Periods")
        unique_together = ("employee", "period", "weekday")
        indexes = [
            models.Index(fields=["employee", "period", "weekday"]),
        ]

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbhuman_resources:employeeweeklyoffperiodrepresentation-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_employee_weekly_periods_df(cls, start: date, end: date, **extra_filter_kwargs) -> pd.DataFrame:
        """
        This utility function provides a way to duplicate the employee weekly off periods into a timeserie of absence request whose type is "Day Off" and status is "APPROVED"
        Args:
            start: The beginning of the time period
            end: The end of the time period
            **extra_filter_kwargs: extra filter argument as dictionary to filter down the list of Employee weekly periods (usually to filter out employees)

        Returns:
            A dataframe whose columns is ["status", "type", "employee", "period", "date"]
        """
        df_periods_off = pd.DataFrame(
            EmployeeWeeklyOffPeriods.objects.filter(**extra_filter_kwargs).values("employee", "period", "weekday"),
            columns=["employee", "period", "weekday"],
        )
        df_periods_off = df_periods_off.merge(
            pd.date_range(start, end, freq="W").to_series(name="sunday"), how="cross"
        )
        df_periods_off["date"] = df_periods_off["sunday"] - pd.TimedeltaIndex(6 - df_periods_off["weekday"], unit="D")
        df_periods_off.date = df_periods_off.date.dt.date
        del df_periods_off["weekday"]
        del df_periods_off["sunday"]
        df_periods_off["status"] = AbsenceRequest.Status.APPROVED.value
        df_periods_off["type"] = "Day Off"
        return df_periods_off


class Position(ComplexToStringMixin, WBModel, MPTTModel):
    color = ColorField(default="#FF0000")
    name = models.CharField(max_length=256)
    parent = TreeForeignKey(
        "wbhuman_resources.Position",
        related_name="children",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name=_("Parent Positions"),
    )
    groups = models.ManyToManyField(Group, related_name="human_resources_positions", blank=True)
    height = models.IntegerField(default=0)
    manager = models.ForeignKey(
        "directory.Person",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Department Manager"),
        related_name="managed_positions",
    )

    class Meta:
        verbose_name = _("Position")
        verbose_name_plural = _("Positions")

    def compute_str(self) -> str:
        if self.parent and self.parent.computed_str:
            return f"{self.name} ({self.parent.computed_str})"
        return f"{self.name}"

    def save(self, *args, **kwargs):
        self.computed_str = self.compute_str()
        super().save(*args, **kwargs)

    def get_employees(self) -> QuerySet[EmployeeHumanResource]:
        """
        Get the queryset of employees that are within this position hierarchy

        Returns:
            A queryset of employees
        """
        return EmployeeHumanResource.objects.filter(
            is_active=True, position__in=self.get_descendants(include_self=True)
        )

    # @classmethod
    # def to_graph(cls):
    #     nr_vertices = 25
    #     v_label = list(map(str, range(nr_vertices)))
    #     G = Graph.Tree(nr_vertices, 2)  # 2 stands for children number
    #     lay = G.layout('rt')
    #
    #     position = {k: lay[k] for k in range(nr_vertices)}
    #     Y = [lay[k][1] for k in range(nr_vertices)]
    #     M = max(Y)
    #
    #     es = EdgeSeq(G)  # sequence of edges
    #     E = [e.tuple for e in G.es]  # list of edges
    #
    #     L = len(position)
    #     Xn = [position[k][0] for k in range(L)]
    #     Yn = [2 * M - position[k][1] for k in range(L)]
    #     Xe = []
    #     Ye = []
    #     for edge in E:
    #         Xe += [position[edge[0]][0], position[edge[1]][0], None]
    #         Ye += [2 * M - position[edge[0]][1], 2 * M - position[edge[1]][1], None]
    #
    #     labels = v_label
    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbhuman_resources:position"

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbhuman_resources:positionrepresentation-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{ computed_str }}"


@receiver(post_save, sender=EmployeeHumanResource)
def post_save_employee(sender, instance, created, **kwargs):
    """
    Post save signal, Ensure that employee is among the employees of the CRM company profile upon save
    """
    if created:
        if not instance.weekly_off_periods.exists():
            # Default in creating the weekend default period off
            for default_period in instance.calendar.default_periods.all():
                EmployeeWeeklyOffPeriods.objects.get_or_create(
                    employee=instance, period=default_period, weekday=5
                )  # Saturday
                EmployeeWeeklyOffPeriods.objects.get_or_create(
                    employee=instance, period=default_period, weekday=6
                )  # Sunday
        [start, end] = EmployeeHumanResource.ExtraDaysBalanceFrequency[instance.extra_days_frequency].get_date_range(
            instance.enrollment_at
        )
        instance.assign_vacation_allowance_from_range(start.date(), end.date())

        try:
            main_company = Company.objects.get(id=get_main_company())
            rel = EmployerEmployeeRelationship.objects.get_or_create(
                employee=instance.profile,
                employer=main_company,
                defaults={
                    "primary": True,
                    "position": (
                        CRMPosition.objects.get_or_create(title=instance.position.name)[0]
                        if instance.position
                        else None
                    ),
                },
            )[0]
            rel.primary = True
            rel.save()
        except Company.DoesNotExist:
            pass

    # We assign or unassign the auth.Group position based on the active status
    if instance.is_active:
        instance.assign_position_groups()
    else:
        instance.unassign_position_groups()


@receiver(post_delete, sender=Position)
def post_delete_position(sender, instance, **kwargs):
    """
    Post delete Position logic
    """
    # We compute the height given the level of this position and its leaf node level
    if leaf_position := instance.get_family().filter(children__isnull=True).order_by("-level").first():
        instance.height = leaf_position.level - instance.level

    # We recompute the height for all ancestors if this position is a leaf node
    if instance.height == 0:
        for pos in instance.get_ancestors():
            pos.save()


@receiver(m2m_changed, sender=Position.groups.through)
def position_groups_to_employee(
    sender: Type[Position.groups.through], instance: Position, action: str, pk_set: set[int], **kwargs
):
    employees = EmployeeHumanResource.objects.filter(
        profile__isnull=False,
        profile__user_account__isnull=False,
        position__in=instance.get_descendants(include_self=True),
    )
    groups_to_changed = Group.objects.filter(id__in=pk_set)
    for employee in employees:
        user = employee.profile.user_account
        for group in groups_to_changed:
            if action == "post_add":
                if group not in user.groups.all():
                    user.groups.add(group)
            elif action in ["post_remove", "post_clear"]:
                user.groups.remove(group)


@shared_task
def deactivate_profile_as_task(requester_id: int, employee_id: int, substitute_id: Optional[int] = None):
    """
    Call the deactivation method as a async task

    Args:
        requester_id: The User account id of the user asking for the deactivation
        employee_id: The deactivated user profile
        substitute_id: The potential Profile id to replace this employee's resources

    """
    requester = get_user_model().objects.get(id=requester_id)
    employee = EmployeeHumanResource.objects.get(id=employee_id)
    substitute = None
    if substitute_id:
        substitute = Person.objects.get(id=substitute_id)
    messages = employee.deactivate(substitute)

    send_notification(
        code="wbhuman_resources.employeehumanresource.deactivate",
        title=gettext("{employee} deactivation ended and was successful").format(
            employee=employee.profile.computed_str
        ),
        body=gettext("The following actions have been done: \n{messages}").format(messages=messages),
        user=requester,
    )
