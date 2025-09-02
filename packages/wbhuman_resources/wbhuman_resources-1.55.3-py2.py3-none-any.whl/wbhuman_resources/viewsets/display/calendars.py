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


class DayOffDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="title", label=_("Title")),
                dp.Field(key="date", label=_("Date")),
                dp.Field(key="count_as_holiday", label=_("Count as Holiday")),
                dp.Field(key="calendar", label=_("Calendar")),
            ]
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [[repeat_field(2, "title")], [repeat_field(2, "calendar")], ["date", "count_as_holiday"]]
        )


class DayOffCalendarDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="title", label=_("Title")),
                dp.Field(key="resource", label=_("Resource")),
                dp.Field(key="timezone", label=_("Timezone")),
            ]
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                ["title", "resource", "timezone"],
                [repeat_field(3, "default_periods_section")],
                [repeat_field(3, "days_off_section")],
            ],
            [
                create_simple_section(
                    "default_periods_section",
                    _("Default Periods"),
                    [["default_periods"]],
                    "default_periods",
                    collapsed=True,
                ),
                create_simple_section("days_off_section", _("Day off"), [["days_off"]], "days_off", collapsed=False),
            ],
        )


class DayOffDayOffCalendarDisplayConfig(DayOffDisplayConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="date", label=_("Date")),
                dp.Field(key="title", label=_("Title")),
                dp.Field(key="count_as_holiday", label=_("Count as Holiday")),
            ]
        )


class DefaultDailyPeriodDayOffCalendarDisplayConfig(DisplayViewConfig):
    def get_list_display(self):
        return dp.ListDisplay(
            fields=[
                dp.Field(key="lower_time", label=_("Start")),
                dp.Field(key="upper_time", label=_("End")),
                dp.Field(key="title", label=_("Title")),
                dp.Field(key="total_hours", label=_("Total Hours")),
            ]
        )

    def get_instance_display(self) -> Display:
        return create_simple_display([["lower_time", "upper_time", "title", "total_hours"]])
