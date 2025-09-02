from django.db.models import Avg, F, Max, Min, QuerySet, Sum

from wbcore import viewsets
from wbcore.contrib.example_app.filters import (
    PlayerFilter,
    PlayerTeamFilter,
    SportPersonFilter,
    SportPersonRepresentationFilter,
)
from wbcore.contrib.example_app.models import Player, SportPerson, Team
from wbcore.contrib.example_app.serializers import (
    PlayerModelSerializer,
    PlayerRepresentationSerializer,
    SportPersonModelSerializer,
    SportPersonRepresentationSerializer,
    SportPersonTooltipSerializer,
    TreeViewPlayerModelSerializer,
)
from wbcore.contrib.example_app.viewsets.buttons import PlayerButtonConfig
from wbcore.contrib.example_app.viewsets.displays import (
    PlayerDisplayConfig,
    PlayerTeamDisplayConfig,
    SportPersonDisplayConfig,
    SportPersonToolTipDisplayConfig,
)
from wbcore.contrib.example_app.viewsets.endpoints import PlayerTeamEndpointConfig
from wbcore.contrib.example_app.viewsets.titles import (
    PlayerTeamTitleConfig,
    PlayerTitleConfig,
    SportPersonTitleConfig,
)
from wbcore.utils.strings import format_number
from wbcore.viewsets.mixins import OrderableMixin, ReparentMixin


class SportPersonModelViewSet(viewsets.ModelViewSet):
    display_config_class = SportPersonDisplayConfig
    queryset = SportPerson.objects.all()
    search_fields = ("first_name", "last_name")
    serializer_class = SportPersonModelSerializer
    title_config_class = SportPersonTitleConfig
    ordering_fields = (
        "last_name",
        "first_name",
        "roles__title",
    )
    ordering = ("last_name", "first_name")
    filterset_class = SportPersonFilter

    def get_queryset(self) -> QuerySet[SportPerson]:
        return super().get_queryset().prefetch_related("roles")


class SportPersonRepresentationViewSet(viewsets.RepresentationViewSet):
    queryset = SportPerson.objects.all()
    serializer_class = SportPersonRepresentationSerializer
    search_fields = ("computed_str",)
    filterset_class = SportPersonRepresentationFilter


class SportPersonToolTipViewset(viewsets.ModelViewSet):
    IDENTIFIER = "example_app:persontooltip"
    queryset = SportPerson.objects.all()
    display_config_class = SportPersonToolTipDisplayConfig
    serializer_class = SportPersonTooltipSerializer
    title_config_class = SportPersonTitleConfig


class PlayerModelViewSet(SportPersonModelViewSet):
    display_config_class = PlayerDisplayConfig
    queryset = Player.objects.all()
    search_fields = SportPersonModelViewSet.search_fields + ("current_team__name",)
    serializer_class = PlayerModelSerializer
    title_config_class = PlayerTitleConfig
    ordering_fields = SportPersonModelViewSet.ordering_fields + (
        "position",
        "current_team__name",
        "former_teams__name",
        "transfer_value",
    )
    ordering = ("last_name", "first_name", "current_team__name", "id")
    filterset_class = PlayerFilter
    button_config_class = PlayerButtonConfig

    def get_aggregates(self, queryset: QuerySet[Player], paginated_queryset: QuerySet[Player]):
        transfer_sum = queryset.aggregate(s=Sum(F("transfer_value")))["s"] or 0
        transfer_average = queryset.aggregate(a=Avg(F("transfer_value")))["a"] or 0
        transfer_max = queryset.aggregate(m=Max(F("transfer_value")))["m"] or 0
        transfer_min = queryset.aggregate(m=Min(F("transfer_value")))["m"] or 0
        return {
            "transfer_value": {
                "Σ": format_number(transfer_sum),
                "⌀": format_number(transfer_average),
                "Max": format_number(transfer_max),
                "Min": format_number(transfer_min),
            }
        }

    def get_queryset(self) -> QuerySet[Player]:
        return super().get_queryset().select_related("current_team").prefetch_related("former_teams")


class PlayerRepresentationViewSet(viewsets.RepresentationViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerRepresentationSerializer
    search_fields = ("computed_str",)


class PlayerTeamModelViewSet(PlayerModelViewSet):
    display_config_class = PlayerTeamDisplayConfig
    ordering_fields = SportPersonModelViewSet.ordering_fields + (
        "position",
        "former_teams__name",
        "transfer_value",
    )
    ordering = ("last_name", "first_name", "id")
    filterset_class = PlayerTeamFilter
    title_config_class = PlayerTeamTitleConfig
    endpoint_config_class = PlayerTeamEndpointConfig

    def get_queryset(self) -> QuerySet[Player]:
        queryset = super().get_queryset()
        if team_id := self.kwargs.get("team_id"):
            queryset = queryset.filter(current_team=team_id)
        return queryset


class TreeViewPlayerModelViewSet(OrderableMixin, ReparentMixin, viewsets.ModelViewSet):
    PARENT_FIELD = "current_team"
    PARENT_MODEL = Team
    ordering = ("order", "computed_str", "id")
    filterset_class = PlayerFilter
    queryset = Player.objects.all()
    serializer_class = TreeViewPlayerModelSerializer
