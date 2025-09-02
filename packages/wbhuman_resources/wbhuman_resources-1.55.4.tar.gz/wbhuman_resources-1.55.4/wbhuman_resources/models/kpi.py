import importlib
from datetime import date
from typing import Iterator, Protocol, Type

import numpy as np
import pandas as pd
from django.conf import settings
from django.contrib.postgres.fields import DateRangeField
from django.db import models
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _
from wbcore.models import WBModel
from wbcore.serializers.serializers import ModelSerializer


class KPIHandler(Protocol):
    """
    This is a protocol to ensure that two methods are present in the implemented handlers.
    A handler makes sure that we have a valid serializer and a valid evaluate method to customize
    KPIs.
    """

    def get_name(self) -> str: ...

    def get_serializer(self) -> Type[ModelSerializer]: ...

    def annotate_parameters(self, queryset: QuerySet["KPI"]) -> QuerySet["KPI"]: ...

    def evaluate(self, kpi: "KPI") -> int: ...


def default_additional_data() -> dict[str, dict | list]:
    return {
        "serializer_data": {},
        "list_data": [],
    }


class KPI(WBModel):
    """
    Key Performance Indicator. Stores 1 KPI for either a person or a group of people. It defines a goal and a method to evaluate this goal.
    Additional parameters are set through a custom serializer which stores its result in a JSON field. The visualizion of it is done by
    passing the json field in the custom serializer. The addition parameters in the json field need to have to keys, one for the raw data that
    is passed into the form serializer and one for a list to show the parameters in human readable form in a list field.
    """

    class Interval(models.TextChoices):
        DAILY = "DAILY", _("Daily")
        WEEKLY = "WEEKLY", _("Weekly")
        MONTHLY = "MONTHLY", _("Monthly")
        QUARTERLY = "QUARTERLY", _("Quarterly")

        @classmethod
        def get_frequence_correspondance(cls, name):
            _map = {
                "DAILY": "D",
                "WEEKLY": "W",
                "MONTHLY": "ME",
                "QUARTERLY": "3M",
            }

            return _map[name]

    name = models.CharField(max_length=255)
    goal = models.PositiveIntegerField(verbose_name=_("Goal"))
    period = DateRangeField(verbose_name=_("Period"))

    evaluated_persons = models.ManyToManyField(
        to="directory.Person", related_name="wbhuman_resources_kpis", verbose_name=_("Evaluated Persons")
    )
    evaluated_intervals = models.CharField(
        max_length=16, choices=Interval.choices, default=Interval.MONTHLY, verbose_name=_("Evaluated Intervals")
    )

    handler = models.CharField(max_length=255)
    additional_data = models.JSONField(default=default_additional_data)
    last_update = models.DateTimeField(
        auto_now=True, verbose_name=_("Last update"), help_text=_("Date of latest change (automatically computed)")
    )
    individual_evaluation = models.BooleanField(default=True, verbose_name=_("Individual Evaluation"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))

    @staticmethod
    def get_all_handlers() -> Iterator[KPIHandler]:
        for handler_path, name in settings.KPI_HANDLERS:
            *module, handler = handler_path.split(".")
            module_path = ".".join(module)
            yield getattr(importlib.import_module(module_path), handler)()

    @staticmethod
    def get_all_handler_choices() -> Iterator[tuple[str, str]]:
        yield from getattr(settings, "KPI_HANDLERS", [])

    def get_handler(self) -> KPIHandler:
        *module, handler = self.handler.split(".")
        module_path = ".".join(module)
        return getattr(importlib.import_module(module_path), handler)()

    @classmethod
    def is_administrator(cls, user):
        user_groups = user.groups
        user_permission = user.user_permissions
        return (
            user_groups.filter(permissions__codename="administrate_kpi").exists()
            or user_permission.filter(codename="administrate_kpi").exists()
            or user.is_superuser
        )

    def generate_evaluation(self, evaluation_date: date):
        if self.individual_evaluation:
            persons = self.evaluated_persons.all()
        else:
            persons = [None]

        for person in persons:
            if evaluation_date <= date.today() and evaluation_date > self.period.lower:
                Evaluation.objects.update_or_create(
                    evaluation_date=evaluation_date,
                    person=person,
                    kpi=self,
                    defaults={
                        "evaluated_period": [self.period.lower, evaluation_date],
                        "evaluated_score": self.get_handler().evaluate(
                            self, evaluated_person=person, evaluation_date=evaluation_date
                        ),
                    },
                )

    class Meta:
        verbose_name = _("Key Performance Indicator")
        verbose_name_plural = _("Key Performance Indicators")
        permissions = [("administrate_kpi", "Can Administrate KPI")]

    def __str__(self):
        return f"{self.name}"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbhuman_resources:kpi-list"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{name}}"

    @classmethod
    def get_endpoint_basename(cls):
        return "wbhuman_resources:kpi"


class Evaluation(models.Model):
    """
    Stores the evaluated result of a KPI on the evaluation day for the previous period for 1 person.
    """

    kpi = models.ForeignKey(
        to="wbhuman_resources.KPI", related_name="evaluations", on_delete=models.CASCADE, verbose_name=_("KPI")
    )
    person = models.ForeignKey(
        to="directory.Person",
        related_name="wbhuman_resources_evaluations",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    evaluated_score = models.IntegerField(null=True, blank=True)
    evaluated_period = DateRangeField()
    evaluation_date = models.DateField()
    last_update = models.DateTimeField(
        auto_now=True, verbose_name=_("Last update"), help_text=_("Date of latest change (automatically computed)")
    )

    class Meta:
        verbose_name = _("Evaluation")
        verbose_name_plural = _("Evaluations")

    def get_rating(self):
        list_date = list(
            pd.date_range(
                start=self.kpi.period.lower,
                end=self.kpi.period.upper,
                freq=KPI.Interval.get_frequence_correspondance(self.kpi.evaluated_intervals),
            )
        )
        list_date = [_date.date() for _date in list_date]
        index = list_date.index(self.evaluation_date)
        nb_intervals = len(list_date)
        goals_expected = (self.kpi.goal * np.ones(nb_intervals) / nb_intervals).cumsum().round(2)
        goal_expected = goals_expected[index]
        rating = (self.evaluated_score / goal_expected * 100).round(2)
        rating = round(rating / 100 * 4)
        return 1 if rating < 1 else rating if rating < 4 else 4
