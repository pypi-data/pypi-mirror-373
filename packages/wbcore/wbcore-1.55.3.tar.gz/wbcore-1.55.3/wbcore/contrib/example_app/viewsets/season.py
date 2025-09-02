from wbcore import viewsets
from wbcore.contrib.example_app.models import Season
from wbcore.contrib.example_app.serializers import (
    SeasonModelSerializer,
    SeasonRepresentationSerializer,
)
from wbcore.contrib.example_app.viewsets.displays import SeasonDisplayConfig


class SeasonModelViewSet(viewsets.ModelViewSet):
    display_config_class = SeasonDisplayConfig
    queryset = Season.objects.all()
    search_fields = ("name", "winner")
    serializer_class = SeasonModelSerializer
    ordering_fields = ("name", "winner", "top_scorer", "start_date", "end_date")
    ordering = ("name", "id")
    filterset_fields = ("name", "winner")


class SeasonRepresentationViewSet(viewsets.RepresentationViewSet):
    queryset = Season.objects.all()
    serializer_class = SeasonRepresentationSerializer
    search_fields = ("name",)
