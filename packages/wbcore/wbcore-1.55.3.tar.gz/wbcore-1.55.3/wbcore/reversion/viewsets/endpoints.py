from rest_framework.reverse import reverse

from wbcore.metadata.configs.endpoints import EndpointViewConfig


class RevisionEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse("wbcore:revision-list", request=self.request)

    def get_create_endpoint(self, **kwargs):
        return None

    def get_delete_endpoint(self, **kwargs):
        return None


class VersionEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse("wbcore:version-list", request=self.request)

    def get_create_endpoint(self, **kwargs):
        return None

    def get_delete_endpoint(self, **kwargs):
        return None


class VersionRevisionEndpointConfig(VersionEndpointConfig):
    def get_endpoint(self, **kwargs):
        return reverse("wbcore:revision-version-list", args=[self.view.kwargs["revision_id"]], request=self.request)
