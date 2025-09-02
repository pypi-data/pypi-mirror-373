from django.conf import settings
from django.forms import ValidationError
from django.utils.translation import gettext as _
from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences.types import (
    BooleanPreference,
    IntegerPreference,
    LongStringPreference,
    ModelChoicePreference,
    StringPreference,
)

from wbhuman_resources.models.calendars import DayOffCalendar

human_resources = Section("wbhuman_resources")

# Employee dynamic preferences


@global_preferences_registry.register
class EmployeeDefaultCalendarEntry(ModelChoicePreference):
    section = human_resources
    name = "employee_default_calendar"
    queryset = DayOffCalendar.objects.all()
    default = None


@global_preferences_registry.register
class DefaultVacationDaysPreference(IntegerPreference):
    section = human_resources
    name = "default_vacation_days"
    default = 25

    verbose_name = _("Default employee vacation days")
    help_text = _("The number of vacation days allocated to an employee working full time")

    def validate(self, value):
        if not isinstance(value, int) or value <= 1:
            raise ValidationError(_("Only positive natural numbers allowed."))


@global_preferences_registry.register
class DefaultFromEmailAddressPreference(StringPreference):
    section = human_resources
    name = "default_from_email_address"
    default = settings.DEFAULT_FROM_EMAIL

    verbose_name = "The default from email address"
    help_text = "The default from email address used to send hr related emails"


@global_preferences_registry.register
class NumberOfMonthsBeforeBalanceExpiration(IntegerPreference):
    section = human_resources
    name = "number_of_month_before_balance_expiration"
    default = 12 * 5  # Default to 5 years
    verbose_name = _("The number of month before yearly balance expiration")
    help_text = _(
        "The number of months before any yearly balance is considered expired. The count starts the first day of the next balance year"
    )


@global_preferences_registry.register
class LongVacationNumberOfDaysPreference(IntegerPreference):
    section = human_resources
    name = "long_vacation_number_of_days"
    default = 10
    help_text = _("The number of days after which a vacation is considered a long vacation.")
    verbose_name = _("Long Vacation Number of days")


# Monthly report accounting preference


@global_preferences_registry.register
class AccountingCompanyEmails(LongStringPreference):
    section = human_resources
    name = "accounting_company_emails"
    default = "no-reply@stainly-bench.com;"
    verbose_name = _("Accounting email destination")
    help_text = _("The accounting company emails to send automatic reports to, as a comma separated list")


# Calendar preferences


@global_preferences_registry.register
class CalendarDefaultPublicHolidayPackagePreference(StringPreference):
    section = human_resources
    name = "calendar_default_public_holiday_package"
    default = "europe.Switzerland"

    verbose_name = _("Default calendar Public holiday package")
    help_text = _("Package where the correct public holidays are found. Defaults to Europe Switzerland")

    def validate(self, value):
        if len(value.split(".")) != 2:
            raise ValidationError(_("The preference has to be in the format of <continent>.<region>"))


@global_preferences_registry.register
class CalendarDefaultTimezonePreference(StringPreference):
    section = human_resources
    name = "calendar_default_timezone"
    default = "UTC"

    verbose_name = _("Default calendar timezone")
    help_text = _("The default calendar timezone")


@global_preferences_registry.register
class AreExternalEmployeesConsideredAsInternal(BooleanPreference):
    section = human_resources
    name = "is_external_considered_as_internal"
    default = False

    verbose_name = _("Are external employee considered as internal?")
    help_text = _("If True, will consider the external employee (and any related logic) as internal employee")
