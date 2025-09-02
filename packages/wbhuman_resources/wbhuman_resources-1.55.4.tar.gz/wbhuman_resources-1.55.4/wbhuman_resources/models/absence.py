from datetime import timedelta

import pandas as pd
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import DateTimeRangeField, RangeOperators
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.functions import Coalesce
from django.db.models.signals import post_save
from django.db.utils import ProgrammingError
from django.dispatch import receiver
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext, pgettext_lazy
from django.utils.translation import gettext_lazy as _
from django_fsm import FSMField, transition
from pandas._libs.tslibs.offsets import BDay
from psycopg.types.range import TimestamptzRange
from wbcore.contrib.agenda.models import CalendarItem
from wbcore.contrib.geography.models import Geography
from wbcore.contrib.icons import WBIcon
from wbcore.contrib.notifications.dispatch import send_notification
from wbcore.contrib.notifications.utils import create_notification_type
from wbcore.enums import RequestType
from wbcore.metadata.configs.buttons import ActionButton, ButtonDefaultColor
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    create_simple_display,
)
from wbcore.models import WBModel
from wbcore.utils.models import CalendarItemTypeMixin

from .calendars import DayOff, DefaultDailyPeriod
from .preferences import get_previous_year_balance_expiration_date

User = get_user_model()


def can_cancel_request(instance: "AbsenceRequest", user: "User") -> bool:
    """
    Check if the given user has cancel ability on the given request

    Args:
        instance: The request
        user: User to check permission

    Returns:
        True if the user got the right to cancel this request
    """
    if instance.period.upper < timezone.now():
        return False
    return (
        user.profile == instance.employee.profile
        or user.has_perm("wbhuman_resources.administrate_absencerequest")
        or user.profile.human_resources.is_manager_of(instance.employee)
    )


def can_validate_or_deny_request(instance: "AbsenceRequest", user: "User") -> bool:
    """
    Check if the given user can validate or deny the given request

    Args:
        instance: The request
        user: User to check permission

    Returns:
        True if the user got the right to validate or deny this request
    """
    if user.has_perm("wbhuman_resources.administrate_absencerequest"):
        return True
    elif (
        user.profile
        and (employee := getattr(user.profile, "human_resources", None))
        and (requester := instance.employee)
    ):
        return employee.is_manager_of(requester)
    return False


class AbsenceRequestType(CalendarItemTypeMixin, WBModel):
    title = models.CharField(max_length=255, verbose_name=_("Title"))

    is_vacation = models.BooleanField(
        default=False,
        verbose_name=_("Vacation"),
        help_text=_("If true, the days will be counted towards the employee's vacation balance"),
    )
    is_timeoff = models.BooleanField(
        default=False, verbose_name=_("Time-Off"), help_text=_("If true, the employee is considered as not working")
    )
    is_extensible = models.BooleanField(
        default=False,
        verbose_name=_("Extensible"),
        help_text=_("If true, allow the associated request to be extended"),
    )
    auto_approve = models.BooleanField(default=False, verbose_name=_("Auto Approve"))
    days_in_advance = models.PositiveIntegerField(default=0, verbose_name=_("Days In Advance"))

    is_country_necessary = models.BooleanField(default=False, verbose_name=_("Is country necessary"))
    crossborder_countries = models.ManyToManyField(
        to="geography.Geography",
        limit_choices_to={"level": 1},
        blank=True,
        verbose_name=_("Countries"),
        help_text=_("List of countries where crossborder activity is allowed"),
    )
    extra_notify_groups = models.ManyToManyField(
        to=Group, blank=True, related_name="notified_absence_request_types", verbose_name=_("Extra Notify Groups")
    )

    def validate_country(self, country):
        if self.is_country_necessary:
            if not country:
                raise ValueError(_("A country is necessary for this absence request type"))
            elif not self.crossborder_countries.filter(id=country.id).exists():
                raise ValueError(
                    _(
                        "You are not allowed to have crossborder activities in the specified country for the specified absence request type"
                    )
                )
        return True

    class Meta:
        verbose_name = _("Absence Request Type")
        verbose_name_plural = _("Absence Request Types")

    def __str__(self):
        return self.title

    @classmethod
    def get_choices(cls) -> list[tuple[int, str]]:
        """
        Utility method that returns all possible absence request type choices as a text choices datastructure with id as name and title as label

        We expect runtime error at runtime on non-initialized database that will be caught and an empty list will be returned in that case.

        Returns:
            A list of tuple choices
        """
        try:
            return [(absence_type.id, absence_type.title) for absence_type in cls.objects.all()]
        except (RuntimeError, ProgrammingError):
            return []

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbhuman_resources:absencerequesttype"

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbhuman_resources:absencerequesttyperepresentation-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{title}}"


class AbsenceRequestManager(models.Manager):
    def get_queryset(self) -> "models.QuerySet[AbsenceRequest]":
        """
        Default manager that provide a set of annotated variables for convenience
        """
        return (
            super()
            .get_queryset()
            .annotate(
                daily_hours=Coalesce(
                    models.Subquery(
                        DefaultDailyPeriod.objects.filter(calendar=models.OuterRef("employee__calendar"))
                        .values("calendar")
                        .annotate(s=models.Sum("total_hours"))
                        .values("s")[:1]
                    ),
                    0.0,
                ),
                _total_hours=Coalesce(
                    models.Subquery(
                        AbsenceRequestPeriods.objects.filter(request=models.OuterRef("pk"))
                        .values("request")
                        .annotate(s=models.Sum("_total_hours"))
                        .values("s")[:1]
                    ),
                    0.0,
                ),
                _total_vacation_hours=Coalesce(
                    models.Subquery(
                        AbsenceRequestPeriods.vacation_objects.filter(request=models.OuterRef("pk"))
                        .values("request")
                        .annotate(s=models.Sum("_total_hours"))
                        .values("s")[:1]
                    ),
                    0.0,
                ),
                _total_hours_in_days=models.F("_total_hours") / models.F("daily_hours"),
                _total_vacation_hours_in_days=models.F("_total_vacation_hours") / models.F("daily_hours"),
            )
        )


class AbsenceRequest(CalendarItem):
    """
    Stores a single Absence Request entry, related to :model:`wbhuman_resources.EmployeeHumanResource` and :model:`wbcrm.Activity`.
    """

    class Status(models.TextChoices):
        DRAFT = "DRAFT", _("Draft")
        PENDING = "PENDING", _("Pending")
        APPROVED = "APPROVED", _("Approved")
        DENIED = "DENIED", _("Denied")
        CANCELLED = "CANCELLED", _("Cancelled")

    status = FSMField(
        default=Status.DRAFT,
        choices=Status.choices,
        verbose_name=_("Status"),
        help_text=_("The request status (defaults to draft)"),
    )

    type = models.ForeignKey(
        to="wbhuman_resources.AbsenceRequestType",
        related_name="request",
        verbose_name=_("Type"),
        on_delete=models.PROTECT,
    )

    employee = models.ForeignKey(
        "wbhuman_resources.EmployeeHumanResource",
        related_name="requests",
        on_delete=models.CASCADE,
        verbose_name=_("Employee"),
        help_text=_("The employee requesting the absence"),
    )

    notes = models.TextField(
        null=True, blank=True, verbose_name=_("Extra Notes"), help_text=_("A note to the HR administrator")
    )
    reason = models.TextField(
        null=True, blank=True, verbose_name=_("Reason"), help_text=_("The HR's response to this absence request")
    )
    created = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Created"), help_text=_("The request creation time")
    )

    attachment = models.FileField(
        null=True,
        blank=True,
        max_length=256,
        verbose_name=_("Attachment"),
        upload_to="human_resources/absence_request/attachments",
        help_text=_("Upload a file to document this absence request (e.g. medical certificate)"),
    )

    crossborder_country = models.ForeignKey(
        to="geography.Geography",
        null=True,
        blank=True,
        related_name="absence_requests",
        on_delete=models.PROTECT,
        verbose_name=_("Crossborder Country"),
        help_text=_("The country where this absence request will be held."),
        limit_choices_to={"level": 1},
    )

    @transition(
        field=status,
        source=[Status.DRAFT],
        target=Status.PENDING,
        permission=lambda instance, user: user.profile == instance.employee.profile
        or user.has_perm("wbhuman_resources.administrate_absencerequest"),
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                color=ButtonDefaultColor.WARNING,
                identifiers=("wbhuman_resources:absencerequest",),
                icon=WBIcon.SEND.icon,
                key="submit",
                label=_("Submit"),
                action_label=_("Submitting"),
                description_fields=_("<p>Are you sure you want to submit this request?</p>"),
                instance_display=create_simple_display([["notes"]]),
            )
        },
    )
    def submit(self, **kwargs):
        pass

    def post_submit(self, **kwargs):
        msg = gettext(
            "<p>{employee} has submitted a {type} request for {hours} hours from {lower} to {upper}.</p>"
        ).format(
            employee=str(self.employee),
            type=str(self.type),
            hours=self.total_hours,
            lower=self.period.lower.strftime("%Y-%m-%d %H:%M:%S"),
            upper=self.period.upper.strftime("%Y-%m-%d %H:%M:%S"),
        )
        if self.crossborder_country:
            msg += gettext("</br><p><b>Country:</b></p><i>{0}</i>").format(str(self.crossborder_country))
        if self.notes and self.notes != "<p></p>" and self.notes != "null":
            msg += gettext("</br><p><b>Employee's Note:</b></p><i>{notes}</i>").format(notes=self.notes)
        title = gettext("New {type} Request").format(type=str(self.type))
        self.notify(title, msg, to_requester=False, to_manager=True)

    def can_submit(self):
        errors = dict()
        try:
            self.type.validate_country(self.crossborder_country)
        except ValueError as e:
            errors["crossborder_country"] = e.args[0]
        return errors

    @transition(
        field=status,
        source=[Status.PENDING],
        target=Status.APPROVED,
        on_error="failed",
        permission=lambda instance, user: can_validate_or_deny_request(instance, user),
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbhuman_resources:absencerequest",),
                icon=WBIcon.APPROVE.icon,
                color=ButtonDefaultColor.SUCCESS,
                key="approve",
                label=_("Approve"),
                action_label=_("Approval"),
                description_fields=_("<p>Are you sure you want to approve this request?</p>"),
            )
        },
    )
    def approve(self, **kwargs):
        pass

    def post_approve(self, **kwargs):
        msg = gettext("<p>Your {type} request from {start_date} to {end_date} has been approved.</p>").format(
            type=str(self.type),
            start_date=self.period.lower.strftime("%d.%m.%Y"),
            end_date=self.period.upper.strftime("%d.%m.%Y"),
        )
        title = gettext("Absence request approved")
        self.notify(title, msg, to_requester=True)

    @transition(
        field=status,
        source=[Status.PENDING],
        target=Status.DENIED,
        permission=lambda instance, user: can_validate_or_deny_request(instance, user),
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbhuman_resources:absencerequest",),
                icon=WBIcon.DENY.icon,
                color=ButtonDefaultColor.ERROR,
                key="deny",
                label=_("Deny"),
                action_label=_("Denial"),
                description_fields=_("<p>Are you sure you want to deny this request?</p>"),
                instance_display=create_simple_display([["reason"]]),
            )
        },
    )
    def deny(self, **kwargs):
        pass

    def post_deny(self, **kwargs):
        if self.type.is_vacation:
            msg = gettext("<p>Your absence request from {start_date} to {end_date} has been denied.</p>").format(
                start_date=self.period.lower.strftime("%d.%m.%Y"), end_date=self.period.upper.strftime("%d.%m.%Y")
            )
            if self.reason and self.reason not in ["<p></p>", ""]:
                msg += gettext("</br><p><b>HR's reason:</b></p><i>{reason}</i>").format(reason=self.reason)
            title = gettext("Absence request denied")
            self.notify(title, msg, to_requester=True)

    @transition(
        field=status,
        source=[Status.PENDING],
        target=Status.DRAFT,
        permission=lambda instance, user: user.profile == instance.employee.profile
        or user.has_perm("wbhuman_resources.administrate_absencerequest"),
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbhuman_resources:absencerequest",),
                color=ButtonDefaultColor.WARNING,
                icon=WBIcon.EDIT.icon,
                key="backtodraft",
                label=_("Back to Draft"),
                action_label=_("Back to Draft"),
                description_fields=_("<p>Are you sure you want to put this request back to draft?</p>"),
            )
        },
    )
    def backtodraft(self, **kwargs):
        pass

    @transition(
        field=status,
        source=[Status.APPROVED],
        target=Status.CANCELLED,
        on_error="failed",
        permission=can_cancel_request,
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbhuman_resources:absencerequest",),
                icon=WBIcon.REJECT.icon,
                color=ButtonDefaultColor.ERROR,
                key="cancel",
                label=pgettext_lazy("Transition button", "Cancel"),
                action_label=_("Cancellation"),
                description_fields=_("<p>Are you sure you want to cancel this request?</p>"),
            )
        },
    )
    def cancel(self, **kwargs):
        pass

    def post_cancel(self, **kwargs):
        msg = gettext("{employee} has cancelled a {type} request from {start_date} to {end_date}.").format(
            employee=str(self.employee),
            type=str(self.type),
            start_date=self.period.lower.strftime("%d.%m.%Y"),
            end_date=self.period.upper.strftime("%d.%m.%Y"),
        )
        self.periods.all().delete()
        title = gettext("Cancelled {type} Request").format(type=str(self.type))
        self.notify(title, msg, to_manager=True)

    objects = AbsenceRequestManager()

    class Meta:
        verbose_name = _("Absence Request")
        verbose_name_plural = _("Absence Requests")
        permissions = [("administrate_absencerequest", "Can Administrate Absence Requests")]

    @property
    @admin.display(description="Total hours")
    def total_hours(self) -> float:
        return getattr(self, "_total_hours", self.periods.aggregate(s=models.Sum("_total_hours"))["s"] or 0.0)

    @property
    @admin.display(description="Total Vacation hours")
    def total_vacation_hours(self) -> float:
        return getattr(
            self,
            "_total_vacation_hours",
            self.total_hours if self.type.is_vacation and self.status == AbsenceRequest.Status.APPROVED else 0.0,
        )

    @property
    @admin.display(description="Total hours (in days)")
    def total_hours_in_days(self) -> float:
        return getattr(self, "_total_hours_in_days", self.total_hours / self.employee.calendar.get_daily_hours())

    @property
    @admin.display(description="Total Vacation hours (in days)")
    def total_vacation_hours_in_days(self) -> float:
        return getattr(
            self, "_total_vacation_hours_in_days", self.total_vacation_hours / self.employee.calendar.get_daily_hours()
        )

    @property
    def next_extensible_period(self) -> TimestamptzRange | None:
        upper_date = (self.period.upper + BDay(1)).to_pydatetime()
        while self.employee.calendar.days_off.filter(date=upper_date.date(), count_as_holiday=True).exists():
            upper_date += timedelta(days=1)
        if not AbsenceRequestPeriods.objects.filter(employee=self.employee, date=upper_date).exists():
            return TimestamptzRange(lower=self.period.lower, upper=upper_date)

    def get_color(self) -> str:
        return self.type.color

    def get_icon(self) -> str:
        return self.type.icon

    def __str__(self) -> str:
        return f"{str(self.employee)} [{self.period.lower:%Y-%m-%d %H:%M}-{self.period.upper:%Y-%m-%d %H:%M}] ({self.Status[self.status].label})"

    def clean(self):
        if not self.period or not self.period.lower or not self.period.upper:
            raise ValidationError("Period needs to be set with nonnull bound")
        super().clean()

    def save(self, *args, **kwargs):
        self.title = f"{str(self.type)}: {str(self.employee)}"
        self.full_clean()
        if self.id and self.periods.count() > 1:
            self.all_day = True
        self.is_cancelled = self.status == self.Status.CANCELLED
        self.period = self.employee.calendar.normalize_period(
            self.period
        )  # We normalize the period to be sure it respect the default calendar working periods
        super().save(*args, **kwargs)

    def delete(self, **kwargs):
        super().delete(no_deletion=False)

    @property
    def periods_timespan(self) -> TimestamptzRange:
        """
        Property to returns the timespan datetime range originating from the attached periods

        Returns:
            A datetime range. None if no period are already attached to this request
        """
        periods = self.periods.order_by("timespan__startswith")
        if periods.exists():
            return TimestamptzRange(lower=periods.first().timespan.lower, upper=periods.last().timespan.upper)

    def notify(self, title: str, msg: str, to_requester: bool = True, to_manager: bool = False):
        """
        Get a message and a title and create the proper Notification object for the user administrating the HR module

        Args:
            title (str): The Notification title
            msg (str): The Notification message
        """
        users = []
        if to_requester and (requester_account := getattr(self.employee.profile, "user_account", None)):
            users.append(requester_account)
        if to_manager:
            for manager in self.employee.get_managers():
                if manager_account := getattr(manager, "user_account", None):
                    users.append(manager_account)
            for extra_group in self.type.extra_notify_groups.all():
                for extra_notify_user in extra_group.user_set.all():
                    users.append(extra_notify_user)
        for user in users:
            if user.is_active:
                send_notification(
                    code="wbhuman_resources.absencerequest.notify",
                    title=title,
                    body=msg,
                    user=user,
                    reverse_name="wbhuman_resources:absencerequest-detail",
                    reverse_args=[self.id],
                )

    def is_deletable_for_user(self, user: "User") -> bool:
        """
        Check if the given user has the permission to delete a request

        Args:
            user: Checked user

        Returns:
            True if the request can be deleted by the user
        """
        return self.is_deletable and (
            (self.status == AbsenceRequest.Status.PENDING and self.period.lower > timezone.now())
            or self.status == AbsenceRequest.Status.DRAFT
            or user.has_perm("wbhuman_resources.administrate_absencerequest")
        )

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbhuman_resources:absencerequest"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{employee}}"


class AbsenceRequestPeriodDefaultManager(models.Manager):
    def get_queryset(self) -> "models.QuerySet[AbsenceRequestPeriods]":
        """
        Default manager
        """
        return super().get_queryset().annotate(_total_hours=models.F("default_period__total_hours"))


class AbsenceRequestPeriodVacationManager(models.Manager):
    def get_queryset(self) -> "models.QuerySet[AbsenceRequestPeriods]":
        """
        Default manager
        """
        return (
            super()
            .get_queryset()
            .filter(request__type__is_vacation=True, request__status=AbsenceRequest.Status.APPROVED)
            .annotate(_total_hours=models.F("default_period__total_hours"))
        )


class AbsenceRequestPeriods(models.Model):
    request = models.ForeignKey(
        "wbhuman_resources.AbsenceRequest",
        related_name="periods",
        on_delete=models.CASCADE,
        verbose_name=_("Request"),
        help_text=_("The associated request"),
    )
    employee = models.ForeignKey(
        "wbhuman_resources.EmployeeHumanResource",
        related_name="periods",
        on_delete=models.CASCADE,
        verbose_name=_("Employee"),
        help_text=_("The Requester"),
    )  # Not supposed to be set dynamically. Use as a replicate to ensure database constraint
    default_period = models.ForeignKey(
        "wbhuman_resources.DefaultDailyPeriod",
        related_name="periods",
        on_delete=models.PROTECT,
        verbose_name=_("Period"),
        help_text=_("The associated period"),
    )
    date = models.DateField()

    timespan = DateTimeRangeField(
        verbose_name=_("Timespan"),
    )  # Expected to be read only

    balance = models.ForeignKey(
        "wbhuman_resources.EmployeeYearBalance",
        related_name="periods",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name=_("Balance"),
        help_text=_("For which balance this absence will count towards"),
    )
    consecutive_hours_count = models.IntegerField(
        default=0,
        verbose_name=_("Consecutive Absence Hours count"),
        help_text=_("The number of consecutive hours this absence request period spans"),
    )

    objects = AbsenceRequestPeriodDefaultManager()
    vacation_objects = AbsenceRequestPeriodVacationManager()

    class Meta:
        verbose_name = _("Absence Request Period")
        verbose_name_plural = _("Absence Request Periods")
        unique_together = ("employee", "default_period", "date")
        indexes = [
            models.Index(fields=["employee", "default_period", "date"]),
        ]
        constraints = [
            ExclusionConstraint(
                name="exclude_overlapping_periods",
                expressions=[
                    ("timespan", RangeOperators.OVERLAPS),
                    ("employee", RangeOperators.EQUAL),
                ],
            ),
        ]

        notification_types = [
            create_notification_type(
                code="wbhuman_resources.absencerequest.notify",
                title="Absence Notification",
                help_text="Sends a notification when you can approve an absence request",
            )
        ]

    def __str__(self) -> str:
        return f"{self.request.employee.computed_str}: {self.timespan.lower:%Y-%m-%d %H:%M:%S}-{self.timespan.upper:%Y-%m-%d %H:%M:%S} ({self.total_hours})"

    @cached_property
    def total_hours(self) -> float:
        """
        A property holding the number of hours this period has. Get it from the attached default period
        """
        return getattr(self, "_total_hours", self.default_period.total_hours)

    @property
    def previous_period(self):
        """
        Return the previous approved period if it exists from this period's employee
        """
        return (
            AbsenceRequestPeriods.objects.exclude(
                request__status=AbsenceRequest.Status.CANCELLED,
            )
            .filter(
                employee=self.employee,
                timespan__startswith__lt=self.timespan.lower,
            )
            .order_by("-timespan__startswith")
            .first()
        )

    @classmethod
    def get_periods_as_df(cls, start: date, end: date, **extra_filter_kwargs) -> pd.DataFrame:
        """
        Utility function that reshape the periods for a given calendar and a list of employees among a certain date range

        Args:
            start: Start filter
            end: End filter
            extra_filter_kwargs: keyword argument that can be passed down to filter out employees

        Returns:
            A dataframe whose columns are [employee, period, date, type, status]
        """
        periods = cls.objects.filter(
            models.Q(date__gte=start),
            models.Q(date__lte=end),
            models.Q(_total_hours__gt=0)
            & models.Q(
                request__status__in=[
                    AbsenceRequest.Status.APPROVED.name,
                    AbsenceRequest.Status.PENDING.name,
                    AbsenceRequest.Status.DRAFT.name,
                ]
            ),
        ).filter(**extra_filter_kwargs)
        df_periods = pd.DataFrame(
            periods.values(
                "employee",
                "request__type__title",
                "request__status",
                "default_period",
                "date",
            ),
            columns=["employee", "request__type__title", "request__status", "default_period", "date"],
        ).rename(
            columns={
                "employee": "employee",
                "request__type__title": "type",
                "request__status": "status",
                "default_period": "period",
                "date": "date",
            }
        )
        return df_periods

    def assign_balance(self, check_date_availability: bool = True):
        """
        Utility function that returns what balance this request will be counted for

        Args:
            check_date_availability: If False, we bypass wether this request can be used toward the previous year balance from the prereference and only check if the previous year balance can accomotate the period's total hours
        """

        if self.request.type.is_vacation:
            previous_balances_with_positive_allowance = self.employee.balances.filter(
                _total_vacation_hourly_balance__gte=self.total_hours, year__lt=self.date.year
            )
            year = (
                previous_balances_with_positive_allowance.earliest("year").year
                if previous_balances_with_positive_allowance.exists()
                else self.date.year
            )

            # we loop to try to find, in order, the first balance to accomodate our request since the request's year to the max year
            while year <= self.date.year + 1 and self.balance is None:
                if possible_balance := self.employee.balances.filter(year=year).first():
                    if (
                        possible_balance.balance > 0
                        and possible_balance.total_vacation_hourly_balance >= self.total_hours
                        and get_previous_year_balance_expiration_date(possible_balance.year) > self.date
                    ):
                        self.balance = possible_balance
                        self.save()
                year += 1
            if self.balance is None:
                # we make sure that the max year is always the last seeded balance year + 1
                seeded_balances = self.employee.balances.filter(_given_balance__gt=0)
                if seeded_balances.exists():
                    self.balance = self.employee.get_or_create_balance(seeded_balances.latest("year").year + 1)[0]

    def get_consecutive_hours_count(self) -> float:
        """
        This subroutines aims to find the latest valid request days and get its consecutive days balance in order to
        compute this request day consecutive days balance.
        """
        consecutive_hours = self.total_hours
        if (
            (previous_period := self.previous_period)
            and previous_period.request.type.is_timeoff
            and not list(
                self.employee.extract_workable_periods(previous_period.timespan.upper, self.timespan.lower, count=1)
            )
        ):
            consecutive_hours += previous_period.consecutive_hours_count
        return consecutive_hours

    def save(self, *args, **kwargs):
        self.timespan = TimestamptzRange(
            lower=self.default_period.get_lower_datetime(self.date),
            upper=self.default_period.get_upper_datetime(self.date),
        )
        self.employee = self.request.employee
        self.consecutive_hours_count = self.get_consecutive_hours_count()
        super().save(*args, **kwargs)

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{request}}{{timespan}}{{_total_hours}}"


@receiver(post_save, sender=AbsenceRequest)
def post_save_absence_request(sender, instance, created, **kwargs):
    """
    Post save signal
    * Auto approve request if there are not absence request.
    * Compute and Create one AbsenceRequestPeriods if the request holds within the same year or two if the request spans multiple years.
    AbsenceRequestPeriods stores the total number of working days for a certain period of time.
    """

    if instance.type.auto_approve and instance.status == AbsenceRequest.Status.DRAFT:
        instance.submit()
        AbsenceRequest.objects.filter(id=instance.id).update(status=AbsenceRequest.Status.APPROVED)

    if employee := instance.employee:
        instance.entities.set([employee.profile])

    # We make sure that the periods are deleted on cancellation
    if instance.status == AbsenceRequest.Status.CANCELLED:
        instance.periods.all().delete()

    # Create for every workable period a Absence request period object for this request
    existing_periods = instance.periods
    for period_date, default_period in instance.employee.extract_workable_periods(
        instance.period.lower, instance.period.upper
    ):
        period, created = AbsenceRequestPeriods.objects.get_or_create(
            default_period=default_period, employee=instance.employee, date=period_date, defaults={"request": instance}
        )
        existing_periods = existing_periods.exclude(id=period.id)
    existing_periods.all().delete()
    update_kwargs = {"all_day": (instance.periods.count() > 1)}
    if (new_period := instance.periods_timespan) and new_period != instance.period:
        update_kwargs["period"] = new_period
    AbsenceRequest.objects.filter(id=instance.id).update(**update_kwargs)

    if instance.status == AbsenceRequest.Status.APPROVED and instance.type.is_vacation:
        for period in instance.periods.filter(balance__isnull=True).order_by("timespan__startswith"):
            period.assign_balance()


# TODO find an optimal way to recompute consecutive hours count on posterieurs periods save
# @shared_task
# def save_future_employee_periods_as_task(request_id: int, from_datetime: datetime):
#     request = AbsenceRequest.objects.get(id=request_id)
#     if (new_period := request.timespan) and new_period != request.period:
#         AbsenceRequest.objects.filter(id=request.id).update(period=new_period)
#     for period in AbsenceRequestPeriods.objects.filter(
#         employee=request.employee, timespan__startswith__gt=from_datetime
#     ).order_by("timespan__startswith"):
#         # If the consecutive hours is equals to a normal working day, we assume this is the beginning of a new continious serie of periods
#         if period.consecutive_hours_count == period.default_period.calendar.get_daily_hours():
#             break
#         period.save()


# @receiver(post_delete, sender=AbsenceRequestPeriods)
# @receiver(post_save, sender=AbsenceRequestPeriods)
# def receiver_absence_request_periods(sender, instance, **kwargs):
#     if kwargs.get("created", False) or not hasattr(kwargs, "created"):
#         save_future_employee_periods_as_task.delay(instance.request.id, instance.timespan.upper)


@receiver(post_save, sender=DayOff)
def post_save_dayoff(sender, instance, created, **kwargs):
    """
    Post save signal, Ensure that when a day off is created, all absence request periods are recomputed
    """
    if created:
        for period in AbsenceRequestPeriods.objects.filter(date=instance.date):
            period.request.save()


@receiver(post_save, sender=AbsenceRequestType)
def post_save_absence_request_type(sender, instance: AbsenceRequestType, created: bool, raw: bool, **kwargs):
    """
    Post save signal for absence request type
    """
    # Ensure that when a absence request where country validation is necessary, all countries are added to the allowed list by default
    if created and instance.is_country_necessary:
        instance.crossborder_countries.set(Geography.countries.all())

    if not raw:
        # We need to trigger all requests' save methods to update their color and icon
        for request in instance.request.all():
            request.save()


@receiver(post_save, sender=Geography)
def post_country_creation(sender, instance, created, **kwargs):
    """
    Post save signal, Ensure that when a country is created, it is added by default to all absence request where country validation is necessary
    """
    if created and instance.level == 1:
        for absence_request_type in AbsenceRequestType.objects.filter(is_country_necessary=True):
            absence_request_type.crossborder_countries.add(instance)
