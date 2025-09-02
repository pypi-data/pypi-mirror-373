from django.contrib.messages import warning
from django.db.models import Q, QuerySet
from django.utils.translation import gettext as _

from wbcore import viewsets
from wbcore.contrib.example_app.filters import (
    MatchFilter,
    MatchLeagueFilter,
    MatchStadiumFilter,
)
from wbcore.contrib.example_app.models import Match
from wbcore.contrib.example_app.serializers import (
    MatchModelSerializer,
    MatchRepresentationSerializer,
    ReadOnlyMatchModelSerializer,
)
from wbcore.contrib.example_app.viewsets.displays import (
    MatchDisplayConfig,
    MatchLeagueDisplayConfig,
    MatchStadiumDisplayConfig,
)
from wbcore.contrib.example_app.viewsets.endpoints import (
    MatchLeagueEndpointConfig,
    MatchStadiumEndpointConfig,
)
from wbcore.contrib.example_app.viewsets.titles import (
    MatchLeagueTitleConfig,
    MatchStadiumTitleConfig,
    MatchTitleConfig,
)


class MatchModelViewSet(viewsets.ModelViewSet):
    display_config_class = MatchDisplayConfig
    queryset = Match.objects.all()
    serializer_class = MatchModelSerializer
    title_config_class = MatchTitleConfig
    search_fields = ("home__name", "away__name", "league__computed_str", "sport__name")
    ordering = ("-date_time", "home__name", "away__name")
    ordering_fields = (
        "home__name",
        "away__name",
        "league__computed_str",
        "date_time",
        "stadium__name",
        "score_home",
        "score_away",
        "referee__computed_str",
        "sport__name",
    )
    filterset_class = MatchFilter

    def get_serializer_class(self):
        if "pk" in self.kwargs:
            if match_obj := self.get_object():
                if match_obj.status != Match.MatchStatus.SCHEDULED:
                    return ReadOnlyMatchModelSerializer
        return super().get_serializer_class()

    def add_messages(self, request, instance: Match | None = None, **kwargs):
        if instance and (home_stadium := instance.home.home_stadium) and instance.stadium.pk != home_stadium.pk:
            warning(request, _("Home team's home stadium not selected!"))

    def get_queryset(self) -> QuerySet[Match]:
        queryset = super().get_queryset().select_related("home", "away", "stadium", "referee", "league", "sport")
        if team_id := self.kwargs.get("team_id"):
            queryset = queryset.filter(Q(home=team_id) | Q(away=team_id))
        return queryset


class MatchStadiumModelViewSet(MatchModelViewSet):
    display_config_class = MatchStadiumDisplayConfig
    ordering_fields = (
        "home__name",
        "away__name",
        "date_time",
        "score_home",
        "score_away",
        "referee__computed_str",
        "league__computed_str",
        "sport__name",
    )
    filterset_class = MatchStadiumFilter
    endpoint_config_class = MatchStadiumEndpointConfig
    title_config_class = MatchStadiumTitleConfig

    def get_queryset(self) -> QuerySet[Match]:
        queryset = super().get_queryset()
        if stadium_id := self.kwargs.get("stadium_id"):
            queryset = queryset.filter(stadium=stadium_id)
        return queryset


class MatchLeagueModelViewSet(MatchModelViewSet):
    display_config_class = MatchLeagueDisplayConfig
    ordering_fields = (
        "home__name",
        "away__name",
        "date_time",
        "score_home",
        "score_away",
        "referee__computed_str",
        "stadium__name",
        "sport__name",
    )
    filterset_class = MatchLeagueFilter
    endpoint_config_class = MatchLeagueEndpointConfig
    title_config_class = MatchLeagueTitleConfig

    def get_queryset(self) -> QuerySet[Match]:
        queryset = super().get_queryset()
        if league_id := self.kwargs.get("league_id"):
            queryset = queryset.filter(league=league_id)
        return queryset


class MatchRepresentationViewSet(viewsets.RepresentationViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchRepresentationSerializer
    search_fields = ("computed_str",)
