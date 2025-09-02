from rest_framework.reverse import reverse

from wbcore.metadata.configs.endpoints import EndpointViewConfig


class UserPermissionsModelEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbcore:authentication:user-permissions-list", args=[self.view.kwargs["user_id"]], request=self.request
        )


class UserProfileModelEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return None

    def get_instance_endpoint(self, **kwargs):
        return reverse("wbcore:authentication:userprofile-list", args=[], request=self.request)
