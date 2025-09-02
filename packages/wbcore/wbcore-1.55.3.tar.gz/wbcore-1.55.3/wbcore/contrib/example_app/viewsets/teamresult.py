from django.db.models import Count, IntegerField, OuterRef, Q, QuerySet, Subquery
from django.db.models.functions import Coalesce

from wbcore import viewsets
from wbcore.contrib.example_app.filters import (
    TeamResultsFilter,
    TeamResultsLeagueFilter,
)
from wbcore.contrib.example_app.models import Match, TeamResults
from wbcore.contrib.example_app.serializers import (
    TeamResultsModelSerializer,
    TeamResultsRepresentationSerializer,
)
from wbcore.contrib.example_app.viewsets.displays import (
    TeamResultsDisplayConfig,
    TeamResultsLeagueDisplayConfig,
)
from wbcore.contrib.example_app.viewsets.endpoints import TeamResultsEndpointConfig
from wbcore.contrib.example_app.viewsets.titles import (
    TeamResultsLeagueTitleConfig,
    TeamResultsTitleConfig,
)


class TeamResultsModelViewSet(viewsets.ModelViewSet):
    display_config_class = TeamResultsDisplayConfig
    queryset = TeamResults.objects.all()
    search_fields = ("team__name", "league__computed_str")
    ordering_fields = (
        "league__computed_str",
        "points",
        "match_point_difference",
        "match_points_for",
        "team__name",
        "match_points_against",
        "wins",
        "draws",
        "losses",
    )
    ordering = (
        "league__computed_str",
        "-points",
        "-match_point_difference",
        "-match_points_for",
        "team__name",
    )
    serializer_class = TeamResultsModelSerializer
    title_config_class = TeamResultsTitleConfig
    filterset_class = TeamResultsFilter
    endpoint_config_class = TeamResultsEndpointConfig

    def get_queryset(self) -> QuerySet[TeamResults]:
        games_subquery = (
            Match.objects.filter(
                Q(league=OuterRef("league"))
                & Q(Q(home=OuterRef("team")) | Q(away=OuterRef("team")))
                & Q(status=Match.MatchStatus.FINISHED)
            )
            .values("league__pk")
            .annotate(games=Count("id"))
            .values("games")
        )

        qs = (
            super()
            .get_queryset()
            .select_related("league", "team")
            .annotate(
                games_played=Coalesce(Subquery(games_subquery, output_field=IntegerField()), 0),
            )
        )
        return qs


class TeamResultsRepresentationViewSet(viewsets.RepresentationViewSet):
    queryset = TeamResults.objects.all()
    serializer_class = TeamResultsRepresentationSerializer
    search_fields = ("team__name", "league__computed_str")


class TeamResultsLeagueModelViewSet(TeamResultsModelViewSet):
    title_config_class = TeamResultsLeagueTitleConfig
    display_config_class = TeamResultsLeagueDisplayConfig
    filterset_class = TeamResultsLeagueFilter
    search_fields = ("team__name",)
    ordering_fields = (
        "points",
        "match_point_difference",
        "match_points_for",
        "team__name",
        "match_points_against",
        "wins",
        "draws",
        "losses",
    )
    ordering = (
        "-points",
        "-match_point_difference",
        "-match_points_for",
        "team__name",
    )

    def get_queryset(self) -> QuerySet[TeamResults]:
        queryset = super().get_queryset()
        if league_id := self.kwargs.get("league_id"):
            queryset = queryset.filter(league=league_id)
        return queryset
