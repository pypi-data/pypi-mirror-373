from django.db.models import QuerySet

from wbcore import viewsets
from wbcore.contrib.example_app.filters import LeagueFilter, LeagueSportFilter
from wbcore.contrib.example_app.models import League
from wbcore.contrib.example_app.serializers import (
    LeagueModelSerializer,
    LeagueRepresentationSerializer,
)
from wbcore.contrib.example_app.viewsets.displays import (
    LeagueDisplayConfig,
    LeagueSportDisplayConfig,
)
from wbcore.contrib.example_app.viewsets.endpoints import LeagueSportEndpointConfig
from wbcore.contrib.example_app.viewsets.titles import (
    LeagueSportTitleConfig,
    LeagueTitleConfig,
)


class LeagueModelViewSet(viewsets.ModelViewSet):
    display_config_class = LeagueDisplayConfig
    queryset = League.objects.all()
    search_fields = ("name", "sport__name")
    serializer_class = LeagueModelSerializer
    title_config_class = LeagueTitleConfig
    ordering_fields = (
        "name",
        "country__name",
        "established_date",
        "commissioner__computed_str",
        "website",
        "sport__name",
        "points_per_win",
        "points_per_draw",
        "points_per_loss",
    )
    ordering = ("name", "sport__name")
    filterset_class = LeagueFilter

    def get_queryset(self) -> QuerySet[League]:
        return super().get_queryset().select_related("sport", "country", "commissioner")


class LeagueSportModelViewSet(LeagueModelViewSet):
    display_config_class = LeagueSportDisplayConfig
    ordering_fields = (
        "name",
        "country__name",
        "established_date",
        "commissioner__computed_str",
        "website",
        "points_per_win",
        "points_per_draw",
        "points_per_loss",
    )
    ordering = ("name",)
    filterset_class = LeagueSportFilter
    endpoint_config_class = LeagueSportEndpointConfig
    title_config_class = LeagueSportTitleConfig

    def get_queryset(self) -> QuerySet[League]:
        queryset = super().get_queryset()
        if sport_id := self.kwargs.get("sport_id"):
            queryset = queryset.filter(sport=sport_id)
        return queryset


class LeagueRepresentationViewSet(viewsets.RepresentationViewSet):
    queryset = League.objects.all()
    serializer_class = LeagueRepresentationSerializer
    search_fields = ("name",)
    filterset_fields = ("sport",)
