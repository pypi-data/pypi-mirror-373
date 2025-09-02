from typing import TYPE_CHECKING

from django.utils.functional import cached_property
from rest_framework import serializers

if TYPE_CHECKING:
    from wbcore.contrib.authentication.models import User
    from wbcore.contrib.directory.models import Person


class UserProfileMixin(serializers.Serializer):
    @cached_property
    def user(self) -> "User | None":
        """Returns the user associated with the request."""
        if request := self.context.get("request", None):
            return request.user
        return None

    @cached_property
    def profile(self) -> "Person | None":
        """Returns the profile of the user associated with the request."""
        if user := self.user:
            return user.profile
        return None
