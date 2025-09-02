from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from wbcore import filters
from wbcore.contrib.example_app.models import Player, SportPerson, Stadium, Team
from wbcore.contrib.geography.models import Geography


class TeamStadiumFilter(filters.FilterSet):
    founded_date__gte = filters.DateFilter(
        label=_("Founded Date"),
        lookup_expr="gte",
        field_name="founded_date",
    )
    founded_date__lte = filters.DateFilter(
        label=_("Founded Date"),
        lookup_expr="lte",
        field_name="founded_date",
    )
    coach = filters.ModelMultipleChoiceFilter(
        label=_("Coaches"),
        queryset=SportPerson.objects.all(),
        endpoint=SportPerson.get_representation_endpoint(),
        value_key=SportPerson.get_representation_value_key(),
        label_key=SportPerson.get_representation_label_key(),
    )
    current_players = filters.ModelChoiceFilter(
        label=_("Current Player"),
        queryset=Player.objects.all(),
        endpoint=Player.get_representation_endpoint(),
        value_key=Player.get_representation_value_key(),
        label_key=Player.get_representation_label_key(),
    )
    former_players = filters.ModelChoiceFilter(
        label=_("Former Player"),
        queryset=Player.objects.all(),
        endpoint=Player.get_representation_endpoint(),
        value_key=Player.get_representation_value_key(),
        label_key=Player.get_representation_label_key(),
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
        model = Team
        fields = {
            "name": ["exact", "icontains"],
        }


class TeamFilter(TeamStadiumFilter):
    opponent = filters.ModelChoiceFilter(
        label=_("Opponent"),
        queryset=Team.objects.all(),
        endpoint=Team.get_representation_endpoint(),
        value_key=Team.get_representation_value_key(),
        label_key=Team.get_representation_label_key(),
        method="filter_opponent",
    )

    def filter_opponent(self, queryset: QuerySet[Team], name, value: Team) -> QuerySet[Team]:
        if value:
            return queryset.exclude(id=value.id)
        return queryset

    home_stadium = filters.ModelMultipleChoiceFilter(
        label=_("Stadiums"),
        queryset=Stadium.objects.all(),
        endpoint=Stadium.get_representation_endpoint(),
        value_key=Stadium.get_representation_value_key(),
        label_key=Stadium.get_representation_label_key(),
    )
