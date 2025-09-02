from django.utils.translation import gettext_lazy as _

from wbcore import filters
from wbcore.contrib.example_app.models import League, Sport


class SportFilter(filters.FilterSet):
    leagues = filters.ModelChoiceFilter(
        label=_("Associated League"),
        queryset=League.objects.all(),
        endpoint=League.get_representation_endpoint(),
        value_key=League.get_representation_value_key(),
        label_key=League.get_representation_label_key(),
    )
    match_duration__gte = filters.NumberFilter(
        label=_("Match Duration"), lookup_expr="gte", field_name="match_duration"
    )
    match_duration__lte = filters.NumberFilter(
        label=_("Match Duration"), lookup_expr="lte", field_name="match_duration"
    )

    class Meta:
        model = Sport
        fields = {
            "name": ["exact", "icontains"],
            "rules": ["exact", "icontains"],
        }
