import zoneinfo
from datetime import datetime, time, timedelta
from importlib import import_module

import pytest
from django.db.models import Q
from django.utils.timezone import make_aware
from faker import Faker
from psycopg.types.range import TimestamptzRange

from wbhuman_resources.models.calendars import (
    DayOff,
    InvalidDayOffCalendarResourceError,
)
from wbhuman_resources.models.employee import EmployeeHumanResource

fake = Faker()


@pytest.mark.django_db
class TestDayOffCalendar:
    def test_get_period_start_choices(self, day_off_calendar):
        assert day_off_calendar.get_period_start_choices() == ["09:00:00", "14:00:00"]

    def test_get_period_end_choices(self, day_off_calendar):
        assert day_off_calendar.get_period_end_choices() == ["13:00:00", "18:00:00"]

    @pytest.mark.parametrize("val_date", [(fake.date_this_decade())])
    def test_create_public_holidays_sanitize_resource(self, day_off_calendar_factory, val_date):
        with pytest.raises(InvalidDayOffCalendarResourceError):
            calendar = day_off_calendar_factory.create(resource="eurasia.China")
            calendar.create_public_holidays(val_date.year)
        with pytest.raises(InvalidDayOffCalendarResourceError):
            calendar = day_off_calendar_factory.create(resource="europe.Listenbourg")
            calendar.create_public_holidays(val_date.year)

    @pytest.mark.parametrize(
        "val_date,continent,region",
        [
            (fake.date_this_decade(), "europe", "Berlin"),
            (fake.date_this_decade(), "europe", "Switzerland"),
        ],
    )
    def test_create_public_holidays_valid_resource(self, day_off_calendar_factory, val_date, continent, region):
        calendar = day_off_calendar_factory.create(resource=f"{continent}.{region}")
        calendar.create_public_holidays(val_date.year)
        workalendar = import_module(f"workalendar.{continent}")
        cal = getattr(workalendar, region)()
        for _d, _ in cal.holidays(val_date.year):
            assert DayOff.objects.filter(
                date=_d,
                calendar=calendar,
            )

    def test_get_day_off_per_employee_df(self, day_off_calendar, employee_human_resource_factory, day_off_factory):
        employee1 = employee_human_resource_factory.create()
        employee2 = employee_human_resource_factory.create()
        employee_human_resource_factory.create()
        base_day_off = day_off_factory.create()
        period1 = day_off_calendar.default_periods.first()
        period2 = day_off_calendar.default_periods.last()
        day_off_factory.create(date=base_day_off.date - timedelta(days=1))  # create left_outside_day_off
        day_off_factory.create(date=base_day_off.date + timedelta(days=1))  # create right_outside_day_off
        res = (
            day_off_calendar.get_day_off_per_employee_df(
                base_day_off.date,
                base_day_off.date,
                EmployeeHumanResource.objects.filter(Q(id=employee1.id) | Q(id=employee2.id)),
            )
            .set_index(["employee", "period"])
            .to_dict("index")
        )
        assert res == {
            (employee1.id, period1.id): {"date": base_day_off.date, "type": "Holiday", "status": "APPROVED"},
            (employee1.id, period2.id): {"date": base_day_off.date, "type": "Holiday", "status": "APPROVED"},
            (employee2.id, period1.id): {"date": base_day_off.date, "type": "Holiday", "status": "APPROVED"},
            (employee2.id, period2.id): {"date": base_day_off.date, "type": "Holiday", "status": "APPROVED"},
        }

    @pytest.mark.parametrize("h1,h2", [(fake.pyint(min_value=1), fake.pyint(min_value=1))])
    def test_get_daily_hours(self, day_off_calendar_without_period, default_daily_period_factory, h1, h2):
        default_daily_period_factory.create(
            calendar=day_off_calendar_without_period,
            total_hours=h1,
            lower_time=time(9, 0, 0),
            upper_time=time(13, 0, 0),
        )
        default_daily_period_factory.create(
            calendar=day_off_calendar_without_period,
            total_hours=h2,
            lower_time=time(14, 0, 0),
            upper_time=time(18, 0, 0),
        )
        assert day_off_calendar_without_period.get_daily_hours() == h1 + h2

    @pytest.mark.parametrize(
        "ranges, hour_start, expected_res",
        [
            (
                [(time(9, 0, 0), time(13, 0, 0)), (time(14, 0, 0), time(18, 0, 0))],
                time(0, 0),
                [(time(0, 0), time(8, 59)), (time(13, 1), time(13, 59)), (time(18, 1), time(23, 59))],
            ),
            (
                [(time(9, 0, 0), time(13, 0, 0)), (time(14, 0, 0), time(18, 0, 0))],
                time(4, 0),
                [(time(4, 0), time(8, 59)), (time(13, 1), time(13, 59)), (time(18, 1), time(3, 59))],
            ),
            (
                [(time(9, 0, 0), time(13, 0, 0)), (time(14, 0, 0), time(18, 0, 0))],
                time(15, 0),
                [(time(18, 1), time(8, 59)), (time(13, 1), time(13, 59))],
            ),
            (
                [(time(9, 0, 0), time(13, 0, 0)), (time(14, 0, 0), time(18, 0, 0))],
                time(20, 0),
                [(time(20, 0), time(8, 59)), (time(13, 1), time(13, 59)), (time(18, 1), time(19, 59))],
            ),
        ],
    )
    def test_get_unworked_time_range(
        self, day_off_calendar_without_period, default_daily_period_factory, ranges, hour_start, expected_res
    ):
        for lower, upper in ranges:
            default_daily_period_factory.create(
                calendar=day_off_calendar_without_period, lower_time=lower, upper_time=upper
            )

        assert list(day_off_calendar_without_period.get_unworked_time_range(hour_start)) == expected_res

    @pytest.mark.parametrize(
        "unnormalized_lower_datetime, unnormalized_upper_datetime, expected_lower_datetime, expected_upper_datetime",
        [
            (datetime(2023, 1, 1, 8), datetime(2023, 1, 1, 20), datetime(2023, 1, 1, 9), datetime(2023, 1, 1, 18)),
            (datetime(2023, 1, 1, 15), datetime(2023, 1, 1, 23), datetime(2023, 1, 1, 14), datetime(2023, 1, 1, 18)),
            (
                datetime(2023, 1, 1, 2, 3, 2),
                datetime(2023, 1, 1, 23, 5, 6),
                datetime(2023, 1, 1, 9),
                datetime(2023, 1, 1, 18),
            ),
        ],
    )
    def test_normalize_period(
        self,
        day_off_calendar,
        unnormalized_lower_datetime,
        unnormalized_upper_datetime,
        expected_lower_datetime,
        expected_upper_datetime,
    ):
        normalized_period = day_off_calendar.normalize_period(
            TimestamptzRange(
                lower=make_aware(unnormalized_lower_datetime, day_off_calendar.timezone),
                upper=make_aware(unnormalized_upper_datetime, day_off_calendar.timezone),
            )
        )
        assert normalized_period.lower == make_aware(expected_lower_datetime, day_off_calendar.timezone)
        assert normalized_period.upper == make_aware(expected_upper_datetime, day_off_calendar.timezone)


@pytest.mark.django_db
class TestDayOff:
    @pytest.mark.parametrize(
        "timezone_str, lower_time, upper_time",
        [
            ("Pacific/Kwajalein", time(9, 0, 0), time(18, 0, 0)),
            ("Europe/Berlin", time(9, 0, 0), time(18, 0, 0)),
            ("Europe/Berlin", time(15, 0, 0), time(16, 0, 0)),
        ],
    )
    def test_get_timespan(
        self,
        base_day_off_calendar_factory,
        default_daily_period_factory,
        day_off_factory,
        timezone_str,
        lower_time,
        upper_time,
    ):
        timezone = zoneinfo.ZoneInfo(timezone_str)
        calendar = base_day_off_calendar_factory.create(timezone=timezone)
        default_daily_period_factory.create(calendar=calendar, lower_time=lower_time, upper_time=upper_time)
        day_off = day_off_factory.create(calendar=calendar)
        assert day_off.period.lower == datetime.combine(day_off.date, lower_time, tzinfo=timezone).astimezone(
            zoneinfo.ZoneInfo("UTC")
        )
        assert day_off.period.upper == datetime.combine(day_off.date, upper_time, tzinfo=timezone).astimezone(
            zoneinfo.ZoneInfo("UTC")
        )
        #
        # timespan = day_off.get_timespan(as_utc=False)
        # assert timespan.lower == datetime.combine(day_off.date, lower_time, tzinfo=timezone)
        # assert timespan.upper == datetime.combine(day_off.date, upper_time, tzinfo=timezone)


@pytest.mark.django_db
class TestDefaultDailyPeriod:
    @pytest.mark.parametrize("val_date", [fake.date_object()])
    def test_get_lower_datetime(self, default_daily_period, val_date):
        assert default_daily_period.get_lower_datetime(val_date) == datetime.combine(
            val_date, default_daily_period.lower_time, tzinfo=default_daily_period.calendar.timezone
        ).astimezone(zoneinfo.ZoneInfo("UTC"))

    @pytest.mark.parametrize("val_date", [fake.date_object()])
    def test_get_upper_datetime(self, default_daily_period, val_date):
        assert default_daily_period.get_upper_datetime(val_date) == datetime.combine(
            val_date, default_daily_period.upper_time, tzinfo=default_daily_period.calendar.timezone
        ).astimezone(zoneinfo.ZoneInfo("UTC"))
