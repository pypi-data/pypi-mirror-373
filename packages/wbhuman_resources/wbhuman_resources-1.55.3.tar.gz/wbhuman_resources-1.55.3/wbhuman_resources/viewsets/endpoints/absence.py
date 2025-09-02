from rest_framework.reverse import reverse
from wbcore.metadata.configs.endpoints import EndpointViewConfig

from wbhuman_resources.models import AbsenceRequest, EmployeeHumanResource


class AbsenceRequestEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(f"{self.view.get_model().get_endpoint_basename()}-list", request=self.request)

    def get_instance_endpoint(self, **kwargs):
        if self.instance:
            obj = self.view.get_object()
            if obj.status != AbsenceRequest.Status.DRAFT.name and not EmployeeHumanResource.is_administrator(
                self.request.user
            ):
                return None
        return self.get_endpoint()

    def get_create_endpoint(self, **kwargs):
        return self.get_endpoint()

    def get_delete_endpoint(self, **kwargs):
        if self.instance:
            obj = self.view.get_object()
            if obj.is_deletable_for_user(self.request.user):
                return self.get_endpoint()
        return None


class AbsenceRequestCrossBorderCountryEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbhuman_resources:absencerequesttype-crossbordercountry-list",
            args=[self.view.kwargs["absencerequesttype_id"]],
            request=self.request,
        )


class AbsenceTypeCountEmployeeEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return None


class AbsenceRequestPeriodsAbsenceRequestEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return None


class AbsenceRequestPlannerEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return None


class AbsenceTablePandasEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return None
