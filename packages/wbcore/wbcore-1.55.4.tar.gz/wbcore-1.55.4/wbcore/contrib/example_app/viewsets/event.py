import pandas as pd
import plotly.graph_objects as go
import tablib
from django.db.models import (
    Case,
    Count,
    Exists,
    F,
    IntegerField,
    OuterRef,
    Q,
    QuerySet,
    Subquery,
    When,
)
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from wbcore import viewsets
from wbcore.contrib.example_app.filters import (
    EventFilter,
    EventMatchFilter,
    EventTypeFilter,
    EventTypeSportFilter,
    PlayerStatisticsChartFilter,
)
from wbcore.contrib.example_app.models import (
    Event,
    EventType,
    Match,
    Player,
    SportPerson,
)
from wbcore.contrib.example_app.serializers import (
    EventModelSerializer,
    EventRepresentationSerializer,
    EventTypeModelSerializer,
    EventTypeRepresentationSerializer,
    LeaguePlayerStatisticsModelSerializer,
    LeagueTeamStatisticsModelSerializer,
)
from wbcore.contrib.example_app.viewsets.displays import (
    EventDisplayConfig,
    EventMatchDisplayConfig,
    EventTypeDisplayConfig,
    EventTypeSportDisplayConfig,
    LeaguePlayerStatisticsDisplayConfig,
    LeagueTeamStatisticsDisplayConfig,
)
from wbcore.contrib.example_app.viewsets.endpoints import (
    EventEndpointConfig,
    EventMatchEndpointConfig,
    EventTypeSportEndpointConfig,
    LeagueStatisticsEndpointConfig,
)
from wbcore.contrib.example_app.viewsets.titles import (
    EventTitleConfig,
    EventTypeSportTitleConfig,
    EventTypeTitleConfig,
    PlayerStatisticsChartTitleConfig,
)


class EventModelViewSet(viewsets.ModelViewSet):
    display_config_class = EventDisplayConfig
    queryset = Event.objects.all()
    search_fields = ("person__computed_str", "event_type__name")
    serializer_class = EventModelSerializer
    title_config_class = EventTitleConfig
    ordering_fields = ("match__home", "minute", "person__computed_str", "event_type__name")
    ordering = ("match__id", "minute", "person__computed_str", "event_type__name")
    filterset_class = EventFilter
    endpoint_config_class = EventEndpointConfig

    @action(detail=False, methods=["PATCH"])
    def matchevent(self, request, pk=None):
        person_id = request.POST.get("person")
        minute = request.POST.get("minute")
        event_type_id = request.GET.get("event_type")
        match_id = request.GET.get("match")
        data = {"person": person_id, "minute": minute, "event_type": event_type_id, "match": match_id}
        serializer = self.serializer_class(data=data, context={"request": request})
        if serializer.is_valid():
            person = get_object_or_404(SportPerson, pk=person_id)
            event_type = get_object_or_404(EventType, pk=event_type_id)
            match = get_object_or_404(Match, pk=match_id)
            event = Event(person=person, minute=minute, event_type=event_type, match=match)
            event.save()
            return Response("Event Created", status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self) -> QuerySet[Event]:
        return super().get_queryset().select_related("person", "event_type", "match")


class PlayerStatisticsChartModelViewSet(viewsets.ChartViewSet):
    EXPORT_ALLOWED = True
    queryset = Event.objects.all()
    title_config_class = PlayerStatisticsChartTitleConfig
    filterset_class = PlayerStatisticsChartFilter

    def get_queryset(self):
        return super().get_queryset().filter(person=self.kwargs["player_id"])

    def _get_data_for_export(self, queryset, **kwargs) -> tablib.Dataset:
        dataset = tablib.Dataset(headers=["League", "Event"])
        for event in queryset.select_related("event_type", "match", "match__league"):
            dataset.append([event.match.league.name, event.event_type.name])
        return dataset

    def get_plotly(self, queryset):
        fig = go.Figure()
        if queryset.exists():
            df = pd.DataFrame(queryset.values("match__league__name", "event_type__name"))
            df.fillna("None", inplace=True)
            pivot_df = df.pivot_table(
                index="match__league__name",
                columns="event_type__name",
                aggfunc="size",
                fill_value=0,
            )

            for event_type in pivot_df.columns:
                fig.add_trace(
                    go.Histogram(
                        histfunc="sum",
                        y=pivot_df[event_type],
                        x=pivot_df.index,
                        name=f"{event_type}s",
                    )
                )

            fig.update_layout(
                xaxis=dict(title=_("League")),
                yaxis=dict(title=_("Amount"), type="linear"),
                autosize=True,
                bargap=0.8,
                bargroupgap=0.7,
            )

        return fig


class LeaguePlayerStatisticsModelViewSet(viewsets.ModelViewSet):
    endpoint_config_class = LeagueStatisticsEndpointConfig
    serializer_class = LeaguePlayerStatisticsModelSerializer
    display_config_class = LeaguePlayerStatisticsDisplayConfig
    search_fields = ("person_name",)
    ordering_fields = ("person_name", "count")
    ordering = ("-count", "person_name", "person_id")

    def get_queryset(self) -> QuerySet[Event]:
        return (
            Event.objects.filter(
                match__league=self.kwargs["league_id"],
                event_type=self.kwargs["event_type_id"],
            )
            .values("person")
            .annotate(
                count=Count("person"),
                person_name=F("person__computed_str"),
                person_id=F("person_id"),
                id=F("person_id"),
            )
        )


class LeagueTeamStatisticsModelViewSet(viewsets.ModelViewSet):
    endpoint_config_class = LeagueStatisticsEndpointConfig
    serializer_class = LeagueTeamStatisticsModelSerializer
    display_config_class = LeagueTeamStatisticsDisplayConfig
    search_fields = ("team_name",)
    ordering_fields = ("team_name", "count")
    ordering = ("-count", "team_name", "team_id")

    def get_queryset(self) -> QuerySet[Event]:
        return (
            Event.objects.filter(
                Q(match__league=self.kwargs["league_id"])
                & Q(event_type=self.kwargs["event_type_id"])
                & Q(
                    Q(person__coached_team__isnull=False)
                    | Q(person__in=Player.objects.filter(current_team__isnull=False).values("id"))
                )
            )
            .values("person")
            .annotate(
                is_player=Exists(Player.objects.filter(id=OuterRef("person_id"), current_team__isnull=False)),
                is_coach=Q(person__coached_team__isnull=False),
                team_id=Case(
                    When(
                        is_player=True,
                        then=Subquery(Player.objects.filter(id=OuterRef("person_id")).values("current_team__id")[:1]),
                    ),
                    When(
                        is_coach=True,
                        then=F("person__coached_team__id"),
                    ),
                    output_field=IntegerField(),
                ),
            )
            .values("team_id")
            .annotate(
                count=Count("person"),
                id=F("team_id"),
                team_name=Case(
                    When(
                        is_player=True,
                        then=Subquery(
                            Player.objects.filter(id=OuterRef("person_id")).values("current_team__name")[:1]
                        ),
                    ),
                    When(
                        is_coach=True,
                        then=F("person__coached_team__name"),
                    ),
                ),
            )
        )


class EventMatchModelViewSet(EventModelViewSet):
    display_config_class = EventMatchDisplayConfig
    ordering_fields = ("minute", "person__computed_str", "event_type__name")
    ordering = ("minute", "person__computed_str", "event_type__name")
    filterset_class = EventMatchFilter
    endpoint_config_class = EventMatchEndpointConfig

    def get_queryset(self) -> QuerySet[Event]:
        queryset = super().get_queryset()
        if match_id := self.kwargs.get("match_id"):
            queryset = queryset.filter(match=match_id)
        return queryset


class EventRepresentationViewSet(viewsets.RepresentationViewSet):
    queryset = Event.objects.all()
    serializer_class = EventRepresentationSerializer
    search_fields = ("event_type__name", "minute", "person__computed_str")


class EventTypeModelViewSet(viewsets.ModelViewSet):
    display_config_class = EventTypeDisplayConfig
    queryset = EventType.objects.all()
    search_fields = ("name", "sport")
    serializer_class = EventTypeModelSerializer
    title_config_class = EventTypeTitleConfig
    ordering_fields = (
        "name",
        "points",
        "sport__name",
        "icon",
        "color",
    )
    ordering = ("sport", "name")
    filterset_class = EventTypeFilter

    def get_queryset(self) -> QuerySet[EventType]:
        return super().get_queryset().select_related("sport")


class EventTypeSportModelViewSet(EventTypeModelViewSet):
    display_config_class = EventTypeSportDisplayConfig
    ordering_fields = (
        "name",
        "points",
        "icon",
        "color",
    )
    ordering = ("name",)
    filterset_class = EventTypeSportFilter
    endpoint_config_class = EventTypeSportEndpointConfig
    title_config_class = EventTypeSportTitleConfig

    def get_queryset(self) -> QuerySet[EventType]:
        queryset = super().get_queryset()
        if sport_id := self.kwargs.get("sport_id"):
            queryset = queryset.filter(sport=sport_id)
        return queryset


class EventTypeRepresentationViewSet(viewsets.RepresentationViewSet):
    queryset = EventType.objects.all()
    serializer_class = EventTypeRepresentationSerializer
    search_fields = ("name",)
