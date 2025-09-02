from django.apps import apps
from django.db import connection
from django.db.models.signals import pre_migrate
from pytest_factoryboy import register
from wbcore.contrib.authentication.factories import (
    AuthenticatedPersonFactory,
    InternalUserFactory,
    SuperUserFactory,
    UserFactory,
)
from wbcore.contrib.directory.factories import (
    AddressContactFactory,
    BankingContactFactory,
    ClientFactory,
    ClientManagerRelationshipFactory,
    CompanyFactory,
    CompanyTypeFactory,
    CustomerStatusFactory,
    EmailContactFactory,
    EmployersCompanyFactory,
    EntryFactory,
    PersonFactory,
    RelationshipFactory,
    RelationshipTypeFactory,
    TelephoneContactFactory,
    UnemployedPersonFactory,
    WebsiteContactFactory,
)
from wbcore.contrib.geography.factories import ContinentFactory, CountryFactory
from wbcore.contrib.geography.tests.signals import (
    app_pre_migration as app_pre_migration_geography,
)
from wbhuman_resources.factories import (
    AbsenceRequestFactory,
    AbsenceRequestPeriodsFactory,
    AbsenceRequestTypeFactory,
    BalanceHourlyAllowanceFactory,
    BaseDayOffCalendarFactory,
    DayOffCalendarFactory,
    DayOffFactory,
    DefaultDailyPeriodFactory,
    EmployeeHumanResourceFactory,
    EmployeeWeeklyOffPeriodsFactory,
    EmployeeYearBalanceFactory,
    PositionFactory,
    TimeOffRequestFactory,
    TimeOffTypeFactory,
    VacationRequestFactory,
    VacationTypeFactory,
)

register(DayOffCalendarFactory)
register(BaseDayOffCalendarFactory, "day_off_calendar_without_period"),
register(DayOffFactory)
register(EmployeeHumanResourceFactory)
register(EmployeeYearBalanceFactory)
register(AbsenceRequestFactory)
register(TimeOffRequestFactory, "time_off_request")
register(VacationRequestFactory, "vacation_request")
register(VacationTypeFactory, "time_off_type")
register(TimeOffTypeFactory, "vacation_type")
register(AbsenceRequestPeriodsFactory)
register(AbsenceRequestTypeFactory)
register(PositionFactory)
register(DefaultDailyPeriodFactory)
register(BalanceHourlyAllowanceFactory)
register(EmployeeWeeklyOffPeriodsFactory)

register(EntryFactory)
register(CompanyFactory)
register(PersonFactory)
register(ClientFactory)
register(InternalUserFactory)
register(UnemployedPersonFactory)
register(AuthenticatedPersonFactory)
register(EmployersCompanyFactory)
register(BankingContactFactory)
register(AddressContactFactory)
register(TelephoneContactFactory)
register(EmailContactFactory)
register(WebsiteContactFactory)
register(ClientManagerRelationshipFactory)
register(RelationshipFactory)
register(RelationshipTypeFactory)
register(CustomerStatusFactory)
register(CompanyTypeFactory)
register(ContinentFactory)
register(CountryFactory, "country")

register(AuthenticatedPersonFactory, "authenticated_person")
register(UserFactory)
register(SuperUserFactory, "superuser")
from .signals import app_pre_migration as app_pre_migration

pre_migrate.connect(app_pre_migration, sender=apps.get_app_config("wbhuman_resources"))
pre_migrate.connect(app_pre_migration_geography, sender=apps.get_app_config("geography"))
