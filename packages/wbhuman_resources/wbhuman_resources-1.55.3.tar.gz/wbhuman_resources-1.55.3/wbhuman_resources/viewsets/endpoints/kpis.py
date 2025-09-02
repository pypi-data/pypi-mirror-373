from rest_framework.reverse import reverse
from wbcore.metadata.configs.endpoints import EndpointViewConfig

from wbhuman_resources.models import KPI


class KPIEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return super().get_endpoint()

    def get_instance_endpoint(self, **kwargs):
        if self.instance:
            if not KPI.is_administrator(self.request.user):
                return None
        return super().get_instance_endpoint()

    def get_create_endpoint(self, **kwargs):
        if KPI.is_administrator(self.request.user):
            return super().get_instance_endpoint()
        return None

    def get_delete_endpoint(self, **kwargs):
        if KPI.is_administrator(self.request.user):
            return super().get_delete_endpoint()
        return None


class KPIEvaluationEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbhuman_resources:kpi-evaluation-list",
            args=[self.view.kwargs["kpi_id"]],
            request=self.request,
        )

    def get_instance_endpoint(self, **kwargs):
        if self.instance:
            return None
        return super().get_instance_endpoint()

    def get_create_endpoint(self, **kwargs):
        return None

    def get_delete_endpoint(self, **kwargs):
        return None


class EvaluationGraphEndpointConfig(EndpointViewConfig):
    pass


class KPIEvaluationPandasEndpointConfig(EndpointViewConfig):
    pass
