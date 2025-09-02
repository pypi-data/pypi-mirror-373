import random

import factory
from faker import Faker
from pandas.tseries.offsets import BDay
from psycopg.types.range import TimestamptzRange
from wbcore.contrib.icons import WBIcon

from wbhuman_resources.models import (
    AbsenceRequest,
    AbsenceRequestPeriods,
    AbsenceRequestType,
)

from .calendars import DefaultDailyPeriodFactory
from .employee import EmployeeYearBalanceFactory

fake = Faker()


class AbsenceRequestTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AbsenceRequestType
        django_get_or_create = ["title"]

    title = factory.Faker("text", max_nb_chars=64)
    icon = factory.Iterator(WBIcon.values)
    is_vacation = factory.Faker("boolean")
    is_timeoff = factory.Faker("boolean")
    is_extensible = factory.Faker("boolean")
    auto_approve = False
    days_in_advance = factory.Faker("pyint", min_value=0, max_value=5)

    @factory.post_generation
    def crossborder_countries(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for country in extracted:
                self.crossborder_countries.add(country)


def _get_random_period(calendar):
    lower = Faker().future_datetime() + BDay(0)
    upper = lower + BDay(random.randint(1, 7))
    return TimestamptzRange(
        lower=lower.to_pydatetime().astimezone(calendar.timezone),
        upper=upper.to_pydatetime().astimezone(calendar.timezone),
    )


class VacationTypeFactory(AbsenceRequestTypeFactory):
    title = "Vacation"
    is_vacation = True
    is_timeoff = True
    is_extensible = False
    auto_approve = False


class TimeOffTypeFactory(AbsenceRequestTypeFactory):
    title = "TimeOff"
    is_vacation = False
    is_timeoff = True
    is_extensible = True
    auto_approve = True


class AbsenceRequestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AbsenceRequest

    period = factory.LazyAttribute(lambda o: _get_random_period(o.employee.calendar))
    attachment = factory.django.FileField()
    type = factory.SubFactory("wbhuman_resources.factories.AbsenceRequestTypeFactory")
    employee = factory.SubFactory("wbhuman_resources.factories.EmployeeHumanResourceFactory")
    notes = factory.Faker("text")
    reason = factory.Faker("text")


class VacationRequestFactory(AbsenceRequestFactory):
    type = factory.SubFactory(VacationTypeFactory)
    status = AbsenceRequest.Status.APPROVED


class TimeOffRequestFactory(AbsenceRequestFactory):
    type = factory.SubFactory(TimeOffTypeFactory)
    status = AbsenceRequest.Status.APPROVED


class AbsenceRequestPeriodsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AbsenceRequestPeriods
        django_get_or_create = ["employee", "default_period", "date"]

    date = factory.LazyAttribute(lambda o: (fake.date_object() + BDay(0)).date())
    employee = factory.SubFactory("wbhuman_resources.factories.EmployeeHumanResourceFactory")
    default_period = factory.LazyAttribute(lambda o: DefaultDailyPeriodFactory.create(calendar=o.employee.calendar))
    request = factory.LazyAttribute(
        lambda o: AbsenceRequestFactory.create(
            status=AbsenceRequest.Status.APPROVED,
            type=VacationTypeFactory.create(),
            employee=o.employee,
            period=TimestamptzRange(
                lower=o.default_period.get_lower_datetime(o.date), upper=o.default_period.get_upper_datetime(o.date)
            ),
        )
    )
    balance = factory.LazyAttribute(lambda o: EmployeeYearBalanceFactory.create(year=o.date.year, employee=o.employee))
