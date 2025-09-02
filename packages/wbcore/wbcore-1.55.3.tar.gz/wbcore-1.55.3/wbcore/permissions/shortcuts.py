from django.contrib.auth.models import Group
from django.db.models.query import QuerySet

from wbcore.contrib.authentication.models.users import User


def get_internal_groups() -> QuerySet[Group]:
    from wbcore.permissions.registry import user_registry

    """
    Return the cached groups of internals users

    Returns:
        A queryset of group corresponding to the internal notion defined by the set UserBackend

    Raises:
        ValueError: If user backend path does not correspond to a valid module
    """
    return user_registry.internal_groups


def get_internal_users() -> QuerySet[User]:
    from wbcore.permissions.registry import user_registry

    """
    Return the cached queryset of internals users

    Returns:
        A queryset of user corresponding to the internal notion defined by the set UserBackend

    Raises:
        ValueError: If user backend path does not correspond to a valid module
    """
    return user_registry.internal_users


def is_internal_user(user: User, include_superuser: bool = False) -> bool:
    return user and (user.is_internal or (include_superuser and user.is_superuser))
