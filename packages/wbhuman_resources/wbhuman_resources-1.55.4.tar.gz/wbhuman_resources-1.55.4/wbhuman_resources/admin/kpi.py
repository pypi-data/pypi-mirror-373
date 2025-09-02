from django.contrib import admin

from ..models.kpi import KPI, Evaluation


@admin.register(Evaluation)
class KEvaluationAdmin(admin.ModelAdmin):
    list_display = ["id", "person", "evaluated_score", "evaluation_date", "evaluated_period"]


class EvaluationInline(admin.TabularInline):
    model = Evaluation
    extra = 0
    raw_id_fields = ["kpi", "person"]


@admin.register(KPI)
class KPIAdmin(admin.ModelAdmin):
    list_display = ["name", "period", "goal"]
    inlines = (EvaluationInline,)
    raw_id_fields = ["evaluated_persons"]
