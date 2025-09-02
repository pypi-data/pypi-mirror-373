from django.db.models import QuerySet

from wbcore import viewsets
from wbcore.contrib.example_app.filters import StadiumFilter
from wbcore.contrib.example_app.models import Stadium
from wbcore.contrib.example_app.serializers import (
    StadiumModelSerializer,
    StadiumRepresentationSerializer,
)
from wbcore.contrib.example_app.viewsets.displays import StadiumDisplayConfig
from wbcore.contrib.example_app.viewsets.titles import StadiumTitleConfig


class StadiumModelViewSet(viewsets.ModelViewSet):
    display_config_class = StadiumDisplayConfig
    queryset = Stadium.objects.all()
    search_fields = ("name", "city__representation")
    serializer_class = StadiumModelSerializer
    title_config_class = StadiumTitleConfig
    ordering_fields = ("name", "city__representation", "capacity")
    ordering = ("name", "city__representation")
    filterset_class = StadiumFilter

    def get_queryset(self) -> QuerySet[Stadium]:
        return super().get_queryset().select_related("city")


class StadiumRepresentationViewSet(viewsets.RepresentationViewSet):
    queryset = Stadium.objects.all()
    serializer_class = StadiumRepresentationSerializer
    search_fields = ("name",)
