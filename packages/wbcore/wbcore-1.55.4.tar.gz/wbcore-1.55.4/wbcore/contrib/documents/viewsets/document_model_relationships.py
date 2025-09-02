from wbcore import viewsets
from wbcore.contrib.documents.models import DocumentModelRelationship
from wbcore.contrib.documents.serializers import (
    DocumentModelRelationshipModelSerializer,
)
from wbcore.contrib.documents.viewsets.display import (
    DocumentModelRelationshipViewConfig,
)
from wbcore.contrib.documents.viewsets.endpoints.documents_model_relationships import (
    DocumentModelRelationshipEndpointConfig,
)


class DocumentModelRelationshipModelViewSet(viewsets.ModelViewSet):
    queryset = DocumentModelRelationship.objects.all()
    serializer_class = DocumentModelRelationshipModelSerializer
    display_config_class = DocumentModelRelationshipViewConfig
    endpoint_config_class = DocumentModelRelationshipEndpointConfig

    def get_queryset(self):
        queryset = super().get_queryset()
        if document_id := self.kwargs.get("document_id", None):
            queryset = queryset.filter(document_id=document_id)

        return queryset
