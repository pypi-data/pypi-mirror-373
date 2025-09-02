from rest_framework.reverse import reverse

from wbcore.metadata.configs.endpoints import EndpointViewConfig


class DocumentModelRelationshipEndpointConfig(EndpointViewConfig):
    def get_create_endpoint(self, **kwargs):
        if document_id := self.view.kwargs.get("document_id", None):
            return reverse(
                "wbcore:documents:document-documentmodelrelationship-list",
                args=[document_id],
                request=self.request,
            )
        return super().get_create_endpoint(**kwargs)
