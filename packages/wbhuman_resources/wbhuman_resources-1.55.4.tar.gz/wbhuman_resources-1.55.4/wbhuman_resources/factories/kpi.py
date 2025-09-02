import random
from datetime import timedelta

import factory
import pytz
from django.utils import timezone
from faker import Faker
from psycopg.types.range import DateRange
from wbcore.contrib.authentication.factories import InternalUserFactory
from wbcore.contrib.directory.factories.entries import PersonFactory

from wbhuman_resources.models import (
    KPI,
    Evaluation,
    Review,
    ReviewAnswer,
    ReviewGroup,
    ReviewQuestion,
    ReviewQuestionCategory,
)

fake = Faker()


class ReviewGroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ReviewGroup

    name = factory.Faker("text", max_nb_chars=64)

    @factory.post_generation
    def employees(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for employee in extracted:
                self.employees.add(employee)


class ReviewAbstractFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Review
        django_get_or_create = ["moderator"]

    review_group = factory.SubFactory(ReviewGroupFactory)
    review = factory.Faker("date_time_between", start_date="+5d", end_date="+6d", tzinfo=pytz.utc)
    moderator = factory.LazyAttribute(lambda o: InternalUserFactory.create().profile)
    year = factory.Faker("pyint", min_value=1000, max_value=9999)


class ReviewFactory(ReviewAbstractFactory):
    class Meta:
        model = Review
        django_get_or_create = ["moderator", "reviewee", "reviewer"]

    from_date = factory.Faker("date_between", start_date="+2d", end_date="+3d")
    to_date = factory.Faker("date_between", start_date="+4d", end_date="+5d")
    review_deadline = factory.Faker("date_between", start_date="+5d", end_date="+6d")
    reviewee = factory.LazyAttribute(lambda o: InternalUserFactory.create().profile)
    reviewer = factory.LazyAttribute(lambda o: InternalUserFactory.create().profile)
    feedback_reviewee = factory.Faker("text")
    feedback_reviewer = factory.Faker("text")

    signed_reviewee = factory.Faker("date_time", tzinfo=pytz.utc)
    signed_reviewer = factory.Faker("date_time", tzinfo=pytz.utc)
    completely_filled_reviewee = factory.Faker("date_time", tzinfo=pytz.utc)
    completely_filled_reviewer = factory.Faker("date_time", tzinfo=pytz.utc)


class CompletedFilledReviewFactory(ReviewFactory):
    completely_filled_reviewee = factory.Faker("date_time", tzinfo=pytz.utc)
    completely_filled_reviewer = factory.Faker("date_time", tzinfo=pytz.utc)


class SignedReviewFactory(CompletedFilledReviewFactory):
    signed_reviewee = factory.Faker("date_time", tzinfo=pytz.utc)
    signed_reviewer = factory.Faker("date_time", tzinfo=pytz.utc)


class ReviewTemplateFactory(ReviewAbstractFactory):
    is_template = True


class ReviewQuestionCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ReviewQuestionCategory

    name = factory.Faker("text", max_nb_chars=64)
    order = factory.Faker("pyint", min_value=0, max_value=9999)
    weight = factory.Faker("pydecimal", right_digits=1, min_value=0, max_value=9999)


class ReviewQuestionNoCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ReviewQuestion

    review = factory.SubFactory(ReviewFactory)
    question = factory.Faker("text")
    order = factory.Faker("pyint", min_value=0, max_value=9999)
    weight = factory.Faker("pydecimal", right_digits=1, min_value=0, max_value=9999)


class ReviewQuestionFactory(ReviewQuestionNoCategoryFactory):
    category = factory.SubFactory(ReviewQuestionCategoryFactory)


class ReviewAnswerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ReviewAnswer

    question = factory.SubFactory(ReviewQuestionFactory)
    answered_by = factory.LazyAttribute(lambda o: InternalUserFactory.create().profile)
    answered_anonymized = hash(factory.SelfAttribute("answered_by"))
    answer_number = factory.Faker("pyint", min_value=0, max_value=9999)
    answer_text = factory.Faker("text")


class ReviewAnswerNoCategoryFactory(ReviewAnswerFactory):
    question = factory.SubFactory(ReviewQuestionNoCategoryFactory)


class KPIFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = KPI

    name = factory.Faker("pystr")
    goal = factory.Faker("pyint", min_value=0, max_value=9999)
    period = DateRange(timezone.now().date(), timezone.now().date() + timedelta(days=random.randint(4, 5)))
    handler = "wbcrm.kpi_handlers.activities.NumberOfActivityKPI"

    @factory.post_generation
    def evaluated_persons(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for person in extracted:
                self.evaluated_persons.add(person)


class DefaultPersonKPIFactory(KPIFactory):
    @factory.post_generation
    def evaluated_persons(self, create, extracted, **kwargs):
        self.evaluated_persons.add(PersonFactory())


class EvaluationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Evaluation

    kpi = factory.SubFactory(KPIFactory)
    person = factory.SubFactory("wbcore.contrib.directory.factories.PersonFactory")
    evaluated_period = DateRange(timezone.now().date(), timezone.now().date() + timedelta(days=random.randint(4, 5)))
    evaluation_date = timezone.now().date()
