import zoneinfo
from datetime import time

import factory
from faker import Faker

from wbhuman_resources.models.calendars import (
    DayOff,
    DayOffCalendar,
    DefaultDailyPeriod,
)

fake = Faker()


class BaseDayOffCalendarFactory(factory.django.DjangoModelFactory):
    title = "Default Calendar"
    resource = "europe.Germany"
    timezone = zoneinfo.ZoneInfo("UTC")

    class Meta:
        model = DayOffCalendar
        django_get_or_create = ["resource"]


class DayOffCalendarFactory(BaseDayOffCalendarFactory):
    @factory.post_generation
    def post_gen(self, create, extracted, **kwargs):
        if create:
            DefaultDailyPeriodFactory.create(calendar=self)
            DefaultDailyPeriodFactory.create(
                calendar=self,
                lower_time=time(
                    14,
                    0,
                    0,
                ),
                upper_time=time(18, 0, 0),
                title="afternoon",
            )


class DefaultDailyPeriodFactory(factory.django.DjangoModelFactory):
    lower_time = time(9, 0, 0)
    upper_time = time(13, 0, 0)
    title = "morning"
    calendar = factory.SubFactory("wbhuman_resources.factories.BaseDayOffCalendarFactory")

    class Meta:
        model = DefaultDailyPeriod
        django_get_or_create = ["lower_time", "upper_time", "calendar"]


class DayOffFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DayOff

    title = factory.Faker("text", max_nb_chars=64)
    date = factory.Faker("date_object")
    calendar = factory.SubFactory("wbhuman_resources.factories.DayOffCalendarFactory")
