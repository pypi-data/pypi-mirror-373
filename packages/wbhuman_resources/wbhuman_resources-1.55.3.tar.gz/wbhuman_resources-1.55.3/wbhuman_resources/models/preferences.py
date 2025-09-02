from datetime import date

from django.db.utils import ProgrammingError
from dynamic_preferences.registries import global_preferences_registry
from pandas.tseries.offsets import MonthBegin

from wbhuman_resources.dynamic_preferences_registry import (
    NumberOfMonthsBeforeBalanceExpiration,
)


def default_vacation_days_per_year():
    return global_preferences_registry.manager()["wbhuman_resources__default_vacation_days"]


def long_vacation_number_of_days():
    return global_preferences_registry.manager()["wbhuman_resources__long_vacation_number_of_days"]


def get_main_company():
    return global_preferences_registry.manager()["directory__main_company"]


def get_previous_year_balance_expiration_date(year: int) -> date:
    next_year_date = date(year + 1, 1, 1)
    try:
        number_of_month_before_balance_expiration = global_preferences_registry.manager()[
            "wbhuman_resources__number_of_month_before_balance_expiration"
        ]
    except (RuntimeError, ProgrammingError):
        number_of_month_before_balance_expiration = NumberOfMonthsBeforeBalanceExpiration.default

    return (next_year_date + MonthBegin(number_of_month_before_balance_expiration)).date()


def get_is_external_considered_as_internal():
    try:
        return global_preferences_registry.manager()["wbhuman_resources__is_external_considered_as_internal"]
    except (RuntimeError, ProgrammingError):
        return False
