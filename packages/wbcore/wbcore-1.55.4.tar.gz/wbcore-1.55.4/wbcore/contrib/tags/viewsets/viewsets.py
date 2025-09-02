from wbcore import viewsets

from ..filters import TagFilterSet
from ..models import Tag, TagGroup
from ..serializers import (
    TagGroupModelSerializer,
    TagGroupRepresentationSerializer,
    TagModelSerializer,
    TagRepresentationSerializer,
)
from .display import TagDisplayConfig, TagGroupDisplayConfig, TagPreviewConfig


class TagGroupRepresentationViewSet(viewsets.RepresentationViewSet):
    queryset = TagGroup.objects.all()
    serializer_class = TagGroupRepresentationSerializer

    search_fields = ["title"]


class TagGroupModelViewSet(viewsets.ModelViewSet):
    queryset = TagGroup.objects.all()
    serializer_class = TagGroupModelSerializer

    filterset_fields = {"title": ["icontains", "exact"]}
    search_fields = ["title"]

    display_config_class = TagGroupDisplayConfig


class TagRepresentationViewSet(viewsets.RepresentationViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagRepresentationSerializer
    filterset_class = TagFilterSet

    search_fields = ["title", "slug", "groups__title"]


class TagModelViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagModelSerializer

    filterset_class = TagFilterSet
    search_fields = ("title", "description")
    ordering_fields = [
        "title",
        "color",
        "slug",
        "content_type",
    ]
    ordering = ["title"]
    display_config_class = TagDisplayConfig
    preview_config_class = TagPreviewConfig


class TagTagGroupModelViewSet(TagModelViewSet):
    def get_queryset(self):
        return super().get_queryset().filter(groups=self.kwargs["group_id"])
