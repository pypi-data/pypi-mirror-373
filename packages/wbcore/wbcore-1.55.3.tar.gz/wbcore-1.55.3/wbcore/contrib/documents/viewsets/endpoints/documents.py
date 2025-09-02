from rest_framework.reverse import reverse

from wbcore.metadata.configs.endpoints import EndpointViewConfig


class DocumentEndpointConfig(EndpointViewConfig):
    def get_create_endpoint(self, **kwargs):
        if "content_type" in self.view.kwargs and "content_id" in self.view.kwargs:
            return reverse(
                "wbcore:documents:document_content_object",
                args=[self.view.kwargs["content_type"], self.view.kwargs["content_id"]],
                request=self.request,
            )
        return super().get_create_endpoint(**kwargs)

    def get_delete_endpoint(self, **kwargs):
        if "pk" in self.view.kwargs:
            if self.view.get_object().system_created:
                return None
        return super().get_delete_endpoint(**kwargs)
