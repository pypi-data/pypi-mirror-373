import zoneinfo
from datetime import date, datetime, time, timedelta

import pandas as pd
import pytest
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models
from dynamic_preferences.registries import global_preferences_registry
from faker import Faker
from psycopg.types.range import TimestamptzRange
from wbcore.contrib.directory.models import EmployerEmployeeRelationship

from wbhuman_resources.factories import (
    DayOffCalendarFactory,
    DayOffFactory,
    EmployeeYearBalanceFactory,
    TimeOffRequestFactory,
    VacationRequestFactory,
)
from wbhuman_resources.models.employee import (
    EmployeeHumanResource,
    EmployeeWeeklyOffPeriods,
    EmployeeYearBalance,
    post_save_employee,
)
from wbhuman_resources.models.preferences import (
    get_previous_year_balance_expiration_date,
)

this_year_minimum_date_to_consume_previous_year_balance = get_previous_year_balance_expiration_date(date.today().year)


fake = Faker()


@pytest.mark.django_db
class TestEmployeeHumanResource:
    # Permission base tests
    def test_get_administrators(self, employee_human_resource, user_factory):
        user_factory.create(is_superuser=True)  # superuser
        admin = user_factory.create()
        admin.user_permissions.add(Permission.objects.get(codename="administrate_absencerequest"))
        user_factory.create()  # normal_user
        assert set(EmployeeHumanResource.get_administrators()) == {admin}

    def test_is_administrator_super_user(self, user_factory):
        superuser = user_factory.create(is_superuser=True)
        assert EmployeeHumanResource.is_administrator(superuser)

    def test_is_administrator_normal_user(self, user):
        assert not EmployeeHumanResource.is_administrator(user)

    def test_is_administrator_user_with_permission(self, user_factory):
        admin = user_factory.create()
        admin.user_permissions.add(Permission.objects.get(codename="administrate_absencerequest"))
        assert EmployeeHumanResource.is_administrator(admin)

    def test_get_managed_employees(self, employee_human_resource_factory, position_factory):
        top_manager = employee_human_resource_factory.create()
        manager1 = employee_human_resource_factory.create()
        manager2 = employee_human_resource_factory.create()

        top_position = position_factory.create(manager=top_manager.profile)
        pos_1 = position_factory.create(parent=top_position, manager=manager1.profile)
        pos_2 = position_factory.create(parent=top_position, manager=manager2.profile)

        top_manager.position = top_position
        top_manager.save()
        manager1.position = pos_1
        manager1.save()
        manager2.position = pos_2
        manager2.save()

        top_employee = employee_human_resource_factory.create(position=top_position)
        employee_1 = employee_human_resource_factory.create(position=pos_1)
        employee_2 = employee_human_resource_factory.create(position=pos_2)

        employee_without_pos = employee_human_resource_factory.create(direct_manager=manager1.profile)
        top_manager_employees = {top_manager, manager1, manager2, top_employee, employee_1, employee_2}
        assert set(top_manager.get_managed_employees(include_self=False)) == {
            manager1,
            manager2,
            top_employee,
            employee_1,
            employee_2,
        }
        assert set(top_manager.get_managed_employees(include_self=True)) == top_manager_employees
        for managee in top_manager_employees:
            assert top_manager.is_manager_of(managee, include_self=True)

        manager1_employees = {employee_1, manager1, employee_without_pos}
        assert set(manager1.get_managed_employees(include_self=True)) == manager1_employees
        assert set(manager1.get_managed_employees(include_self=False)) == {employee_1, employee_without_pos}
        for managee in manager1_employees:
            assert manager1.is_manager_of(managee, include_self=True)

        manager2_employees = {employee_2, manager2}
        assert set(manager2.get_managed_employees(include_self=True)) == manager2_employees
        assert set(manager2.get_managed_employees(include_self=False)) == {employee_2}
        for managee in manager2_employees:
            assert manager2.is_manager_of(managee, include_self=True)

        assert not employee_1.get_managed_employees(include_self=False).exists()
        assert not employee_2.get_managed_employees(include_self=False).exists()
        assert not employee_without_pos.get_managed_employees(include_self=False).exists()

    def test_get_managers(self, position_factory, employee_human_resource_factory):
        position_manager = employee_human_resource_factory.create()
        main_manager = employee_human_resource_factory.create()

        position = position_factory.create(manager=position_manager.profile)
        assert (
            next(
                employee_human_resource_factory.create(
                    direct_manager=main_manager.profile, position=position
                ).get_managers()
            )
            == main_manager.profile
        )
        assert (
            next(employee_human_resource_factory.create(direct_manager=None, position=position).get_managers())
            == position_manager.profile
        )
        with pytest.raises(StopIteration):
            next(employee_human_resource_factory.create(direct_manager=None, position=None).get_managers())

    def test_get_managers_with_global_manager(
        self, authenticated_person_factory, position_factory, employee_human_resource_factory
    ):
        global_manager_permission = Permission.objects.get(
            codename="administrate_employeehumanresource",
            content_type=ContentType.objects.get_for_model(EmployeeHumanResource),
        )
        administrate_employeehumanresource = authenticated_person_factory.create()
        administrate_employeehumanresource.user_account.user_permissions.add(global_manager_permission)
        assert (
            next(employee_human_resource_factory.create(direct_manager=None, position=None).get_managers())
            == administrate_employeehumanresource
        )

    @pytest.mark.parametrize("val_date", [(fake.date_this_decade())])
    def test_deactivate(self, employee_human_resource_factory, val_date):
        employee = employee_human_resource_factory.create(enrollment_at=val_date)
        employee.deactivate(disenrollment_date=date(val_date.year, 12, 31))
        assert not employee.is_active
        assert not employee.profile.user_account.is_active
        balance = employee.balances.get(year=val_date.year)
        assert balance.monthly_allowances.count() == 1

    def test_assign_unassign_position_groups(self, employee_human_resource):
        assert not employee_human_resource.profile.user_account.groups.exists()
        employee_human_resource.assign_position_groups()
        assert employee_human_resource.profile.user_account.groups.filter(
            id=employee_human_resource.position.groups.first().id
        ).exists()
        employee_human_resource.unassign_position_groups()
        assert not employee_human_resource.profile.user_account.groups.exists()

    # Balance & Usage tests
    def test_post_save_employee(self, employee_human_resource, company):
        # Set main CRM company
        global_preferences_registry.manager()["directory__main_company"] = company.id
        global_preferences_registry.manager().cache.clear()

        post_save_employee("SENDER ", employee_human_resource, created=True)

        # Expect the weekend days to be labeled as off period by default
        assert EmployeeWeeklyOffPeriods.objects.filter(employee=employee_human_resource, weekday=5).count() == 2
        assert EmployeeWeeklyOffPeriods.objects.filter(employee=employee_human_resource, weekday=6).count() == 2

        # Expect the employee to have balance and monthly allowance for at its enrolment year
        balance = employee_human_resource.balances.get(year=employee_human_resource.enrollment_at.year)
        assert balance.monthly_allowances.count() == 1

        # Expect the CRM position to reflect the
        assert EmployerEmployeeRelationship.objects.filter(
            employee=employee_human_resource.profile,
            employer=company,
            primary=True,
            position__title=employee_human_resource.position.name,
        ).exists()
        assert employee_human_resource.profile.user_account.groups.filter(
            id=employee_human_resource.position.groups.first().id
        ).exists()

    @pytest.mark.parametrize("start_date", [(fake.date_object())])
    def test_extract_workable_periods_basic_usage(
        self, employee_human_resource, start_date, day_off_factory, employee_weekly_off_periods_factory
    ):
        end_date = start_date + timedelta(days=7)
        start_datetime = datetime.combine(start_date, time(0, 0, 0)).astimezone(zoneinfo.ZoneInfo("UTC"))
        end_datetime = datetime.combine(end_date, time(23, 59, 59)).astimezone(zoneinfo.ZoneInfo("UTC"))
        day_off = day_off_factory.create(
            calendar=employee_human_resource.calendar, date=fake.date_between(start_date, end_date)
        )
        period_off = employee_weekly_off_periods_factory.create(employee=employee_human_resource)
        res = set(employee_human_resource.extract_workable_periods(start_datetime, end_datetime))
        expected_res = set()
        for i in range(8):
            _d = start_date + timedelta(days=i)
            if day_off.date != _d:
                for period in employee_human_resource.calendar.default_periods.all():
                    if period_off.period != period or period_off.weekday != _d.weekday():
                        expected_res.add((_d, period))
        assert expected_res == res

    def test_assign_vacation_allowance_from_range(self, employee_human_resource):
        pass

    @pytest.mark.parametrize("year_str", [(fake.year())])
    def test_get_or_create_balance(self, employee_human_resource, year_str):
        assert employee_human_resource.get_or_create_balance(int(year_str))[0].year == int(year_str)


@pytest.mark.django_db
class TestEmployeeYearBalance:
    @pytest.fixture
    def test_args(self, start_date):
        balance = EmployeeYearBalanceFactory.create(year=start_date.year)
        default_period1 = balance.employee.calendar.default_periods.earliest("lower_time")
        default_period2 = balance.employee.calendar.default_periods.latest("lower_time")

        start_r2 = fake.date_between_dates(start_date, date(balance.year, 12, 31))
        start_r3 = fake.date_between_dates(date(balance.year, 1, 1), start_date)
        vacation_request1 = VacationRequestFactory.create(
            employee=balance.employee,
            period=TimestamptzRange(
                default_period1.get_lower_datetime(start_date),
                default_period2.get_upper_datetime(start_date) + timedelta(days=2),
            ),
        )
        vacation_request2 = VacationRequestFactory.create(
            employee=balance.employee,
            period=TimestamptzRange(
                default_period1.get_lower_datetime(start_r2),
                default_period2.get_upper_datetime(start_r2) + timedelta(days=2),
            ),
        )
        timeoff_request = TimeOffRequestFactory.create(
            employee=balance.employee,
            period=TimestamptzRange(
                default_period1.get_lower_datetime(start_r3),
                default_period2.get_upper_datetime(start_r3) + timedelta(days=2),
            ),
        )

        mandatatory_day_off = DayOffFactory.create(
            calendar=balance.employee.calendar,
            count_as_holiday=False,
            date=fake.date_between_dates(date(balance.year, 1, 5), date(balance.year, 12, 31)),
        )
        DayOffFactory.create(
            calendar=DayOffCalendarFactory.create(title="other calendar", resource="other.resource"),
            count_as_holiday=False,
            date=fake.date_between_dates(date(balance.year, 1, 5), date(balance.year, 12, 31)),
        )  # Other calendar
        return (
            balance,
            default_period1,
            default_period2,
            vacation_request1,
            vacation_request2,
            timeoff_request,
            mandatatory_day_off,
        )

    # test properties
    @pytest.mark.parametrize("start_date", [(fake.date_this_year())])
    def test_balance(self, test_args, start_date):
        [
            balance,
            default_period1,
            default_period2,
            vacation_request1,
            vacation_request2,
            timeoff_request,
            mandatatory_day_off,
        ] = test_args
        expected_res = (
            balance.extra_balance + balance.monthly_allowances.aggregate(s=models.Sum("hourly_allowance"))["s"]
        )
        assert balance.balance == expected_res
        assert EmployeeYearBalance.objects.get(id=balance.id)._balance == expected_res

    @pytest.mark.parametrize("start_date", [(fake.date_this_year())])
    def test_daily_hours(self, test_args, start_date):
        [
            balance,
            default_period1,
            default_period2,
            vacation_request1,
            vacation_request2,
            timeoff_request,
            mandatatory_day_off,
        ] = test_args

        expected_res = default_period1.total_hours + default_period2.total_hours
        assert balance.daily_hours == expected_res
        assert EmployeeYearBalance.objects.get(id=balance.id)._daily_hours == expected_res

    @pytest.mark.parametrize("start_date", [(fake.date_this_year())])
    def test_number_mandatory_days_off_in_days(self, test_args, start_date):
        [
            balance,
            default_period1,
            default_period2,
            vacation_request1,
            vacation_request2,
            timeoff_request,
            mandatatory_day_off,
        ] = test_args
        expected_res = 1
        assert balance.number_mandatory_days_off_in_days == expected_res
        assert EmployeeYearBalance.objects.get(id=balance.id)._number_mandatory_days_off_in_days == expected_res

    @pytest.mark.parametrize("start_date", [(fake.date_this_year())])
    def test_number_mandatory_days_off(self, test_args, start_date):
        [
            balance,
            default_period1,
            default_period2,
            vacation_request1,
            vacation_request2,
            timeoff_request,
            mandatatory_day_off,
        ] = test_args
        expected_res = balance.employee.calendar.get_daily_hours()
        assert balance.number_mandatory_days_off == expected_res
        assert EmployeeYearBalance.objects.get(id=balance.id)._number_mandatory_days_off == expected_res

    @pytest.mark.parametrize("start_date", [(fake.date_this_year())])
    def test_total_vacation_hourly_usage(self, test_args, start_date):
        [
            balance,
            default_period1,
            default_period2,
            vacation_request1,
            vacation_request2,
            timeoff_request,
            mandatatory_day_off,
        ] = test_args
        expected_res = vacation_request1.total_hours + vacation_request2.total_hours
        assert balance.total_vacation_hourly_usage == expected_res
        assert EmployeeYearBalance.objects.get(id=balance.id)._total_vacation_hourly_usage == expected_res

    @pytest.mark.parametrize("start_date", [(fake.date_this_year())])
    def test_total_vacation_hourly_balance(self, test_args, start_date):
        [
            balance,
            default_period1,
            default_period2,
            vacation_request1,
            vacation_request2,
            timeoff_request,
            mandatatory_day_off,
        ] = test_args

        expected_res = (
            balance.extra_balance
            + balance.monthly_allowances.aggregate(s=models.Sum("hourly_allowance"))["s"]
            - vacation_request1.total_hours
            - vacation_request2.total_hours
            - balance.employee.calendar.get_daily_hours()
        )
        assert balance.total_vacation_hourly_balance == expected_res
        assert EmployeeYearBalance.objects.get(id=balance.id)._total_vacation_hourly_balance == expected_res

    @pytest.mark.parametrize("start_date", [(fake.date_this_year())])
    def test_balance_in_days(self, test_args, start_date):
        [
            balance,
            default_period1,
            default_period2,
            vacation_request1,
            vacation_request2,
            timeoff_request,
            mandatatory_day_off,
        ] = test_args
        expected_res = (
            balance.extra_balance + balance.monthly_allowances.aggregate(s=models.Sum("hourly_allowance"))["s"]
        ) / balance.employee.calendar.get_daily_hours()
        assert balance.balance_in_days == expected_res
        assert EmployeeYearBalance.objects.get(id=balance.id)._balance_in_days == expected_res

    @pytest.mark.parametrize("start_date", [(fake.date_this_year())])
    def test_total_vacation_hourly_usage_in_days(self, test_args, start_date):
        [
            balance,
            default_period1,
            default_period2,
            vacation_request1,
            vacation_request2,
            timeoff_request,
            mandatatory_day_off,
        ] = test_args
        expected_res = (
            vacation_request1.total_hours + vacation_request2.total_hours
        ) / balance.employee.calendar.get_daily_hours()
        assert balance.total_vacation_hourly_usage_in_days == expected_res
        assert EmployeeYearBalance.objects.get(id=balance.id)._total_vacation_hourly_usage_in_days == expected_res

    @pytest.mark.parametrize("start_date", [(fake.date_this_year())])
    def test_total_vacation_hourly_balance_in_days(self, test_args, start_date):
        [
            balance,
            default_period1,
            default_period2,
            vacation_request1,
            vacation_request2,
            timeoff_request,
            mandatatory_day_off,
        ] = test_args
        expected_res = (
            balance.extra_balance
            + balance.monthly_allowances.aggregate(s=models.Sum("hourly_allowance"))["s"]
            - vacation_request1.total_hours
            - vacation_request2.total_hours
            - balance.employee.calendar.get_daily_hours()
        ) / balance.employee.calendar.get_daily_hours()

        assert balance.total_vacation_hourly_balance_in_days == expected_res
        assert EmployeeYearBalance.objects.get(id=balance.id)._total_vacation_hourly_balance_in_days == expected_res


@pytest.mark.django_db
class TestEmployeeWeeklyOffPeriods:
    @pytest.mark.parametrize("test_date", [(fake.date_this_year())])
    def get_timespan(self, employee_weekly_off_periods, test_date):
        timespan = employee_weekly_off_periods.get_timespan(test_date)
        assert timespan.lower == employee_weekly_off_periods.period.get_lower_datetime(test_date)
        assert timespan.upper == employee_weekly_off_periods.period.get_upper_datetime(test_date)

    @pytest.mark.parametrize("test_date", [(fake.date_this_year())])
    def test_get_employee_weekly_periods_df(
        self, day_off_calendar, employee_human_resource_factory, employee_weekly_off_periods_factory, test_date
    ):
        test_date = (test_date - pd.tseries.offsets.Week(weekday=0)).date()
        employee1 = employee_human_resource_factory.create(calendar=day_off_calendar, is_active=True)
        employee2 = employee_human_resource_factory.create(calendar=day_off_calendar, is_active=True)
        employee3 = employee_human_resource_factory.create(
            calendar=day_off_calendar, is_active=False
        )  # Expect this employee to not be present

        period1 = employee_weekly_off_periods_factory.create(employee=employee1)
        period2 = employee_weekly_off_periods_factory.create(employee=employee2)
        period3 = employee_weekly_off_periods_factory.create(employee=employee3)
        res = EmployeeWeeklyOffPeriods.get_employee_weekly_periods_df(
            test_date, test_date + timedelta(days=7), employee__is_active=True
        )
        assert res.shape == (2, 5)
        res = res.set_index(["employee", "period", "date"])
        assert res.loc[
            (employee1.id, period1.period.id, test_date + timedelta(days=period1.weekday)), :
        ].values.tolist() == ["APPROVED", "Day Off"]
        assert res.loc[
            (employee2.id, period2.period.id, test_date + timedelta(days=period2.weekday)), :
        ].values.tolist() == ["APPROVED", "Day Off"]
        with pytest.raises(KeyError):
            assert res.loc[(employee3.id, period3.period.id, test_date + timedelta(days=period3.weekday)), :]


@pytest.mark.django_db
class TestPosition:
    def test_change_group_in_position_change_user_groups(self, employee_human_resource):
        employee_human_resource.assign_position_groups()
        position = employee_human_resource.position
        first_group = position.groups.first()
        second_group = Group.objects.create(name="second group")

        assert set(employee_human_resource.profile.user_account.groups.all()) == {first_group}

        position.groups.add(second_group)
        assert set(employee_human_resource.profile.user_account.groups.all()) == {first_group, second_group}

        position.groups.remove(second_group)
        assert set(employee_human_resource.profile.user_account.groups.all()) == {first_group}

        position.groups.remove(first_group)
        assert set(employee_human_resource.profile.user_account.groups.all()) == set()

    def test_get_employees(self, position_factory, employee_human_resource_factory):
        root_1 = position_factory.create()
        e_root_1 = employee_human_resource_factory.create(position=root_1)
        child_1 = position_factory.create(parent=root_1)
        e_child_1 = employee_human_resource_factory.create(position=child_1)
        employee_human_resource_factory.create(
            position=child_1, is_active=False
        )  # Unactive employee, shouldn't show in the method

        root_2 = position_factory.create()
        e_root_2 = employee_human_resource_factory.create(position=root_2)
        child_2 = position_factory.create(parent=root_2)
        e_child_2 = employee_human_resource_factory.create(position=child_2)
        employee_human_resource_factory.create(
            position=child_2, is_active=False
        )  # Unactive employee, shouldn't show in the method

        assert {*root_1.get_employees().values_list("id", flat=True)} == {e_root_1.id, e_child_1.id}
        assert {*child_1.get_employees().values_list("id", flat=True)} == {e_child_1.id}
        assert {*root_2.get_employees().values_list("id", flat=True)} == {e_root_2.id, e_child_2.id}
        assert {*child_2.get_employees().values_list("id", flat=True)} == {e_child_2.id}
