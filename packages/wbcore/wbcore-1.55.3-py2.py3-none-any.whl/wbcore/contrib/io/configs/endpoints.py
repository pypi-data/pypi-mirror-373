from rest_framework.reverse import reverse

from wbcore.metadata.configs.endpoints import EndpointViewConfig


class ImportSourceModelViewSetEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse("wbcore:io:importsource-list", args=[], request=self.request)


class SourceModelViewSetEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse("wbcore:io:source-list", args=[], request=self.request)
