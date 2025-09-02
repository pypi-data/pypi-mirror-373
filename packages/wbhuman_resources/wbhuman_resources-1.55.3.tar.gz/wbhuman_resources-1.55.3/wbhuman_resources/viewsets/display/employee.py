from datetime import date
from typing import Optional

from django.utils.translation import gettext as _
from wbcore.contrib.color.enums import WBColor
from wbcore.enums import Unit
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
    create_simple_section,
)
from wbcore.metadata.configs.display.instance_display.utils import repeat_field
from wbcore.metadata.configs.display.view_config import DisplayViewConfig

from wbhuman_resources.models.preferences import (
    get_previous_year_balance_expiration_date,
)


class PositionDisplayConfig(DisplayViewConfig):
    def get_instance_display(self) -> Display:
        return create_simple_display(
            [["name", "name", "color"], ["level", "parent", "manager"], [repeat_field(3, "groups")]]
        )

    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="name", label=_("Name")),
                dp.Field(key="level", label=_("Level")),
                dp.Field(key="height", label=_("Height")),
                dp.Field(key="parent", label=_("Parent Position")),
                dp.Field(key="manager", label=_("Manager")),
                dp.Field(key="groups", label=_("Groups")),
            ]
        )


class EmployeeBalanceDisplayConfig(DisplayViewConfig):
    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                ["profile", "contract_type", "is_active"],
                ["calendar", "position", "enrollment_at"],
                ["extra_days_per_period", "extra_days_frequency", "occupancy_rate"],
                [
                    "available_vacation_balance_previous_year",
                    "available_vacation_balance_current_year",
                    "available_vacation_balance_next_year",
                ],
                [repeat_field(3, "periods_count_per_type_section")],
                [repeat_field(3, "absencerequest_section")],
                [repeat_field(3, "employeeyearbalance_section")],
            ],
            [
                create_simple_section(
                    "periods_count_per_type_section",
                    _("Absence Periods Count per type"),
                    [["periods_count_per_type"]],
                    "periods_count_per_type",
                    collapsed=True,
                ),
                create_simple_section(
                    "absencerequest_section", _("Requests"), [["absencerequest"]], "absencerequest", collapsed=True
                ),
                create_simple_section(
                    "employeeyearbalance_section",
                    _("Balances"),
                    [["employeeyearbalance"]],
                    "employeeyearbalance",
                    collapsed=True,
                ),
            ],
        )

    def get_list_display(self) -> Optional[dp.ListDisplay]:
        current_year = date.today().year

        base_fields = [
            dp.Field(key="profile", label=_("Profile"), width=Unit.PIXEL(250)),
            dp.Field(key="position", label=_("Position"), width=Unit.PIXEL(350)),
            dp.Field(key="contract_type", label=_("Contract Type"), width=Unit.PIXEL(140)),
            dp.Field(key="is_active", label=_("Active"), width=Unit.PIXEL(100)),
            dp.Field(key="occupancy_rate", label=_("Occupancy Rate"), width=Unit.PIXEL(120)),
            dp.Field(key="calendar", label=_("Calendar"), width=Unit.PIXEL(140)),
            dp.Field(key="extra_days_frequency", label=_("Frequency"), width=Unit.PIXEL(120)),
            dp.Field(key="extra_days_per_period", label=_("Periodic days"), width=Unit.PIXEL(120)),
            dp.Field(key="took_long_vacations", label=_("Long Vacation"), width=Unit.PIXEL(140)),
        ]
        if date.today() < get_previous_year_balance_expiration_date(current_year):
            base_fields.append(
                dp.Field(
                    key="available_vacation_balance_previous_year",
                    label=_("Balance ({current_year})").format(current_year=current_year - 1),
                    formatting_rules=[
                        dp.FormattingRule(
                            style={"color": WBColor.RED.value, "fontWeight": "bold"},
                            condition=("<=", 0),
                        ),
                        dp.FormattingRule(
                            style={"color": WBColor.GREEN.value, "fontWeight": "bold"},
                            condition=(">", 0),
                        ),
                    ],
                    width=Unit.PIXEL(175),
                )
            )
        base_fields.append(
            dp.Field(
                key="available_vacation_balance_current_year",
                label=_("Balance ({current_year})").format(current_year=current_year),
                formatting_rules=[
                    dp.FormattingRule(
                        style={"color": WBColor.RED.value, "fontWeight": "bold"},
                        condition=("<=", 0),
                    ),
                    dp.FormattingRule(
                        style={"color": WBColor.GREEN.value, "fontWeight": "bold"},
                        condition=(">", 0),
                    ),
                ],
                width=Unit.PIXEL(175),
            )
        )
        if date.today().month == 12:
            base_fields.append(
                dp.Field(
                    key="available_vacation_balance_next_year",
                    label=_("Balance ({current_year})").format(current_year=current_year + 1),
                    formatting_rules=[
                        dp.FormattingRule(
                            style={"color": WBColor.RED.value, "fontWeight": "bold"},
                            condition=("<=", 0),
                        ),
                        dp.FormattingRule(
                            style={"color": WBColor.GREEN.value, "fontWeight": "bold"},
                            condition=(">", 0),
                        ),
                    ],
                    width=Unit.PIXEL(175),
                )
            )
        return dp.ListDisplay(fields=tuple(base_fields))


class EmployeeDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="profile", label=_("Name")),
                dp.Field(key="calendar", label=_("Calendar")),
                dp.Field(key="contract_type", label=_("Contract")),
                dp.Field(key="position", label=_("Position")),
                dp.Field(key="top_position_repr", label=_("Position N+1")),
                dp.Field(key="position_manager", label=_("Department manager")),
                dp.Field(key="direct_manager", label=_("Direct Manager")),
                dp.Field(key="primary_telephone", label=_("Telephone")),
                dp.Field(key="primary_email", label=_("Email")),
                dp.Field(key="primary_address", label=_("Address")),
                dp.Field(key="enrollment_at", label=_("Since")),
            ]
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                ["profile", "is_active", "enrollment_at"],
                ["direct_manager", "calendar", "position"],
                [repeat_field(3, "contract_info_section")],
            ],
            [
                create_simple_section(
                    "contract_info_section",
                    _("Contract Info"),
                    [
                        [
                            "extra_days_frequency",
                            "occupancy_rate",
                            "contract_type",
                        ],
                    ],
                )
            ],
        )


class YearBalanceEmployeeHumanResourceDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="year", label=_("Year")),
                dp.Field(key="_balance", label="Given yearly balance (in hours)"),
                dp.Field(key="_number_mandatory_days_off", label="Mandatory days off (in hours)"),
                dp.Field(key="_total_vacation_hourly_usage", label="Hourly usage (in hours)"),
                dp.Field(key="actual_total_vacation_hourly_balance", label="Hourly available balance (in hours)"),
                dp.Field(key="_balance_in_days", label="Given yearly balance (in days)"),
                dp.Field(key="_number_mandatory_days_off_in_days", label="Mandatory days off (in days)"),
                dp.Field(key="_total_vacation_hourly_usage_in_days", label="Hourly usage (in days)"),
                dp.Field(
                    key="actual_total_vacation_hourly_balance_in_days", label="Hourly available balance (in days)"
                ),
            ]
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                ["year", "extra_balance"],
                [repeat_field(2, "hourly_balance_section")],
                [repeat_field(2, "daily_balance_section")],
            ],
            [
                create_simple_section(
                    "hourly_balance_section",
                    _("Balance (in Hours)"),
                    [
                        [
                            "_balance_in_days",
                            "_number_mandatory_days_off_in_days",
                            "_total_vacation_hourly_usage_in_days",
                            "actual_total_vacation_hourly_balance_in_days",
                        ]
                    ],
                    collapsed=False,
                ),
                create_simple_section(
                    "daily_balance_section",
                    _("Balance (in Days)"),
                    [
                        [
                            "_balance",
                            "_number_mandatory_days_off",
                            "_total_vacation_hourly_usage",
                            "actual_total_vacation_hourly_balance",
                        ]
                    ],
                    collapsed=False,
                ),
            ],
        )


class WeeklyOffPeriodEmployeeHumanResourceDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="period", label=_("Period")),
                dp.Field(key="weekday", label=_("Weekday")),
            ]
        )

    def get_instance_display(self) -> Display:
        return create_simple_display([["period", "weekday"]])
