from django.utils.translation import gettext_lazy as _
from rest_framework.reverse import reverse
from wbcore import serializers
from wbcore.contrib.directory.serializers import PersonRepresentationSerializer

from wbhuman_resources.models import KPI, Evaluation


class KPIRepresentationSerializer(serializers.RepresentationSerializer):
    _detail = serializers.HyperlinkField(reverse_name="wbhuman_resources:kpi-detail")

    class Meta:
        model = KPI
        fields = ("id", "name", "_detail")


class EvaluationRepresentationSerializer(serializers.RepresentationSerializer):
    _person = PersonRepresentationSerializer(source="person")

    class Meta:
        model = Evaluation
        fields = ("id", "evaluated_score", "person", "_person", "evaluation_date")


class KPIModelSerializer(serializers.ModelSerializer):
    handler = serializers.ChoiceField(choices=list(KPI.get_all_handler_choices()), label=_("Handler"))
    parameters = serializers.ListField(read_only=True)
    _evaluated_persons = PersonRepresentationSerializer(source="evaluated_persons", many=True)

    @serializers.register_resource()
    def register_history_resource(self, instance, request, user):
        resources = {
            "evaluations": reverse("wbhuman_resources:kpi-evaluation-list", args=[instance.id], request=request),
            "evaluationgraph": reverse(
                "wbhuman_resources:kpi-evaluationgraph-list", args=[instance.id], request=request
            ),
            "kpievaluationpandas": reverse("wbhuman_resources:kpievaluationpandas-list", args=[], request=request)
            + f"?kpi={instance.id}",
        }

        return resources

    class Meta:
        model = KPI
        fields = (
            "id",
            "name",
            "handler",
            "goal",
            "period",
            "evaluated_intervals",
            "evaluated_persons",
            "_evaluated_persons",
            "parameters",
            "last_update",
            "individual_evaluation",
            "is_active",
            "_additional_resources",
        )


class EvaluationModelSerializer(serializers.ModelSerializer):
    _kpi = KPIRepresentationSerializer(source="kpi")
    _person = PersonRepresentationSerializer(source="person")
    goal = serializers.IntegerField(read_only=True)

    class Meta:
        model = Evaluation
        fields = (
            "id",
            "kpi",
            "_kpi",
            "person",
            "_person",
            "evaluated_score",
            "evaluated_period",
            "evaluation_date",
            "last_update",
            "goal",
        )
