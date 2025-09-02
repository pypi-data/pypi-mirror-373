from contextlib import suppress

from django.conf import settings
from django.contrib.auth.models import Group
from django.db.models import QuerySet
from django.utils.functional import cached_property

from wbcore.contrib.authentication.models import User
from wbcore.utils.importlib import import_from_dotted_path


class UserBackendRegistry:
    def __init__(self):
        internal_users_backend_path = getattr(settings, "USER_BACKEND", "wbcore.permissions.backend.UserBackend")
        internal_users_backend_class = import_from_dotted_path(internal_users_backend_path)
        self.backend = internal_users_backend_class()

    @cached_property
    def internal_groups(self) -> QuerySet[Group]:
        return self.backend.get_internal_groups().all()

    @cached_property
    def internal_users(self) -> QuerySet[User]:
        return self.backend.get_internal_users().all()

    def reset_cache(self):
        with suppress(AttributeError):
            del self.internal_users
        with suppress(AttributeError):
            del self.internal_groups


user_registry = UserBackendRegistry()
