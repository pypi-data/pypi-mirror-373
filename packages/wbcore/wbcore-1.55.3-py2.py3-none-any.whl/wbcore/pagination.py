from typing import TYPE_CHECKING, Callable

from rest_framework import pagination

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from rest_framework.request import Request
    from rest_framework.views import View


class EndlessPaginationMixin(pagination.BasePagination):
    """Custom pagination mixin to support disabling pagination through a query parameter."""

    def paginate_queryset(self, queryset: "QuerySet", request: "Request", view: "View | None" = None):
        """
        Paginate the queryset if pagination is not explicitly disabled.

        Args:
            queryset (QuerySet): The queryset to paginate.
            request (Request): The request object.
            view (View, optional): The view calling this method.

        Returns:
            QuerySet: The paginated queryset or None if pagination is disabled.
        """
        if request.query_params.get("disable_pagination") == "true":
            return None
        return super().paginate_queryset(queryset, request, view)


class InitialPaginationMixin:
    """Mixin to determine whether the current page is the initial page."""

    get_previous_link: Callable[[], str | None]

    def is_initial(self) -> bool:
        """
        Determine if the current page is the initial page.

        Returns:
            bool: True if it's the initial page, False otherwise.
        """
        return self.get_previous_link() is None


class CursorPagination(EndlessPaginationMixin, InitialPaginationMixin, pagination.CursorPagination):
    def _get_position_from_instance(self, instance, ordering) -> str:
        """
        Returns the super _get_position_from_instance but adjusts the first item of ordering
        to ensure that no foreignkey is included to not break the frontend.

        Args:
            instance: The instance to get the position from.
            ordering (list): The ordering criteria.

        Returns:
            Any: The position from the instance.
        """
        new_ordering = [*ordering]
        new_ordering[0] = new_ordering[0].split("__")[0]
        return super()._get_position_from_instance(instance, new_ordering)


class LimitOffsetPagination(EndlessPaginationMixin, InitialPaginationMixin, pagination.LimitOffsetPagination): ...
