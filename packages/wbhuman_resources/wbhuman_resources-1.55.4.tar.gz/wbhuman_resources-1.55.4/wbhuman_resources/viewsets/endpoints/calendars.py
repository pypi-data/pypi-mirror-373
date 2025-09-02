from rest_framework.reverse import reverse
from wbcore.metadata.configs.endpoints import EndpointViewConfig


class DayOffDayOffCalendarEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbhuman_resources:calendar-dayoff-list", args=[self.view.kwargs["calendar_id"]], request=self.request
        )


class DefaultDailyPeriodDayOffCalendar(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbhuman_resources:calendar-defaultperiod-list",
            args=[self.view.kwargs["calendar_id"]],
            request=self.request,
        )
