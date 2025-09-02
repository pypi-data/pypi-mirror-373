from django.utils.translation import gettext_lazy as _

from wbcore import filters
from wbcore.contrib.example_app.models import Stadium, Team
from wbcore.contrib.geography.models import Geography


class StadiumFilter(filters.FilterSet):
    capacity__gte = filters.NumberFilter(label=_("Capacity"), lookup_expr="gte", field_name="capacity")
    capacity__lte = filters.NumberFilter(label=_("Capacity"), lookup_expr="lte", field_name="capacity")
    teams_playing = filters.ModelChoiceFilter(
        label=_("Team Playing"),
        queryset=Team.objects.all(),
        endpoint=Team.get_representation_endpoint(),
        value_key=Team.get_representation_value_key(),
        label_key=Team.get_representation_label_key(),
    )
    city = filters.ModelMultipleChoiceFilter(
        label=_("Cities"),
        queryset=Geography.cities.all(),
        endpoint=Geography.get_representation_endpoint(),
        value_key=Geography.get_representation_value_key(),
        label_key=Geography.get_representation_label_key(),
        filter_params={"level": 3},
    )

    class Meta:
        model = Stadium
        fields = {
            "name": ["exact", "icontains"],
        }
