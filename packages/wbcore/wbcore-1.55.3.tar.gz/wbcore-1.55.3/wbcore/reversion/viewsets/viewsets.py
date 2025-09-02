from django.db.models import F
from django.shortcuts import get_object_or_404, render
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from reversion.models import Revision, Version
from reversion_compare.mixins import CompareMixin

from wbcore import viewsets

from ..filters import RevisionFilterSet, VersionFilterSet
from ..serializers import (
    RevisionModelSerializer,
    RevisionRepresentationSerializer,
    VersionModelSerializer,
    VersionRepresentationSerializer,
)
from .buttons import VersionButtonConfig
from .displays import RevisionDisplayConfig, VersionDisplayConfig
from .endpoints import (
    RevisionEndpointConfig,
    VersionEndpointConfig,
    VersionRevisionEndpointConfig,
)
from .titles import VersionTitleConfig


class VersionRepresentationViewSet(viewsets.RepresentationViewSet):
    ordering_fields = ordering = ("id",)
    # search_fields = ('user',)
    serializer_class = VersionRepresentationSerializer
    queryset = Version.objects.select_related("revision")
    filterset_class = VersionFilterSet


class RevisionRepresentationViewSet(viewsets.RepresentationViewSet):
    ordering_fields = ordering = ("id",)
    search_fields = ("user",)
    serializer_class = RevisionRepresentationSerializer
    queryset = Revision.objects.all()


class RevisionModelViewSet(viewsets.ModelViewSet):
    display_config_class = RevisionDisplayConfig
    endpoint_config_class = RevisionEndpointConfig

    queryset = Revision.objects.select_related("user")
    serializer_class = RevisionModelSerializer

    ordering = "-date_created"
    ordering_fields = ("id", "date_created")
    filterset_class = RevisionFilterSet


class VersionModelViewSet(CompareMixin, viewsets.ModelViewSet):
    display_config_class = VersionDisplayConfig
    endpoint_config_class = VersionEndpointConfig
    title_config_class = VersionTitleConfig
    button_config_class = VersionButtonConfig
    queryset = Version.objects.select_related("revision")
    serializer_class = VersionModelSerializer
    filterset_class = VersionFilterSet

    ordering_fields = ("date_created",)
    ordering = ("-date_created",)

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(
                date_created=F("revision__date_created"), profile_repr=F("revision__user__profile__computed_str")
            )
        )

    @action(detail=True, methods=["GET"], permission_classes=[IsAuthenticated])
    def revert(self, request, pk=None):
        if request.user.is_superuser or request.user.has_perm("reversion.change_version"):
            version1 = get_object_or_404(Version, pk=pk)
            version1.revert()
        return Response({}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["GET"], permission_classes=[IsAuthenticated])
    def comparewith(self, request, pk=None):
        if compare_with := request.GET.get("compare_with", None):
            version1 = get_object_or_404(Version, pk=pk)
            version2 = get_object_or_404(Version, pk=compare_with)
            if version1.id > version2.id:
                # Compare always the newest one (#2) with the older one (#1)
                version1, version2 = version2, version1

            obj = version1.content_type.model_class().objects.get(id=version1.object_id)
            compare_data, has_unfollowed_fields = self.compare(obj, version1, version2)
            return render(
                request,
                "reversion/compare_detail.html",
                {
                    "compare_data": compare_data,
                    "has_unfollowed_fields": has_unfollowed_fields,
                    "version1": version1,
                    "version2": version2,
                },
            )
        return Response({}, status=status.HTTP_400_BAD_REQUEST)


class VersionRevisionModelViewSet(VersionModelViewSet):
    endpoint_config_class = VersionRevisionEndpointConfig

    def get_queryset(self):
        return super().get_queryset().filter(revision=self.kwargs["revision_id"])
