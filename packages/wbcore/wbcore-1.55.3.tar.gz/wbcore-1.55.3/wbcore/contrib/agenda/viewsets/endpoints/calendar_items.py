from django.conf import settings
from rest_framework.reverse import reverse

from wbcore.metadata.configs.endpoints import EndpointViewConfig


class CalendarItemEndpointConfig(EndpointViewConfig):
    def _get_instance_endpoint(self, **kwargs):
        return "{{endpoint}}"

    def get_create_endpoint(self, **kwargs):
        return f"{reverse(settings.DEFAULT_CREATE_ENDPOINT_BASENAME, args=[], request=self.request)}?participants={self.request.user.profile.id}&new_mode=True"

    def get_delete_endpoint(self, **kwargs):
        try:
            if self.view.get_object().can_delete(self.request.user):
                return super().get_delete_endpoint(**kwargs)
        except (AssertionError, AttributeError, KeyError):
            return None
