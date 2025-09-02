import zoneinfo
from datetime import date, datetime, time
from importlib import import_module
from typing import TypeVar

import pandas as pd
from dateutil import rrule
from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import DateTimeRangeField, RangeOperators
from django.db import models
from django.db.models import CheckConstraint, F, Q, Sum
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from dynamic_preferences.registries import global_preferences_registry
from psycopg.types.range import TimestamptzRange
from timezone_field import TimeZoneField
from wbcore.contrib.agenda.models import CalendarItem
from wbcore.contrib.icons import WBIcon
from wbcore.models import WBModel

SelfDefaultDailyPeriod = TypeVar("SelfDefaultDailyPeriod", bound="DefaultDailyPeriod")


class InvalidDayOffCalendarResourceError(Exception):
    pass


class DayOffCalendar(WBModel):
    title = models.CharField(max_length=255)
    resource = models.CharField(
        max_length=255, null=True, blank=True, help_text=_("Used to fetch the days off from an API.")
    )
    timezone = TimeZoneField(default="UTC")

    def __str__(self) -> str:
        return f"{self.title}"

    def get_period_start_choices(self) -> list[str]:
        """
        Get a text choices datastructure from the possible Default Periods starts time

        Returns:
            a list of tuple containing the string representation of the periods lower time
        """
        return [str(t) for t in self.default_periods.order_by("lower_time").values_list("lower_time", flat=True)]

    def get_period_end_choices(self) -> list[str]:
        """
        Get a text choices datastructure from the possible Default Periods ends time

        Returns:
            a list of tuple containing the string representation of the periods upper time
        """
        return [str(t) for t in self.default_periods.order_by("upper_time").values_list("upper_time", flat=True)]

    def create_public_holidays(self, year: int):
        """
        Utility function that generate all holiday provided by the "workalendar" package as DayOff for the given year

        Args:
            year: Year to generate holidays from
        Raises:
            InvalidDayOffCalendarResourceError if calendar's resource is wrongly formatted.
        """
        # If no resource is specified, then we exit early
        if self.resource is None or self.resource == "":
            return

        continent, region = self.resource.split(".")
        try:
            workalendar = import_module(f"workalendar.{continent}")
            holidays = getattr(workalendar, region)()
            for holiday_date, holiday_title in holidays.holidays(year):
                DayOff.objects.get_or_create(
                    date=holiday_date, calendar=self, defaults={"count_as_holiday": True, "title": holiday_title}
                )
        except ModuleNotFoundError:
            raise InvalidDayOffCalendarResourceError(_("The continent you've supplied is invalid."))
        except AttributeError:
            raise InvalidDayOffCalendarResourceError(_("The region you've supplied is invalid."))

    def get_day_off_per_employee_df(self, start: date, end: date, employees) -> pd.DataFrame:
        """
        Utility function that reshape the day off for a given calendar and a list of employees among a certain date range

        Args:
            start: Start filter
            end: End filter
            employees: Queryset of employees

        Returns:
            A dataframe whose columns are [employee, period, date, type, status] with type HOLIDAY and status APPROVED
        """
        employee_df = pd.DataFrame(employees.values("id")).rename(columns={"id": "employee"})
        day_off_df = pd.DataFrame(self.days_off.filter(date__gte=start, date__lte=end).values("date"))
        periods_df = pd.DataFrame(self.default_periods.values("id")).rename(columns={"id": "period"})
        df = employee_df.merge(day_off_df, how="cross").merge(periods_df, how="cross")
        df["type"] = "Holiday"
        df["status"] = "APPROVED"
        return df

    def get_daily_hours(self) -> float:
        """
        Utility function to return the total number of hours that a typical working day spans from this calendar

        Returns:
            A float number corresponding to the total working hours
        """
        return self.default_periods.aggregate(s=Sum("total_hours"))["s"] or 0

    def get_unworked_time_range(self, start_time: time = None) -> list[tuple[int, int]]:
        """
        Utility function that return a list of unworked time range. These time range are the exclusion of the periods defined in the default period table and a typical earth time range.

        Args:
            start_time: If specified, starts the day from that time. Default to time(0,0,0)

        Returns:
            A list of time range tuple
        """
        if not start_time:
            start_time = time(0, 0, 0)
        rules = rrule.rruleset()
        rules.rrule(
            rrule.rrule(
                freq=rrule.MINUTELY,
                dtstart=datetime(1, 1, 1, 0, 0),
                until=datetime(1, 1, 1, 23, 59),
            )
        )
        for period in self.default_periods.order_by("lower_time"):
            rules.exrule(
                rrule.rrule(
                    rrule.MINUTELY,
                    dtstart=datetime(1, 1, 1, period.lower_time.hour, period.lower_time.minute, 0),
                    until=datetime(1, 1, 1, period.upper_time.hour, period.upper_time.minute, 0),
                )
            )

        non_workable_minutes = list(rules)
        pivot_index = next(x[0] for x in enumerate(non_workable_minutes) if x[1].time() >= start_time)
        non_workable_minutes = non_workable_minutes[pivot_index:] + non_workable_minutes[:pivot_index]

        start_range = None
        before_minute = None
        for minute in non_workable_minutes:
            if not start_range:
                start_range = minute
            if before_minute and minute.minute != (before_minute.minute + 1) % 60:
                yield start_range.time(), before_minute.time()
                start_range = minute
            before_minute = minute
        yield start_range.time(), before_minute.time()

    def save(self, *args, **kwargs):
        if not self.resource:
            self.resource = global_preferences_registry.manager()[
                "wbhuman_resources__calendar_default_public_holiday_package"
            ]
        if not self.timezone:
            self.timezone = zoneinfo.ZoneInfo(
                global_preferences_registry.manager()["wbhuman_resources__calendar_default_timezone"]
            )
        super().save(*args, **kwargs)

    def get_default_fullday_period(self, val_date):
        return TimestamptzRange(
            lower=self.default_periods.earliest("lower_time").get_lower_datetime(val_date),
            upper=self.default_periods.latest("lower_time").get_upper_datetime(val_date),
        )

    def normalize_period(self, period: TimestamptzRange) -> TimestamptzRange:
        """
        Given a aware range of datetime, ensure that the local time of each corresponds to a valid time choices
        Args:
            period: The period to normalize

        Returns:
            The normalize period
        """

        def _get_closest_time(periods, ts):
            return sorted(
                map(lambda x: (x[0], abs(ts - x[0].hour * 3600 + x[0].minute * 60 + x[0].second)), periods),
                key=lambda x: x[1],
            )[0][0]

        local_lower_datetime = period.lower.astimezone(self.timezone)
        local_upper_datetime = period.upper.astimezone(self.timezone)
        if str(local_lower_datetime.astimezone(self.timezone).time()) not in self.get_period_start_choices():
            closest_time = _get_closest_time(
                self.default_periods.values_list("lower_time"),
                local_lower_datetime.time().hour * 3600
                + local_lower_datetime.time().minute * 60
                + local_lower_datetime.time().second,
            )
            local_lower_datetime = datetime.combine(period.lower.date(), closest_time, tzinfo=self.timezone)
        if str(local_upper_datetime.astimezone(self.timezone).time()) not in self.get_period_end_choices():
            closest_time = _get_closest_time(
                self.default_periods.exclude(lower_time__lt=local_lower_datetime.time()).values_list("upper_time"),
                local_upper_datetime.time().hour * 3600
                + local_upper_datetime.time().minute * 60
                + local_upper_datetime.time().second,
            )
            local_upper_datetime = datetime.combine(period.upper.date(), closest_time, tzinfo=self.timezone)
        return TimestamptzRange(lower=local_lower_datetime, upper=local_upper_datetime)

    class Meta:
        verbose_name = _("Day Off Calendar")
        verbose_name_plural = _("Days Off Calendar")
        unique_together = ("resource", "timezone")

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbhuman_resources:dayoffcalendar"

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbhuman_resources:dayoffcalendarrepresentation-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{title}}"


class DayOff(CalendarItem):
    date = models.DateField(verbose_name=_("Date"))
    count_as_holiday = models.BooleanField(
        default=True,
        verbose_name=_("Count as Holiday"),
        help_text=_("If true, there is no work but the day counts towards the employees' vacation balance"),
    )
    calendar = models.ForeignKey(
        to="wbhuman_resources.DayOffCalendar",
        related_name="days_off",
        on_delete=models.PROTECT,
        verbose_name=_("Calendar"),
    )

    class Meta:
        verbose_name = _("Day Off")
        verbose_name_plural = _("Days Off")
        constraints = [models.UniqueConstraint(fields=["date", "calendar"], name="unique_date_for_calendar")]

    def __str__(self) -> str:
        return f"{self.title} ({self.date})"

    def get_color(self) -> str:
        return "#211ae9"  # dark blue

    def get_icon(self) -> str:
        return WBIcon.DAY_OFF.icon

    def save(self, *args, **kwargs) -> TimestamptzRange:
        default_periods = self.calendar.default_periods
        self.all_day = True
        if default_periods.exists():
            self.period = self.calendar.get_default_fullday_period(self.date)
        super().save(*args, **kwargs)

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbhuman_resources:dayoff"

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbhuman_resources:dayoffresentation-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{title}}"


class DefaultDailyPeriod(models.Model):
    lower_time = models.TimeField()
    upper_time = models.TimeField()

    timespan = (
        DateTimeRangeField()
    )  # "readonly" field that default to combined time with the epoch date, Used to apply database constraint
    title = models.CharField(max_length=128)
    total_hours = models.FloatField()

    calendar = models.ForeignKey(
        to="wbhuman_resources.DayOffCalendar",
        related_name="default_periods",
        on_delete=models.PROTECT,
        verbose_name=_("Calendar"),
    )

    class Meta:
        verbose_name = _("Default Daily Period")
        verbose_name_plural = _("Default Daily Periods")
        constraints = [
            CheckConstraint(check=Q(upper_time__gt=F("lower_time")), name="check_lower_time_lt_upper_time"),
            ExclusionConstraint(
                expressions=[("timespan", RangeOperators.OVERLAPS), ("calendar", RangeOperators.EQUAL)],
                name="check_no_overlapping_default_periods_time",
            ),
        ]

    def save(self, *args, **kwargs):
        if not hasattr(self, "calendar") or not self.calendar:
            self.calendar = DayOffCalendar.objects.first()
        self.timespan = TimestamptzRange(
            lower=self.get_lower_datetime(date(1970, 1, 1)),
            upper=self.get_upper_datetime(date(1970, 1, 1)),
        )
        if not self.total_hours:
            self.total_hours = (self.timespan.upper - self.timespan.lower).total_seconds() / 3600
        super().save(*args, **kwargs)

    def get_lower_datetime(self, val_date: date) -> datetime:
        """
        Getter function to build a datetime object from this lower period time and the given date

        Args:
            val_date: The date to combine the time with

        Returns:
            A datetime
        """
        return datetime.combine(val_date, self.lower_time, tzinfo=self.calendar.timezone)

    def get_upper_datetime(self, val_date: date) -> datetime:
        """
        Getter function to build a datetime object from this uper period time and the given date

        Args:
            val_date: The date to combine the time with

        Returns:
            A datetime
        """
        return datetime.combine(val_date, self.upper_time, tzinfo=self.calendar.timezone)

    def __str__(self) -> str:
        return f"{self.title} ({self.calendar}) [{self.lower_time:%H:%M} - {self.upper_time:%H:%M}]"

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbhuman_resources:defaultdailyperiodrepresentation-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{title}}"


@receiver(post_migrate, sender=DayOffCalendar)
def post_migrate_day_off_calendar(sender, verbosity, interactive, stdout, using, plan, apps, **kwargs):
    """
    After migration, we check if DayOffCalendar have at least one element. OOtherwise, we create a default one
    """
    if not DayOffCalendar.objects.exists():
        calendar = DayOffCalendar.objects.create(title="Default Calendar", timezone=timezone.get_current_timezone())
        global_preferences_registry["wbhuman_resources__employee_default_calendar"] = calendar
