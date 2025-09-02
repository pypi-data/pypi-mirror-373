from wbcore import viewsets
from wbcore.contrib.example_app.filters import SportFilter
from wbcore.contrib.example_app.models import Sport
from wbcore.contrib.example_app.serializers import (
    SportModelSerializer,
    SportRepresentationSerializer,
)
from wbcore.contrib.example_app.viewsets.displays import SportDisplayConfig
from wbcore.contrib.example_app.viewsets.titles import SportTitleConfig


class SportModelViewSet(viewsets.ModelViewSet):
    display_config_class = SportDisplayConfig
    queryset = Sport.objects.all()
    search_fields = ("name",)
    serializer_class = SportModelSerializer
    title_config_class = SportTitleConfig
    ordering_fields = ("name", "rules", "match_duration")
    ordering = ("name", "id")
    filterset_class = SportFilter


class SportRepresentationViewSet(viewsets.RepresentationViewSet):
    queryset = Sport.objects.all()
    serializer_class = SportRepresentationSerializer
    search_fields = ("name",)
