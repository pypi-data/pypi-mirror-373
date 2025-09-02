from django.db.models import Count

from wbcore import viewsets
from wbcore.contrib.documents.filters import DocumentTypeFilter
from wbcore.contrib.documents.models import DocumentType
from wbcore.contrib.documents.serializers import (
    DocumentTypeModelSerializer,
    DocumentTypeRepresentationSerializer,
)
from wbcore.contrib.documents.viewsets.buttons import DocumentTypeButtonConfig
from wbcore.contrib.documents.viewsets.display import DocumentTypeModelDisplay
from wbcore.contrib.documents.viewsets.titles import DocumentTypeModelTitleConfig


class DocumentTypeModelViewSet(viewsets.ModelViewSet):
    LIST_DOCUMENTATION = "documents/markdown/documentation/document_types.md"
    search_fields = ("name",)
    ordering = ["name"]
    ordering_fields = (
        "name",
        "parent",
    )
    filterset_class = DocumentTypeFilter
    queryset = DocumentType.objects.all()
    serializer_class = DocumentTypeModelSerializer
    title_config_class = DocumentTypeModelTitleConfig

    button_config_class = DocumentTypeButtonConfig
    display_config_class = DocumentTypeModelDisplay

    def get_queryset(self):
        return super().get_queryset().annotate(document_count=Count("documents"))


class DocumentTypeRepresentationViewSet(viewsets.RepresentationViewSet):
    queryset = DocumentType.objects.all()
    serializer_class = DocumentTypeRepresentationSerializer
    search_fields = ("name",)
