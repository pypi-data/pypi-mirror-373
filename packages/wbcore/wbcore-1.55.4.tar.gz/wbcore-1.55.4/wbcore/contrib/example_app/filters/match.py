from django.utils.translation import gettext_lazy as _

from wbcore import filters
from wbcore.contrib.example_app.models import (
    League,
    Match,
    Sport,
    SportPerson,
    Stadium,
    Team,
)


class MatchBaseFilter(filters.FilterSet):
    date_time__gte = filters.DateTimeFilter(
        label=_("Date Time"),
        lookup_expr="gte",
        field_name="date_time",
    )
    date_time__lte = filters.DateTimeFilter(
        label=_("Date Time"),
        lookup_expr="lte",
        field_name="date_time",
    )
    home = filters.ModelChoiceFilter(
        label=_("Home"),
        queryset=Team.objects.all(),
        endpoint=Team.get_representation_endpoint(),
        value_key=Team.get_representation_value_key(),
        label_key=Team.get_representation_label_key(),
    )
    away = filters.ModelChoiceFilter(
        label=_("Away"),
        queryset=Team.objects.all(),
        endpoint=Team.get_representation_endpoint(),
        value_key=Team.get_representation_value_key(),
        label_key=Team.get_representation_label_key(),
    )
    score_home__gte = filters.NumberFilter(label=_("Home Score"), lookup_expr="gte", field_name="score_home")
    score_home__lte = filters.NumberFilter(label=_("Home Score"), lookup_expr="lte", field_name="score_home")
    score_away__gte = filters.NumberFilter(label=_("Away Score"), lookup_expr="gte", field_name="score_away")
    score_away__lte = filters.NumberFilter(label=_("Away Score"), lookup_expr="lte", field_name="score_away")
    referee = filters.ModelMultipleChoiceFilter(
        label=_("Referees"),
        queryset=SportPerson.objects.all(),
        endpoint=SportPerson.get_representation_endpoint(),
        value_key=SportPerson.get_representation_value_key(),
        label_key=SportPerson.get_representation_label_key(),
    )
    status = filters.ChoiceFilter(
        label=_("Status"), choices=Match.MatchStatus.choices, initial=Match.MatchStatus.ONGOING
    )
    sport = filters.ModelMultipleChoiceFilter(
        label=_("Sports"),
        queryset=Sport.objects.all(),
        endpoint=Sport.get_representation_endpoint(),
        value_key=Sport.get_representation_value_key(),
        label_key=Sport.get_representation_label_key(),
    )

    class Meta:
        model = Match
        fields = {}


class MatchLeagueFilter(MatchBaseFilter):
    stadium = filters.ModelMultipleChoiceFilter(
        label=_("Stadiums"),
        queryset=Stadium.objects.all(),
        endpoint=Stadium.get_representation_endpoint(),
        value_key=Stadium.get_representation_value_key(),
        label_key=Stadium.get_representation_label_key(),
    )


class MatchStadiumFilter(MatchBaseFilter):
    league = filters.ModelMultipleChoiceFilter(
        label=_("Leagues"),
        queryset=League.objects.all(),
        endpoint=League.get_representation_endpoint(),
        value_key=League.get_representation_value_key(),
        label_key=League.get_representation_label_key(),
    )


class MatchFilter(MatchStadiumFilter):
    stadium = filters.ModelMultipleChoiceFilter(
        label=_("Stadiums"),
        queryset=Stadium.objects.all(),
        endpoint=Stadium.get_representation_endpoint(),
        value_key=Stadium.get_representation_value_key(),
        label_key=Stadium.get_representation_label_key(),
    )
