from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from wbcore import filters as wb_filters

from wbhuman_resources.models import EmployeeHumanResource, Position


class PositionFilterSet(wb_filters.FilterSet):
    class Meta:
        model = Position
        fields = {"name": ["exact", "icontains"], "parent": ["exact"], "level": ["exact"], "manager": ["exact"]}


class BaseEmployeeFilterSet(wb_filters.FilterSet):
    contract_type = wb_filters.ChoiceFilter(
        label=_("Contract"),
        choices=EmployeeHumanResource.ContractType.choices,
        initial=EmployeeHumanResource.ContractType.INTERNAL,
    )
    is_active = wb_filters.BooleanFilter(label=_("Is Active"), initial=True)
    position = wb_filters.ModelChoiceFilter(
        label=_("Position"),
        queryset=Position.objects.all(),
        endpoint=Position.get_representation_endpoint(),
        value_key=Position.get_representation_value_key(),
        label_key=Position.get_representation_label_key(),
        method="filter_position",
        filter_params={"height": 0},
    )

    def filter_position(self, queryset, name, value):
        if value:
            return queryset.filter(position__in=value.get_descendants(include_self=True)).distinct()
        return queryset


class EmployeeBalanceFilterSet(BaseEmployeeFilterSet):
    took_long_vacations = wb_filters.BooleanFilter(field_name="took_long_vacations", lookup_expr="exact")

    extra_days_per_period__gte = wb_filters.NumberFilter(
        field_name="extra_days_per_period", method="filter_str_number_gte", lookup_expr="gte"
    )

    def filter_str_number_lte(self, queryset, name, value):
        if value:
            numerical_field_name = name.replace("_repr", "")
            return queryset.filter(**{f"{numerical_field_name}__lte": value})
        return queryset

    def filter_str_number_gte(self, queryset, name, value):
        if value:
            numerical_field_name = name.replace("_repr", "")
            return queryset.filter(**{f"{numerical_field_name}__gte": value})
        return queryset

    class Meta:
        model = EmployeeHumanResource
        fields = {"profile": ["exact"], "position": ["exact"], "extra_days_frequency": ["exact"]}


class EmployeeFilterSet(BaseEmployeeFilterSet):
    top_position_repr = wb_filters.ModelChoiceFilter(
        label=_("Position"),
        queryset=Position.objects.all(),
        endpoint=Position.get_representation_endpoint(),
        value_key=Position.get_representation_value_key(),
        label_key=Position.get_representation_label_key(),
        filter_params={"height": 1},
        method="filter_top_position",
    )

    def filter_top_position(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(position__parent__isnull=False) & Q(position__parent__in=value.get_descendants(include_self=True))
            ).distinct()
        return queryset

    class Meta:
        model = EmployeeHumanResource
        fields = {"calendar": ["exact"], "contract_type": ["exact"], "enrollment_at": ["gte", "lte"]}
