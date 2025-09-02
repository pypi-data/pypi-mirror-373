from rest_framework.reverse import reverse
from wbcore.metadata.configs.endpoints import EndpointViewConfig


class AbsenceRequestEmployeeHumanResourceEndpointConfig(EndpointViewConfig):
    def get_create_endpoint(self, **kwargs):
        return reverse("wbhuman_resources:absencerequest-list", args=[], request=self.request)

    def get_endpoint(self, **kwargs):
        return reverse(
            "wbhuman_resources:employee-absencerequest-list",
            args=[self.view.kwargs["employee_id"]],
            request=self.request,
        )


class YearBalanceEmployeeHumanResourceEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbhuman_resources:employee-employeeyearbalance-list",
            args=[self.view.kwargs["employee_id"]],
            request=self.request,
        )

    def get_create_endpoint(self, **kwargs):
        return None

    def get_delete_endpoint(self, **kwargs):
        return None


class EmployeeBalanceEndpointConfig(EndpointViewConfig):
    def get_instance_endpoint(self, **kwargs):
        return reverse("wbhuman_resources:employeebalance-list", args=[], request=self.request)

    def get_endpoint(self, **kwargs):
        return None


class EmployeeEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return None


class WeeklyOffPeriodEmployeeHumanResourceEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbhuman_resources:employee-weeklyoffperiod-list",
            args=[self.view.kwargs["employee_id"]],
            request=self.request,
        )
