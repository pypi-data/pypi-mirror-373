from django.utils.translation import gettext as _
from wbcore.metadata.configs.titles import TitleViewConfig

from wbhuman_resources.models import KPI


class EvaluationGraphTitleConfig(TitleViewConfig):
    def get_list_title(self):
        kpi = KPI.objects.get(id=self.view.kwargs["kpi_id"])
        return _("Evaluations Graph of KPI: {kpi}").format(kpi=str(kpi))


class KPIEvaluationPandasTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return _("KPI Evaluations")
