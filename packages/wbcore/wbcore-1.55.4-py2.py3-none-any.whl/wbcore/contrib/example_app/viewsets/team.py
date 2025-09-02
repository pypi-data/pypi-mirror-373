from django.db.models import F, QuerySet

from wbcore import viewsets
from wbcore.contrib.example_app.filters import TeamFilter, TeamStadiumFilter
from wbcore.contrib.example_app.models import Team
from wbcore.contrib.example_app.serializers import (
    TeamModelSerializer,
    TeamRepresentationSerializer,
)
from wbcore.contrib.example_app.viewsets.buttons import TeamButtonConfig
from wbcore.contrib.example_app.viewsets.displays import (
    TeamDisplayConfig,
    TeamStadiumDisplayConfig,
)
from wbcore.contrib.example_app.viewsets.endpoints import TeamStadiumEndpointConfig
from wbcore.contrib.example_app.viewsets.titles import (
    TeamStadiumTitleConfig,
    TeamTitleConfig,
)
from wbcore.viewsets.mixins import OrderableMixin


class TeamModelViewSet(OrderableMixin, viewsets.ModelViewSet):
    button_config_class = TeamButtonConfig
    display_config_class = TeamDisplayConfig
    title_config_class = TeamTitleConfig

    queryset = Team.objects.all()
    search_fields = ("name", "city__representation")
    serializer_class = TeamModelSerializer
    ordering_fields = (
        "name",
        "city__representation",
        "founded_date",
        "coach__computed_str",
        "home_stadium__name",
    )
    ordering = ("order", "name")
    filterset_class = TeamFilter

    def get_queryset(self) -> QuerySet[Team]:
        return (
            super()
            .get_queryset()
            .annotate(_group_key=F("id"))
            .select_related("city", "coach", "home_stadium")
            .prefetch_related("opponents")
        )


class TeamStadiumModelViewSet(TeamModelViewSet):
    display_config_class = TeamStadiumDisplayConfig
    ordering_fields = ("name", "city__representation", "founded_date", "coach__computed_str")
    filterset_class = TeamStadiumFilter
    endpoint_config_class = TeamStadiumEndpointConfig
    title_config_class = TeamStadiumTitleConfig

    def get_queryset(self) -> QuerySet[Team]:
        queryset = super().get_queryset()
        if stadium_id := self.kwargs.get("stadium_id"):
            queryset = queryset.filter(home_stadium=stadium_id)
        return queryset


class TeamRepresentationViewSet(viewsets.RepresentationViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamRepresentationSerializer
    search_fields = ("name",)
    filterset_class = TeamFilter
