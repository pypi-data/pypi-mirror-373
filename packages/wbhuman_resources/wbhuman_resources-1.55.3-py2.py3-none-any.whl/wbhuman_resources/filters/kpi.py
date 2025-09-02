from django.utils.translation import gettext_lazy as _
from wbcore import filters as wb_filters

from wbhuman_resources.models import KPI, Evaluation


class KPIFilterSet(wb_filters.FilterSet):
    class Meta:
        model = KPI
        fields = {
            "name": ["exact", "icontains"],
            "evaluated_persons": ["exact"],
        }


class KPIEvaluationFilterSet(wb_filters.FilterSet):
    class Meta:
        model = Evaluation
        fields = {
            "person": ["exact"],
            "evaluation_date": ["lte", "gte"],
        }


class KPIEvaluationPandasFilter(wb_filters.FilterSet):
    kpi_name = wb_filters.CharFilter(label=_("KPI"), lookup_expr="icontains")
    goal = wb_filters.CharFilter(label=_("Goal"), lookup_expr="icontains")

    class Meta:
        model = Evaluation
        fields = {
            "person": ["exact"],
            "kpi": ["exact"],
            "evaluation_date": ["lte", "gte"],
        }
