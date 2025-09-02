from datetime import date, timedelta

import pandas as pd
import pytest
from faker import Faker

from wbhuman_resources.models import EmployeeHumanResource

fake = Faker()


@pytest.mark.django_db
class TestUtil:
    @pytest.mark.parametrize("test_date", [(fake.date_object())])
    def test_get_employee_absence_periods_df(
        self,
        employee_human_resource,
        absence_request_periods_factory,
        day_off_factory,
        employee_weekly_off_periods_factory,
        test_date,
    ):
        # Basic utility coverage test. The underlying functions are already tested.
        p = absence_request_periods_factory.create(date=test_date, employee=employee_human_resource)
        w = employee_weekly_off_periods_factory.create(
            employee=employee_human_resource, weekday=(test_date + timedelta(days=1)).weekday()
        )
        day_off_factory.create(calendar=employee_human_resource.calendar, date=test_date + timedelta(days=2))
        res = EmployeeHumanResource.get_employee_absence_periods_df(
            employee_human_resource.calendar,
            (test_date - pd.tseries.offsets.Week(1)).date(),
            (test_date + pd.tseries.offsets.Week(1)).date(),
            EmployeeHumanResource.active_employees.all(),
        ).set_index(["employee", "period", "date", "type"])
        assert not res.loc[(employee_human_resource.id, p.default_period.id, test_date, "Vacation"), :].empty
        assert not res.loc[
            (employee_human_resource.id, w.period.id, test_date + timedelta(days=1), "Day Off"), :
        ].empty
        assert not res.loc[
            (
                employee_human_resource.id,
                employee_human_resource.calendar.default_periods.earliest("lower_time").id,
                test_date + timedelta(days=2),
                "Holiday",
            ),
            :,
        ].empty
        assert not res.loc[
            (
                employee_human_resource.id,
                employee_human_resource.calendar.default_periods.latest("lower_time").id,
                test_date + timedelta(days=2),
                "Holiday",
            ),
            :,
        ].empty
        with pytest.raises(KeyError):
            assert not res.loc[(employee_human_resource.id, 2, test_date + timedelta(days=3), "Holiday"), :].empty

    @pytest.mark.parametrize(
        "end_of_month_date",
        [
            (fake.date_between(date(2021, 1, 1), date(2021, 3, 31))),
            (fake.date_between(date(2021, 4, 1), date(2021, 12, 31))),
        ],
    )
    def test_get_end_of_month_employee_balance_report_df(
        self,
        employee_human_resource,
        employee_year_balance_factory,
        balance_hourly_allowance_factory,
        absence_request_periods_factory,
        end_of_month_date,
    ):
        end_of_month_date = (end_of_month_date + pd.tseries.offsets.MonthEnd(0)).date()
        previous_balance = employee_year_balance_factory.create(
            employee=employee_human_resource, year=end_of_month_date.year - 1, extra_balance=0
        )
        balance_hourly_allowance_factory.create(balance=previous_balance)

        current_balance = employee_year_balance_factory.create(
            employee=employee_human_resource, year=end_of_month_date.year, extra_balance=0
        )
        balance_hourly_allowance_factory.create(balance=current_balance)
        previous_period = absence_request_periods_factory.create(
            balance=previous_balance,
            employee=employee_human_resource,
            date=fake.date_between(date(end_of_month_date.year, 1, 1), end_of_month_date - timedelta(days=1)),
        )
        current_period = absence_request_periods_factory.create(
            balance=current_balance,
            employee=employee_human_resource,
            date=fake.date_between(previous_period.date, end_of_month_date),
        )

        res = EmployeeHumanResource.get_end_of_month_employee_balance_report_df(
            EmployeeHumanResource.active_employees.all(), end_of_month_date
        ).to_dict("records")[0]
        expected_total_balance = (
            current_balance.balance_in_days
            + previous_balance.total_vacation_hourly_balance_in_days
            + previous_balance.total_vacation_hourly_usage_in_days
        )
        expected_usage = (previous_period.total_hours + current_period.total_hours) / 8
        assert res == {
            "Employee": employee_human_resource.computed_str,
            "Total Balance": expected_total_balance,
            "End of Month Usage": expected_usage,
            "Available Balance End of Month": expected_total_balance - expected_usage,
        }
