from django.utils.translation import gettext_lazy as _
from wbcore import filters as wb_filters


def add_position_filter(sender, request=None, *args, **kwargs):
    from wbcore.contrib.directory.models import Entry

    from wbhuman_resources.models import Position

    def filter_position(queryset, name, value):
        if value:
            ids = value.get_employees().values_list("profile")
            entries = Entry.objects.filter(id__in=ids)
            return queryset.filter(participants__in=entries)
        return queryset

    return {
        "position": wb_filters.ModelChoiceFilter(
            label=_("Participant's position"),
            field_name="position",
            queryset=Position.objects.all(),
            endpoint=Position.get_representation_endpoint(),
            value_key=Position.get_representation_value_key(),
            label_key=Position.get_representation_label_key(),
            method=filter_position,
        )
    }
