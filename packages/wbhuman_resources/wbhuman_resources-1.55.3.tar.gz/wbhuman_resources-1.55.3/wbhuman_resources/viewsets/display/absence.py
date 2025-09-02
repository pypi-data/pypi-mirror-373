from typing import Optional

from django.utils.translation import gettext as _
from wbcore.contrib.color.enums import WBColor
from wbcore.contrib.icons import WBIcon
from wbcore.enums import Unit
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
    create_simple_section,
)
from wbcore.metadata.configs.display.instance_display.utils import repeat_field
from wbcore.metadata.configs.display.view_config import DisplayViewConfig

from wbhuman_resources.models import AbsenceRequest, AbsenceRequestType


def get_type_legend():
    """
    Dynamically create the request type list legend
    """
    if AbsenceRequestType.objects.exists():
        legend = []
        for type in AbsenceRequestType.objects.all():
            try:
                legend.append(dp.LegendItem(icon=WBIcon[type.icon].icon, label=type.title, value=type.id))
            except KeyError:
                legend.append(dp.LegendItem(icon=type.icon, label=type.title, value=type.id))

        return dp.Legend(key="type", items=legend)


class AbsenceRequestDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="type_icon", label=" ", width=Unit.PIXEL(50)),
                dp.Field(key="employee", label=_("Employee"), width=Unit.PIXEL(200)),
                dp.Field(key="period", label=_("Period"), width=Unit.PIXEL(250)),
                dp.Field(key="_total_hours_in_days", label=_("Total Days"), width=Unit.PIXEL(125)),
                dp.Field(key="_total_vacation_hours_in_days", label=_("Vacation Days"), width=Unit.PIXEL(125)),
                dp.Field(key="department", label=_("Department"), width=Unit.PIXEL(350)),
                dp.Field(key="created", label=_("Created"), width=Unit.PIXEL(150)),
            ],
            formatting=[
                dp.Formatting(
                    column="status",
                    formatting_rules=[
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.YELLOW_LIGHT.value},
                            condition=("==", AbsenceRequest.Status.DRAFT.name),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.BLUE_LIGHT.value},
                            condition=("==", AbsenceRequest.Status.PENDING.name),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.GREEN_LIGHT.value},
                            condition=("==", AbsenceRequest.Status.APPROVED.name),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.RED_LIGHT.value},
                            condition=("==", AbsenceRequest.Status.DENIED.name),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.RED_DARK.value},
                            condition=("==", AbsenceRequest.Status.CANCELLED.name),
                        ),
                    ],
                ),
            ],
            legends=[
                dp.Legend(
                    key="status",
                    items=[
                        dp.LegendItem(
                            icon=WBColor.YELLOW_LIGHT.value,
                            label=AbsenceRequest.Status.DRAFT.label,
                            value=AbsenceRequest.Status.DRAFT.value,
                        ),
                        dp.LegendItem(
                            icon=WBColor.BLUE_LIGHT.value,
                            label=AbsenceRequest.Status.PENDING.label,
                            value=AbsenceRequest.Status.PENDING.value,
                        ),
                        dp.LegendItem(
                            icon=WBColor.GREEN_LIGHT.value,
                            label=AbsenceRequest.Status.APPROVED.label,
                            value=AbsenceRequest.Status.APPROVED.value,
                        ),
                        dp.LegendItem(
                            icon=WBColor.RED_LIGHT.value,
                            label=AbsenceRequest.Status.DENIED.label,
                            value=AbsenceRequest.Status.DENIED.value,
                        ),
                        dp.LegendItem(
                            icon=WBColor.RED_DARK.value,
                            label=AbsenceRequest.Status.CANCELLED.label,
                            value=AbsenceRequest.Status.CANCELLED.value,
                        ),
                    ],
                ),
                get_type_legend(),
            ],
        )

    def get_instance_display(self) -> Display:
        grid_fields = [[repeat_field(3, "status")], ["period", "employee", "type"]]
        try:
            if self.view.get_object().status == AbsenceRequest.Status.DENIED.name:
                grid_fields.append([repeat_field(3, "reason")])
        except AssertionError:
            pass

        grid_fields.extend(
            [
                ["attachment", repeat_field(2, "crossborder_country")],
                [repeat_field(3, "notes")],
                [repeat_field(3, "hours_section")],
                [repeat_field(3, "periods_section")],
            ]
        )
        return create_simple_display(
            grid_fields,
            [
                create_simple_section(
                    "hours_section",
                    _("Hours"),
                    [
                        ["_total_hours", "_total_hours_in_days"],
                        ["_total_vacation_hours", "_total_vacation_hours_in_days"],
                    ],
                    collapsed=False,
                ),
                create_simple_section("periods_section", _("Periods"), [["periods"]], "periods", collapsed=True),
            ],
        )


class AbsenceRequestTypeDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="title", label=_("Title")),
                dp.Field(key="icon", label=_("Icon")),
                dp.Field(key="color", label=_("Color")),
            ]
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                [
                    "title",
                    "icon",
                    "color",
                ],
                [repeat_field(3, "extra_notify_groups")],
                [repeat_field(3, "settings_section")],
                [repeat_field(3, "allowed_countries_section")],
            ],
            [
                create_simple_section(
                    "settings_section",
                    _("Settings"),
                    [
                        [
                            "is_vacation",
                            "is_timeoff",
                            "is_extensible",
                        ],
                        ["days_in_advance", "auto_approve", "is_country_necessary"],
                    ],
                    collapsed=False,
                ),
                create_simple_section(
                    "allowed_countries_section",
                    _("Allowed Countries (Cross-Border Rule)"),
                    [["crossbordercountries"]],
                    "crossbordercountries",
                    collapsed=False,
                ),
            ],
        )


class AbsenceRequestCrossBorderCountryDisplayConfig(DisplayViewConfig):
    def get_instance_display(self) -> Display:
        return create_simple_display([["geography"]])

    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(fields=(dp.Field(key="geography_repr", label=_("Country")),))


class AbsenceRequestEmployeeHumanResourceDisplayConfig(AbsenceRequestDisplayConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="type", label=_("Type")),
                dp.Field(key="status", label=_("Status")),
                dp.Field(key="period", label=_("Period")),
                dp.Field(key="_total_hours_in_days", label=_("Total Days")),
                dp.Field(key="_total_vacation_hours_in_days", label=_("Vacation Days")),
                dp.Field(key="created", label=_("Created")),
            ]
        )


class AbsenceTypeCountEmployeeDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="year", label=_("Year")),
                dp.Field(key="absence_type", label=_("Type")),
                dp.Field(key="hours_count", label=_("Count (hours)")),
                dp.Field(key="days_count", label=_("Count (days)")),
            ]
        )


class AbsenceRequestPeriodsAbsenceRequestDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="date", label=_("Date")),
                dp.Field(key="default_period", label=_("Period")),
                dp.Field(key="_total_hours", label=_("Total hours")),
                dp.Field(key="balance", label=_("Balance")),
                dp.Field(key="consecutive_hours_count", label=_("Consecutive hours count")),
            ]
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [["date", repeat_field(2, "default_period")], ["_total_hours", "balance", "consecutive_hours_count"]]
        )


class AbsenceTablePandasDisplayConfig(DisplayViewConfig):
    FORMATTING_CELL_RULE = [
        dp.FormattingRule(
            style={"backgroundColor": "#BA324F", "color": "#BA324F"},
            condition=("==", -1),  # Absent
        ),
        dp.FormattingRule(
            style={"backgroundColor": "#F0F7F4", "color": "#F0F7F4"},
            condition=("==", 0),  # Present
        ),
        dp.FormattingRule(
            style={"backgroundColor": "#6A8D73", "color": "#6A8D73"},
            condition=("==", 1),  # Partially Present
        ),
        dp.FormattingRule(
            style={"backgroundColor": "#1E91D6", "color": "#1E91D6"},
            condition=("==", 2),  # Partially Remote
        ),
        dp.FormattingRule(
            style={"backgroundColor": "#18206F", "color": "#18206F"},
            condition=("==", 3),  # Remote
        ),
    ]

    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(
                    key="employee_repr",
                    label=_("Employee"),
                    formatting_rules=[
                        dp.FormattingRule(
                            style={"fontWeight": "bold"},
                            condition=("!=", None),
                        )
                    ],
                    width=Unit.PIXEL(200),
                ),
                dp.Field(key="position", label=_("Department"), width=Unit.PIXEL(300)),
                dp.Field(
                    key="monday", label=_("Monday"), formatting_rules=self.FORMATTING_CELL_RULE, width=Unit.PIXEL(150)
                ),
                dp.Field(
                    key="tuesday",
                    label=_("Tuesday"),
                    formatting_rules=self.FORMATTING_CELL_RULE,
                    width=Unit.PIXEL(150),
                ),
                dp.Field(
                    key="wednesday",
                    label=_("Wednesday"),
                    formatting_rules=self.FORMATTING_CELL_RULE,
                    width=Unit.PIXEL(150),
                ),
                dp.Field(
                    key="thursday",
                    label=_("Thursday"),
                    formatting_rules=self.FORMATTING_CELL_RULE,
                    width=Unit.PIXEL(150),
                ),
                dp.Field(
                    key="friday", label=_("Friday"), formatting_rules=self.FORMATTING_CELL_RULE, width=Unit.PIXEL(150)
                ),
                dp.Field(
                    key="saturday",
                    label=_("Saturday"),
                    formatting_rules=self.FORMATTING_CELL_RULE,
                    width=Unit.PIXEL(150),
                ),
                dp.Field(
                    key="sunday", label=_("Sunday"), formatting_rules=self.FORMATTING_CELL_RULE, width=Unit.PIXEL(150)
                ),
            ],
            legends=[
                dp.Legend(
                    items=[
                        dp.LegendItem(icon="#F0F7F4", label=_("Present")),
                        dp.LegendItem(icon="#6A8D73", label=_("Partially Present")),
                        dp.LegendItem(icon="#18206F", label=_("Remote")),
                        dp.LegendItem(icon="#1E91D6", label=_("Partially Remote")),
                        dp.LegendItem(icon="#BA324F", label=_("Absent")),
                    ]
                )
            ],
            # formatting=[
            #     dp.Formatting(
            #         column="employee_repr",
            #         formatting_rules=[
            #             dp.FormattingRule(
            #                 condition=("!=", None), style={"fontWeight": "bold"}
            #             )
            #         ]
            #     )
            # ]
        )
