from datetime import date
from unittest.mock import patch

import pandas as pd
import pytest
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from dynamic_preferences.registries import global_preferences_registry
from faker import Faker

from wbhuman_resources.models import AbsenceRequest
from wbhuman_resources.models.employee import EmployeeHumanResource
from wbhuman_resources.tasks import assign_balance, send_mail_to_accounting

fake = Faker()


@pytest.mark.django_db
class TestHumanResourceTasks:
    @pytest.mark.parametrize("accounting_email_1,accounting_email_2", [(fake.email(), fake.email())])
    @patch.object(EmployeeHumanResource, "get_end_of_month_employee_balance_report_df")
    def test_send_mail_to_accounting_recipient(self, mock_fct, user_factory, accounting_email_1, accounting_email_2):
        global_preferences_registry.manager()["wbhuman_resources__accounting_company_emails"] = (
            f"{accounting_email_1};{accounting_email_2}"
        )
        mock_fct.return_value = pd.DataFrame(data=["a", "b"])

        admin_user = user_factory.create(is_superuser=True)
        content_type = ContentType.objects.get_for_model(AbsenceRequest)
        permission = Permission.objects.get(
            codename="administrate_absencerequest",
            content_type=content_type,
        )
        admin_user.user_permissions.add(permission)
        user_factory.create(
            is_superuser=True
        )  # we create another superuser to check if administirators don't contain it

        send_mail_to_accounting()
        assert len(mail.outbox) == 1
        last_mail = mail.outbox[-1]

        assert set(last_mail.to) == {accounting_email_2, accounting_email_1}
        assert set(last_mail.cc) == {admin_user.email}

    @pytest.mark.parametrize("year_str", [(fake.year())])
    def test_assign_yearly_balance(self, year_str, employee_human_resource_factory):
        year = int(year_str)
        test_date = date(year, 1, 1)
        active_employee = employee_human_resource_factory.create(
            enrollment_at=test_date,
            is_active=True,
            occupancy_rate=1,
            extra_days_frequency=EmployeeHumanResource.ExtraDaysBalanceFrequency.YEARLY,
        )
        unactive_employee = employee_human_resource_factory.create(
            enrollment_at=test_date,
            is_active=False,
            occupancy_rate=1,
            extra_days_frequency=EmployeeHumanResource.ExtraDaysBalanceFrequency.YEARLY,
        )
        assert not active_employee.balances.exists()
        assign_balance(test_date)
        assert not unactive_employee.balances.exists()
        assert active_employee.balances.count() == 1  # check that we get only this year balance
        employee_balance = active_employee.balances.get(year=test_date.year)
        allowance = employee_balance.monthly_allowances.first()
        assert (
            employee_balance.monthly_allowances.count() == 1
        )  # check that a unique allowance was granted to the employee
        assert (
            allowance.hourly_allowance == 25 * 8
        )  # check the the hourly amount correspond ot the base 25 days per year in hours
