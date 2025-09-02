import zoneinfo
from datetime import date, timedelta
from unittest.mock import patch

import pandas as pd
import pytest
from django.contrib.auth.models import Group, Permission
from django.db.models import Sum
from faker import Faker
from psycopg.types.range import TimestamptzRange

from wbhuman_resources.models import (
    AbsenceRequest,
    AbsenceRequestPeriods,
    AbsenceRequestType,
    BalanceHourlyAllowance,
)
from wbhuman_resources.models.absence import (
    can_cancel_request,
    can_validate_or_deny_request,
)
from wbhuman_resources.models.preferences import (
    get_previous_year_balance_expiration_date,
)

fake = Faker()


@pytest.mark.django_db
class TestAbsenceRequest:
    @pytest.fixture()
    def past_aware_datetime(self):
        return fake.past_datetime().astimezone(zoneinfo.ZoneInfo("UTC"))

    @pytest.fixture()
    def future_aware_datetime(self):
        return fake.future_datetime().astimezone(zoneinfo.ZoneInfo("UTC"))

    def test_normal_user_cannot_cancel_past_request(self, vacation_request_factory, past_aware_datetime):
        request = vacation_request_factory(
            status=AbsenceRequest.Status.APPROVED,
            period=TimestamptzRange(lower=past_aware_datetime - timedelta(days=2), upper=past_aware_datetime),
        )
        assert not can_cancel_request(request, request.employee.profile.user_account)

    def test_normal_user_can_cancel_future_request(
        self, vacation_request_factory, user_factory, future_aware_datetime, employee_human_resource_factory
    ):
        admin = user_factory.create(is_active=True)
        admin.user_permissions.add(Permission.objects.get(codename="administrate_absencerequest"))
        manager = employee_human_resource_factory.create()

        employee = employee_human_resource_factory.create(direct_manager=manager.profile)
        request = vacation_request_factory(
            employee=employee,
            status=AbsenceRequest.Status.APPROVED,
            period=TimestamptzRange(lower=future_aware_datetime, upper=future_aware_datetime + timedelta(days=2)),
        )

        assert can_cancel_request(request, request.employee.profile.user_account)
        assert can_cancel_request(request, admin)
        assert can_cancel_request(request, manager.profile.user_account)

    def test_can_validate_or_deny_request(
        self, vacation_request_factory, user_factory, future_aware_datetime, employee_human_resource_factory
    ):
        admin = user_factory.create(is_active=True)
        admin.user_permissions.add(Permission.objects.get(codename="administrate_absencerequest"))
        manager = employee_human_resource_factory.create()

        employee = employee_human_resource_factory.create(direct_manager=manager.profile)
        request = vacation_request_factory(
            employee=employee,
            status=AbsenceRequest.Status.APPROVED,
            period=TimestamptzRange(lower=future_aware_datetime, upper=future_aware_datetime + timedelta(days=2)),
        )

        assert not can_validate_or_deny_request(request, request.employee.profile.user_account)
        assert can_validate_or_deny_request(request, admin)
        assert can_validate_or_deny_request(request, manager.profile.user_account)

    def test_submit(self, absence_request_factory, employee_human_resource):
        request = absence_request_factory.create(status=AbsenceRequest.Status.DRAFT)
        request.employee.direct_manager = employee_human_resource.profile
        request.employee.save()

        request.submit()
        request.save()
        assert request.status == AbsenceRequest.Status.PENDING

    def test_approve(self, absence_request_factory):
        request = absence_request_factory.create(status=AbsenceRequest.Status.PENDING)

        request.approve()
        request.save()
        assert request.status == AbsenceRequest.Status.APPROVED

    def test_deny_not_vacation_request(self, time_off_request_factory):
        request = time_off_request_factory.create(status=AbsenceRequest.Status.PENDING)
        request.deny()
        request.save()
        assert request.status == AbsenceRequest.Status.DENIED

    def test_deny_vacation_request(self, vacation_request_factory):
        request = vacation_request_factory.create(status=AbsenceRequest.Status.PENDING)
        request.deny()
        request.save()
        assert request.status == AbsenceRequest.Status.DENIED

    def test_backtodraft(self, absence_request_factory):
        request = absence_request_factory.create(status=AbsenceRequest.Status.PENDING)
        request.backtodraft()
        request.save()
        assert request.status == AbsenceRequest.Status.DRAFT

    def test_cancel(self, absence_request_factory, employee_human_resource):
        request = absence_request_factory.create(status=AbsenceRequest.Status.APPROVED)
        request.employee.direct_manager = employee_human_resource.profile
        request.employee.save()

        request.cancel()
        request.save()
        assert request.status == AbsenceRequest.Status.CANCELLED

    def test_timespan(self, absence_request_periods):
        request = absence_request_periods.request
        assert (
            request.periods_timespan.lower
            == request.periods.earliest("timespan__startswith").request.periods_timespan.lower
        )
        assert (
            request.periods_timespan.upper
            == request.periods.latest("timespan__startswith").request.periods_timespan.upper
        )

    def test_can_delete_draft_request(self, absence_request_factory, user):
        request = absence_request_factory(status=AbsenceRequest.Status.DRAFT)
        assert request.is_deletable_for_user(user)

    def test_can_delete_future_pending_request(self, absence_request_factory, future_aware_datetime, user):
        request = absence_request_factory(
            status=AbsenceRequest.Status.PENDING,
            period=TimestamptzRange(lower=future_aware_datetime, upper=future_aware_datetime + timedelta(days=2)),
        )
        assert request.is_deletable_for_user(user)

    def test_can_delete_past_pending_request(self, absence_request_factory, past_aware_datetime, user_factory):
        normal_user = user_factory.create()
        admin_user = user_factory.create()
        admin_user.user_permissions.add(Permission.objects.get(codename="administrate_absencerequest"))
        request = absence_request_factory.create(
            status=AbsenceRequest.Status.PENDING,
            period=TimestamptzRange(lower=past_aware_datetime - timedelta(days=2), upper=past_aware_datetime),
        )
        assert not request.is_deletable_for_user(normal_user)
        assert request.is_deletable_for_user(admin_user)

    # Property checks and test
    def test_total_hours(self, day_off_calendar, absence_request_periods_factory):
        morning = day_off_calendar.default_periods.earliest("lower_time")
        afternoon = day_off_calendar.default_periods.latest("lower_time")
        p1 = absence_request_periods_factory.create(default_period=morning)
        request = p1.request
        absence_request_periods_factory.create(request=request, default_period=afternoon, date=p1.date)
        assert request.total_hours == morning.total_hours + afternoon.total_hours
        assert AbsenceRequest.objects.get(id=request.id)._total_hours == morning.total_hours + afternoon.total_hours
        absence_request_periods_factory.create(
            request=request, default_period=morning, date=(p1.date + pd.tseries.offsets.BDay(1)).date()
        )
        absence_request_periods_factory.create(
            request=request, default_period=afternoon, date=(p1.date + pd.tseries.offsets.BDay(1)).date()
        )
        assert request.total_hours == (morning.total_hours + afternoon.total_hours) * 2
        assert (
            AbsenceRequest.objects.get(id=request.id)._total_hours == (morning.total_hours + afternoon.total_hours) * 2
        )

    def test_total_vacation_hours(self, absence_request_factory, absence_request_type_factory):
        time_off_request = absence_request_factory.create(
            status=AbsenceRequest.Status.APPROVED, type=absence_request_type_factory.create(is_vacation=False)
        )
        vacation_request = absence_request_factory.create(
            status=AbsenceRequest.Status.APPROVED, type=absence_request_type_factory.create(is_vacation=True)
        )
        unapprove_vacation_request = absence_request_factory.create(
            type=absence_request_type_factory.create(is_vacation=True)
        )

        assert time_off_request.total_vacation_hours == 0
        assert AbsenceRequest.objects.get(id=time_off_request.id)._total_vacation_hours == 0

        assert unapprove_vacation_request.total_vacation_hours == 0
        assert AbsenceRequest.objects.get(id=unapprove_vacation_request.id)._total_vacation_hours == 0

        assert vacation_request.total_vacation_hours
        assert vacation_request.total_vacation_hours == vacation_request.periods.aggregate(s=Sum("_total_hours"))["s"]
        assert (
            AbsenceRequest.objects.get(id=vacation_request.id)._total_vacation_hours
            == vacation_request.total_vacation_hours
        )

    def test_total_hours_in_days(self, absence_request):
        exp_res = (
            absence_request.periods.aggregate(s=Sum("_total_hours"))["s"]
            / absence_request.employee.calendar.get_daily_hours()
        )
        assert exp_res
        assert absence_request.total_hours_in_days == exp_res
        assert AbsenceRequest.objects.get(id=absence_request.id)._total_hours_in_days == exp_res

    def test_total_vacation_hours_in_days(self, absence_request_factory, absence_request_type_factory):
        vacation_request = absence_request_factory.create(
            status=AbsenceRequest.Status.APPROVED, type=absence_request_type_factory.create(is_vacation=True)
        )
        assert vacation_request.total_vacation_hours_in_days
        assert (
            vacation_request.total_vacation_hours_in_days
            == vacation_request.periods.aggregate(s=Sum("_total_hours"))["s"]
            / vacation_request.employee.calendar.get_daily_hours()
        )
        assert (
            AbsenceRequest.objects.get(id=vacation_request.id)._total_vacation_hours_in_days
            == vacation_request.total_vacation_hours_in_days
        )

    @patch("wbhuman_resources.models.absence.send_notification")
    def test_notify_requester(self, mock_fct, absence_request):
        title = fake.sentence()
        message = fake.sentence()
        absence_request.notify(title, message, to_requester=True)
        mock_fct.assert_called_with(
            code="wbhuman_resources.absencerequest.notify",
            title=title,
            body=message,
            reverse_name="wbhuman_resources:absencerequest-detail",
            reverse_args=[absence_request.id],
            user=absence_request.employee.profile.user_account,
        )

    @patch("wbhuman_resources.models.absence.send_notification")
    def test_notify_managers(self, mock_fct, absence_request, authenticated_person_factory):
        direct_manager = authenticated_person_factory.create()
        absence_request.employee.direct_manager = direct_manager
        absence_request.employee.save()

        # add a general manager
        general_manager = authenticated_person_factory.create()
        general_manager.user_account.user_permissions.add(
            Permission.objects.get(codename="administrate_employeehumanresource")
        )

        absence_request.refresh_from_db()

        title = fake.sentence()
        message = fake.sentence()
        absence_request.notify(title, message, to_requester=False, to_manager=True)
        mock_fct.assert_any_call(
            code="wbhuman_resources.absencerequest.notify",
            title=title,
            body=message,
            reverse_name="wbhuman_resources:absencerequest-detail",
            reverse_args=[absence_request.id],
            user=general_manager.user_account,
        )
        mock_fct.assert_any_call(
            code="wbhuman_resources.absencerequest.notify",
            title=title,
            body=message,
            reverse_name="wbhuman_resources:absencerequest-detail",
            reverse_args=[absence_request.id],
            user=direct_manager.user_account,
        )

    @patch("wbhuman_resources.models.absence.send_notification")
    def test_notify_extra_notify_user(self, mock_fct, absence_request, user):
        # We create a user, add it to a test group and add this group to the absence request type "extra_notify_group"
        group = Group.objects.create(name="test")
        user.groups.add(group)
        absence_request.type.extra_notify_groups.add(group)
        absence_request.refresh_from_db()

        title = fake.sentence()
        message = fake.sentence()
        absence_request.notify(title, message, to_requester=False, to_manager=True)
        mock_fct.assert_called_with(
            code="wbhuman_resources.absencerequest.notify",
            title=title,
            body=message,
            reverse_name="wbhuman_resources:absencerequest-detail",
            reverse_args=[absence_request.id],
            user=user,
        )


@pytest.mark.django_db
class TestAbsenceRequestType:
    def test_get_choices(self, absence_request_type_factory):
        t1 = absence_request_type_factory.create()
        t2 = absence_request_type_factory.create()
        assert AbsenceRequestType.get_choices() == [(t1.id, t1.title), (t2.id, t2.title)]

    def test_validate_country_needed_but_not_specified(self, absence_request_type_factory):
        absence_request_type = absence_request_type_factory.create(is_country_necessary=True)
        with pytest.raises(ValueError):
            absence_request_type.validate_country(None)

    def test_validate_country_specified_and_allowed(self, absence_request_type_factory, country):
        absence_request_type = absence_request_type_factory.create(
            is_country_necessary=True,
        )  # test that the post_save automatically appends the newly created country to the list of allowed countries
        assert absence_request_type.validate_country(country)

    def test_validate_country_specified_but_not_allowed(self, absence_request_type_factory, country):
        absence_request_type = absence_request_type_factory.create(is_country_necessary=True)
        absence_request_type.crossborder_countries.clear()
        with pytest.raises(ValueError):
            absence_request_type.validate_country(country)


@pytest.mark.django_db
class TestAbsenceRequestPeriod:
    def test_total_hours(self, absence_request_periods):
        exp_res = absence_request_periods.default_period.total_hours
        assert exp_res
        assert absence_request_periods.total_hours == exp_res
        assert AbsenceRequestPeriods.objects.get(id=absence_request_periods.id)._total_hours == exp_res

    @pytest.mark.parametrize("past_date,future_date", [(fake.past_date(), fake.future_date())])
    def test_previous_vacation_period(self, absence_request_periods_factory, past_date, future_date):
        current = absence_request_periods_factory.create(date=date.today())
        past = absence_request_periods_factory.create(employee=current.employee, date=past_date)
        future = absence_request_periods_factory.create(employee=current.employee, date=future_date)
        AbsenceRequest.objects.update(status=AbsenceRequest.Status.APPROVED, type=current.request.type)
        assert current.previous_period == past
        assert future.previous_period == current
        assert past.previous_period is None

    @pytest.mark.parametrize("test_date", [(fake.date_this_year())])
    def test_get_periods_as_df(
        self, day_off_calendar, employee_human_resource_factory, absence_request_periods_factory, test_date
    ):
        employee1 = employee_human_resource_factory.create(calendar=day_off_calendar, is_active=True)
        employee2 = employee_human_resource_factory.create(
            calendar=day_off_calendar, is_active=False
        )  # Expect this employee to not be present
        p1 = absence_request_periods_factory.create(employee=employee1, date=test_date)
        p2 = absence_request_periods_factory.create(employee=employee2, date=test_date)
        p3 = absence_request_periods_factory.create(employee=employee1, date=test_date - timedelta(days=1))
        res = AbsenceRequestPeriods.get_periods_as_df(
            test_date, test_date + timedelta(days=1), employee__is_active=True
        )
        assert res.shape == (1, 5)
        res = res.set_index(["employee", "period", "date"])
        assert res.loc[(employee1.id, p1.default_period.id, test_date), :].values.tolist() == [
            p1.request.type.title,
            p1.request.status,
        ]

        with pytest.raises(KeyError):
            assert res.loc[(employee2.id, p2.default_period.id, test_date), :].values.tolist() == [
                p2.request.type.title,
                p2.request.status,
            ]
            assert res.loc[(employee1.id, p3.period.id, test_date - timedelta(days=1)), :]

    @pytest.mark.parametrize("year_str", [(fake.year())])
    def test_assign_balance(
        self, employee_human_resource, absence_request_periods_factory, employee_year_balance_factory, year_str
    ):
        year = int(year_str)
        previous_balance = employee_year_balance_factory.create(
            employee=employee_human_resource, extra_balance=0, year=year - 1
        )
        current_balance = employee_year_balance_factory.create(
            employee=employee_human_resource, extra_balance=0, year=year
        )
        next_balance = employee_year_balance_factory.create(
            employee=employee_human_resource, extra_balance=0, year=year + 1
        )
        BalanceHourlyAllowance.objects.update(
            hourly_allowance=4
        )  # Update all created balance allowance with 4 crdits (corresponds to a period)

        p1 = absence_request_periods_factory.create(
            balance=None, employee=employee_human_resource, date=fake.date_between(date(year, 1, 1), date(year, 3, 31))
        )
        p1.assign_balance()
        assert p1.balance == previous_balance

        p2 = absence_request_periods_factory.create(
            balance=None,
            employee=employee_human_resource,
            date=fake.date_between(date(year, 3, 31), date(year, 6, 30)),
        )
        p2.assign_balance()
        assert p2.balance == current_balance

        p3 = absence_request_periods_factory.create(
            balance=None,
            employee=employee_human_resource,
            date=fake.date_between(date(year, 6, 30), date(year, 12, 31)),
        )
        p3.assign_balance()
        assert p3.balance == next_balance

        p4 = absence_request_periods_factory.create(  # request but no balance left
            balance=None,
            employee=employee_human_resource,
            date=fake.date_between(date(year, 1, 1), date(year, 12, 31)),
        )
        p4.assign_balance()
        assert p4.balance.year == year + 2

    @pytest.mark.parametrize("year_str", [(fake.year())])
    def test_assign_balance_with_expired_balance(
        self, employee_human_resource, absence_request_periods_factory, employee_year_balance_factory, year_str
    ):
        year = int(year_str)
        expiration_date = get_previous_year_balance_expiration_date(year)

        for y in range(year, expiration_date.year - 1):
            employee_year_balance_factory.create(employee=employee_human_resource, extra_balance=0, year=y)
        BalanceHourlyAllowance.objects.filter(balance__year=year).update(
            hourly_allowance=4
        )  # Update all created balance allowance with 4 crdits (corresponds to a period)
        BalanceHourlyAllowance.objects.exclude(balance__year=year).update(
            hourly_allowance=0
        )  # and set anything else to 0
        p1 = absence_request_periods_factory.create(
            balance=None,
            employee=employee_human_resource,
            date=fake.date_between(expiration_date, date(expiration_date.year, 12, 31)),
        )
        p1.assign_balance()
        assert p1.balance is not None
        assert p1.balance.year == year + 1
        assert p1.balance.balance == 0

    def test_no_vacation_or_approved_request_has_no_balance(self, absence_request_periods):
        AbsenceRequest.objects.update(status=AbsenceRequest.Status.DRAFT)
        AbsenceRequestType.objects.update(is_vacation=False)
        AbsenceRequestPeriods.objects.update(balance=None)
        absence_request_periods.refresh_from_db()
        absence_request_periods.assign_balance()
        assert absence_request_periods.balance is None

    def test_get_consecutive_hours_count(
        self,
        absence_request_periods_factory,
        employee_human_resource,
        employee_weekly_off_periods_factory,
        day_off_factory,
    ):
        morning = employee_human_resource.calendar.default_periods.earliest("lower_time")
        afternoon = employee_human_resource.calendar.default_periods.latest("lower_time")
        hours_per_period = 4
        p1 = absence_request_periods_factory.create(employee=employee_human_resource, default_period=morning)
        assert p1.consecutive_hours_count == hours_per_period
        p2 = absence_request_periods_factory.create(
            date=p1.date, employee=employee_human_resource, default_period=afternoon
        )  # Straight next period, counter should be incremented
        assert p2.consecutive_hours_count == hours_per_period * 2
        employee_weekly_off_periods_factory.create(
            period=morning, weekday=(p1.date.weekday() + 1) % 6, employee=employee_human_resource
        )
        p3 = absence_request_periods_factory.create(
            date=p1.date + timedelta(days=1), employee=employee_human_resource, default_period=afternoon
        )  # Expected to keep incremeting counter because the previous employee's weekly day off period is jumped
        assert p3.consecutive_hours_count == hours_per_period * 3
        day_off_factory.create(calendar=employee_human_resource.calendar, date=p1.date + timedelta(days=2))
        p4 = absence_request_periods_factory.create(
            date=p1.date + timedelta(days=3), employee=employee_human_resource, default_period=morning
        )  # Expected to keep incremeting counter because the previous day off is jumped
        assert p4.consecutive_hours_count == hours_per_period * 4
        p5 = absence_request_periods_factory.create(
            date=p1.date + timedelta(days=4), employee=employee_human_resource, default_period=morning
        )
        assert p5.consecutive_hours_count == hours_per_period  # Expect  reset of counter
