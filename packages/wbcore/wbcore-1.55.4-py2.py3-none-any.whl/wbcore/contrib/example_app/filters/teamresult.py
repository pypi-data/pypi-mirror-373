from django.utils.translation import gettext_lazy as _

from wbcore import filters
from wbcore.contrib.example_app.models import League, Team, TeamResults


class TeamResultsLeagueFilter(filters.FilterSet):
    team = filters.ModelChoiceFilter(
        label=_("Team"),
        queryset=Team.objects.all(),
        endpoint=Team.get_representation_endpoint(),
        value_key=Team.get_representation_value_key(),
        label_key=Team.get_representation_label_key(),
    )
    points__gte = filters.NumberFilter(label=_("Points"), lookup_expr="gte", field_name="points")
    points__lte = filters.NumberFilter(label=_("Points"), lookup_expr="lte", field_name="points")
    match_points_for__gte = filters.NumberFilter(
        label=_("Match Points For"), lookup_expr="gte", field_name="match_points_for"
    )
    match_points_for__lte = filters.NumberFilter(
        label=_("Match Points For"), lookup_expr="lte", field_name="match_points_for"
    )
    match_points_against__gte = filters.NumberFilter(
        label=_("Match Points Against"), lookup_expr="gte", field_name="match_points_against"
    )
    match_points_against__lte = filters.NumberFilter(
        label=_("Match Points Against"), lookup_expr="lte", field_name="match_points_against"
    )
    wins__gte = filters.NumberFilter(label=_("Wins"), lookup_expr="gte", field_name="wins")
    wins__lte = filters.NumberFilter(label=_("Points"), lookup_expr="lte", field_name="wins")
    draws__gte = filters.NumberFilter(label=_("Draws"), lookup_expr="gte", field_name="draws")
    draws__lte = filters.NumberFilter(label=_("Draws"), lookup_expr="lte", field_name="draws")
    losses__gte = filters.NumberFilter(label=_("Losses"), lookup_expr="gte", field_name="losses")
    losses__lte = filters.NumberFilter(label=_("Losses"), lookup_expr="lte", field_name="losses")

    class Meta:
        model = TeamResults
        fields = {}


class TeamResultsFilter(TeamResultsLeagueFilter):
    league = filters.ModelChoiceFilter(
        label=_("League"),
        queryset=League.objects.all(),
        endpoint=League.get_representation_endpoint(),
        value_key=League.get_representation_value_key(),
        label_key=League.get_representation_label_key(),
    )
