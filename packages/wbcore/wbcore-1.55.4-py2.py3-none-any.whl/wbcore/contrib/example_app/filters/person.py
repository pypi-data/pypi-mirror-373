from django.db.models import Q, QuerySet
from django.utils.translation import gettext_lazy as _

from wbcore import filters
from wbcore.contrib.example_app.models import Match, Player, Role, SportPerson, Team


class SportPersonRepresentationFilter(filters.FilterSet):
    match = filters.ModelChoiceFilter(
        label=_("Participating In"),
        queryset=Match.objects.all(),
        endpoint=Match.get_representation_endpoint(),
        value_key=Match.get_representation_value_key(),
        label_key=Match.get_representation_label_key(),
        method="filter_by_match",
        help_text=_("All persons participating in a selected Match."),
    )

    def filter_by_match(self, queryset: QuerySet[SportPerson], name, value: Match) -> QuerySet[SportPerson]:
        return queryset.filter(
            Q(coached_team__home_matches=value)
            | Q(coached_team__away_matches=value)
            | Q(refereed_matches=value)
            | Q(
                id__in=Player.objects.filter(
                    Q(current_team__home_matches=value) | Q(current_team__away_matches=value)
                ).values("id")
            )
        ).distinct()

    class Meta:
        model = SportPerson
        fields = {"roles": ["exact", "icontains"]}


class SportPersonFilter(SportPersonRepresentationFilter):
    roles = filters.ModelMultipleChoiceFilter(
        label=_("Roles"),
        queryset=Role.objects.all(),
        endpoint=Role.get_representation_endpoint(),
        value_key=Role.get_representation_value_key(),
        label_key=Role.get_representation_label_key(),
    )

    class Meta:
        model = SportPerson
        fields = {
            "last_name": ["exact", "icontains"],
            "first_name": ["exact", "icontains"],
        }


class PlayerTeamFilter(SportPersonFilter):
    former_teams = filters.ModelMultipleChoiceFilter(
        label=_("Former Teams"),
        queryset=Team.objects.all(),
        endpoint=Team.get_representation_endpoint(),
        value_key=Team.get_representation_value_key(),
        label_key=Team.get_representation_label_key(),
    )
    transfer_value__gte = filters.NumberFilter(label=_("Market Value"), lookup_expr="gte", field_name="transfer_value")
    transfer_value__lte = filters.NumberFilter(label=_("Market Value"), lookup_expr="lte", field_name="transfer_value")

    class Meta(SportPersonFilter.Meta):
        model = Player
        fields = SportPersonFilter.Meta.fields | {
            "position": ["exact", "icontains"],
        }


class PlayerFilter(PlayerTeamFilter):
    current_team = filters.ModelMultipleChoiceFilter(
        label=_("Current Teams"),
        queryset=Team.objects.all(),
        endpoint=Team.get_representation_endpoint(),
        value_key=Team.get_representation_value_key(),
        label_key=Team.get_representation_label_key(),
    )
