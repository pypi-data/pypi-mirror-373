from django.utils.translation import gettext_lazy as _

from wbcore import filters
from wbcore.contrib.example_app.models import League, Sport, SportPerson, Team
from wbcore.contrib.geography.models import Geography


class LeagueSportFilter(filters.FilterSet):
    established_date__gte = filters.DateFilter(
        label=_("Established Date"),
        lookup_expr="gte",
        field_name="established_date",
    )
    established_date__lte = filters.DateFilter(
        label=_("Established Date"),
        lookup_expr="lte",
        field_name="established_date",
    )
    commissioner = filters.ModelMultipleChoiceFilter(
        label=_("Commissioners"),
        queryset=SportPerson.objects.all(),
        endpoint=SportPerson.get_representation_endpoint(),
        value_key=SportPerson.get_representation_value_key(),
        label_key=SportPerson.get_representation_label_key(),
    )
    country = filters.ModelMultipleChoiceFilter(
        label=_("Countries"),
        queryset=Geography.countries.all(),
        endpoint=Geography.get_representation_endpoint(),
        value_key=Geography.get_representation_value_key(),
        label_key=Geography.get_representation_label_key(),
        filter_params={"level": 1},
    )
    teams = filters.ModelChoiceFilter(
        label=_("Team"),
        queryset=Team.objects.all(),
        endpoint=Team.get_representation_endpoint(),
        value_key=Team.get_representation_value_key(),
        label_key=Team.get_representation_label_key(),
    )
    points_per_win__gte = filters.NumberFilter(
        label=_("Points Per Win"), lookup_expr="gte", field_name="points_per_win"
    )
    points_per_win__lte = filters.NumberFilter(
        label=_("Points Per Win"), lookup_expr="lte", field_name="points_per_win"
    )
    points_per_draw__gte = filters.NumberFilter(
        label=_("Points Per Draw"), lookup_expr="gte", field_name="points_per_draw"
    )
    points_per_draw__lte = filters.NumberFilter(
        label=_("Points Per Draw"), lookup_expr="lte", field_name="points_per_draw"
    )
    points_per_loss__gte = filters.NumberFilter(
        label=_("Points Per Loss"), lookup_expr="gte", field_name="points_per_loss"
    )
    points_per_loss__lte = filters.NumberFilter(
        label=_("Points Per Loss"), lookup_expr="lte", field_name="points_per_loss"
    )

    class Meta:
        model = League
        fields = {
            "name": ["exact", "icontains"],
            "website": ["exact", "icontains"],
        }


class LeagueFilter(LeagueSportFilter):
    sport = filters.ModelMultipleChoiceFilter(
        label=_("Sports"),
        queryset=Sport.objects.all(),
        endpoint=Sport.get_representation_endpoint(),
        value_key=Sport.get_representation_value_key(),
        label_key=Sport.get_representation_label_key(),
    )
