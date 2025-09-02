from wbcore import viewsets
from wbcore.contrib.example_app.filters import RoleFilter
from wbcore.contrib.example_app.models import Role
from wbcore.contrib.example_app.serializers import (
    RoleModelSerializer,
    RoleRepresentationSerializer,
)
from wbcore.contrib.example_app.viewsets.displays import RoleDisplayConfig
from wbcore.contrib.example_app.viewsets.titles import RoleTitleConfig


class RoleModelViewSet(viewsets.ModelViewSet):
    display_config_class = RoleDisplayConfig
    queryset = Role.objects.all()
    serializer_class = RoleModelSerializer
    title_config_class = RoleTitleConfig
    ordering_fields = ordering = ("title",)
    filterset_class = RoleFilter
    search_fields = ("title",)


class RoleRepresentationViewSet(viewsets.RepresentationViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleRepresentationSerializer
    search_fields = ("title",)
