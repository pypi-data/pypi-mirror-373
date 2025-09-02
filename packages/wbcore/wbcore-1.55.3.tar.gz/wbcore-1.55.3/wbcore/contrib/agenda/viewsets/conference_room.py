from wbcore import viewsets
from wbcore.contrib.agenda.filters import BuildingFilter, ConferenceRoomFilter
from wbcore.contrib.agenda.models import Building, ConferenceRoom
from wbcore.contrib.agenda.serializers import (
    BuildingModelSerializer,
    BuildingRepresentationSerializer,
    ConferenceRoomModelSerializer,
    ConferenceRoomRepresentationSerializer,
)

from .buttons import BuildingButtonConfig
from .display import BuildingDisplay, ConferenceRoomDisplay
from .titles import BuildingTitleConfig, ConferenceRoomTitleConfig


class BuildingModelViewSet(viewsets.ModelViewSet):
    LIST_DOCUMENTATION = "agenda/markdown/documentation/building.md"
    queryset = Building.objects.all()
    serializer_class = BuildingModelSerializer
    display_config_class = BuildingDisplay
    title_config_class = BuildingTitleConfig
    search_fields = ("name",)
    ordering_fields = ordering = ("name",)
    button_config_class = BuildingButtonConfig
    filterset_class = BuildingFilter


class BuildingRepresentationViewSet(viewsets.RepresentationViewSet):
    serializer_class = BuildingRepresentationSerializer
    search_fields = ("name",)
    queryset = Building.objects.all()


class ConferenceRoomModelViewSet(viewsets.ModelViewSet):
    LIST_DOCUMENTATION = "agenda/markdown/documentation/conferenceroom.md"
    queryset = ConferenceRoom.objects.all()
    serializer_class = ConferenceRoomModelSerializer
    display_config_class = ConferenceRoomDisplay
    title_config_class = ConferenceRoomTitleConfig
    search_fields = ("name",)
    ordering_fields = ordering = ("name",)
    filterset_class = ConferenceRoomFilter


class ConferenceRoomRepresentationViewSet(viewsets.RepresentationViewSet):
    serializer_class = ConferenceRoomRepresentationSerializer
    search_fields = ("name",)
    queryset = ConferenceRoom.objects.all()
