import factory
from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from faker import Faker

from wbhuman_resources.models import (
    BalanceHourlyAllowance,
    EmployeeHumanResource,
    EmployeeWeeklyOffPeriods,
    EmployeeYearBalance,
    Position,
)

fake = Faker()


class PositionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Position

    name = factory.Faker("text", max_nb_chars=64)
    manager = None

    @factory.post_generation
    def post_gen(self, create, extracted, **kwargs):
        group = Group.objects.get_or_create(name="Test Group")[0]
        self.groups.add(group)


@factory.django.mute_signals(post_save)
class EmployeeHumanResourceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EmployeeHumanResource
        django_get_or_create = ["profile"]

    is_active = True
    profile = factory.SubFactory("wbcore.contrib.authentication.factories.AuthenticatedPersonFactory")
    direct_manager = factory.SubFactory("wbcore.contrib.directory.factories.PersonFactory")
    calendar = factory.SubFactory("wbhuman_resources.factories.DayOffCalendarFactory")
    position = factory.SubFactory(PositionFactory)
    enrollment_at = factory.Faker("past_date")
    extra_days_frequency = EmployeeHumanResource.ExtraDaysBalanceFrequency.YEARLY

    contract_type = EmployeeHumanResource.ContractType.INTERNAL
    occupancy_rate = factory.Faker("pyfloat", min_value=0, max_value=1)


class EmployeeYearBalanceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EmployeeYearBalance
        django_get_or_create = ["employee", "year"]

    employee = factory.SubFactory("wbhuman_resources.factories.EmployeeHumanResourceFactory")
    year = factory.Faker("pyint", min_value=1970, max_value=2022)
    extra_balance = factory.Faker("pyint", min_value=0, max_value=20)

    @factory.post_generation
    def post_gen(self, create, extracted, **kwargs):
        if create:
            BalanceHourlyAllowanceFactory.create(balance=self)


class BalanceHourlyAllowanceFactory(factory.django.DjangoModelFactory):
    balance = factory.SubFactory("wbhuman_resources.factories.EmployeeYearBalanceFactory")
    period_index = 1
    hourly_allowance = factory.Faker("pyint", min_value=160, max_value=200)

    class Meta:
        model = BalanceHourlyAllowance
        django_get_or_create = ["balance", "period_index"]


class EmployeeWeeklyOffPeriodsFactory(factory.django.DjangoModelFactory):
    employee = factory.SubFactory("wbhuman_resources.factories.EmployeeHumanResourceFactory")
    period = factory.LazyAttribute(lambda x: x.employee.calendar.default_periods.order_by("?")[0])
    weekday = factory.Faker("pyint", min_value=0, max_value=7)

    class Meta:
        model = EmployeeWeeklyOffPeriods
        django_get_or_create = ["employee", "period", "weekday"]
