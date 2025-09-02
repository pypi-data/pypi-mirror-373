from typing import Optional

from django.utils.translation import gettext as _
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
    create_simple_section,
)
from wbcore.metadata.configs.display.instance_display.utils import repeat_field
from wbcore.metadata.configs.display.view_config import DisplayViewConfig

from wbhuman_resources.models.kpi import KPI


class KPIDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="name", label=_("Name")),
                dp.Field(key="handler", label=_("KPI")),
                dp.Field(key="evaluated_persons", label=_("Persons")),
                dp.Field(key="period", label=_("Period")),
                dp.Field(key="parameters", label=_("Parameters")),
                dp.Field(key="is_active", label=_("Is Active")),
            ]
        )

    def get_instance_display(self) -> Display:
        sections = []
        grid_fields = [
            [repeat_field(2, "name")],
            [repeat_field(2, "handler")],
            [repeat_field(2, "evaluated_persons")],
            ["evaluated_intervals", "is_active"],
            ["goal", "individual_evaluation"],
            ["period", "last_update"],
        ]
        if pk := self.view.kwargs.get("pk", None):
            handler = KPI.objects.get(id=pk).get_handler()
            sections = [
                create_simple_section("parameters_section", _("Parameters"), handler.get_display_grid()),
                create_simple_section("evaluation_section", _("Evaluations"), [["evaluations"]], "evaluations"),
            ]
            grid_fields.extend(["parameters_section", "evaluation_section"])
        return create_simple_display(grid_fields, sections)


class KPIEvaluationDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="person", label=_("Person")),
                dp.Field(key="evaluated_score", label=_("Evaluated Score")),
                dp.Field(key="goal", label=_("Goal")),
                dp.Field(key="evaluation_date", label=_("Evaluation Date")),
                dp.Field(key="evaluated_period", label=_("Evaluated Period")),
            ]
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                [repeat_field(2, "kpi")],
                [repeat_field(2, "person")],
                [repeat_field(2, "evaluated_period")],
                ["evaluation_date", "last_update"],
                [repeat_field(2, "evaluated_score")],
            ]
        )


class KPIEvaluationPandasDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        pandas_fields = [
            dp.Field(key="person", label=_("Person")),
            dp.Field(key="kpi_name", label=_("KPI")),
            dp.Field(key="period", label=_("Period")),
            dp.Field(key="evaluation_date", label=_("Evaluation Date")),
            dp.Field(key="evaluated_score", label=_("Evaluated Score")),
            dp.Field(
                key="goal",
                label=_("Goal"),
                formatting_rules=[
                    dp.FormattingRule(
                        style={"fontWeight": "bold"},
                    ),
                ],
            ),
            dp.Field(key="progression", label=_("Progression")),
        ]
        return dp.ListDisplay(fields=pandas_fields)
