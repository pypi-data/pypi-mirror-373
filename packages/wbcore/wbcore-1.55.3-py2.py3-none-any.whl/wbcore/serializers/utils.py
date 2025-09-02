from contextlib import suppress
from dataclasses import dataclass
from typing import TYPE_CHECKING

from django.shortcuts import get_object_or_404
from rest_framework.fields import get_attribute

from wbcore.utils.views import parse_query_parameters_list

if TYPE_CHECKING:
    from django.db.models import Model


@dataclass
class CurrentUserDefault:
    """
    Returns the profile of the current user when called.
    """

    user_attr: str = None
    requires_context: str = True
    as_list: bool = False

    def __call__(self, serializer_instance):
        attr = None
        if request := serializer_instance.context.get("request"):
            attr = request.user
            if self.user_attr:
                try:
                    attr = get_attribute(attr, self.user_attr.split("."))
                except AttributeError:
                    attr = None
        if self.as_list and attr:
            attr = [attr]
        return attr


class DefaultFromGET:
    """
    Extracts the informations from the get request depending of the query_name.
    """

    def __init__(self, query_name: str, many: bool = False):
        self.many = many
        self.query_name = query_name

    requires_context = True

    def __call__(self, serializer_instance):
        if request := serializer_instance.context.get("request", None):
            data = request.GET.get(self.query_name, "")
            parameters_list = parse_query_parameters_list(data)

            if (not parameters_list or not self.many) and data:
                return data
            elif parameters_list:
                return parameters_list
        return None


class DefaultFromKwargs:
    """
    Extracts the informations from the view kwargs depending of the query_name.
    """

    def __init__(self, query_name: str):
        self.query_name = query_name

    requires_context = True

    def __call__(self, serializer_instance):
        if (view := serializer_instance.view) and (item_id := view.kwargs.get(self.query_name, None)):
            return item_id
        return None


class DefaultFromView:
    """
    Extracts the informations from the view kwargs depending of the query_name.
    """

    def __init__(self, source: str):
        self.source = source

    requires_context = True

    def __call__(self, serializer_instance):
        if view := serializer_instance.view:
            with suppress(AttributeError):
                return get_attribute(view, self.source.split("."))
        return None


class DefaultFromGetOrKwargs:
    """
    Extracts the informations from the get request or the view kwargs depending of the query_name.
    """

    def __init__(self, query_name_get: str, query_name_kwargs: str, many: bool = False):
        self.defaults = [DefaultFromGET(query_name_get, many), DefaultFromKwargs(query_name_kwargs)]

    requires_context = True

    def __call__(self, serializer_instance):
        for default in self.defaults:
            if result := default(serializer_instance):
                return result

        return None


class DefaultAttributeFromRemoteField(DefaultFromKwargs):
    def __init__(self, query_name: str, model: type["Model"], source: str | None = None):
        self.source = source
        self.model = model
        super().__init__(query_name)

    def __call__(self, serializer_instance):
        if item_id := super().__call__(serializer_instance):
            instance = get_object_or_404(self.model, pk=item_id)
            if self.source:
                try:
                    instance = get_attribute(instance, self.source.split("."))
                except AttributeError:
                    instance = None
            return instance


class DefaultAttributeFromObject:
    requires_context = True

    def __init__(self, source: str | None = None):
        self.source = source

    def __call__(self, serializer_instance):
        if (view := serializer_instance.view) and "pk" in view.kwargs:
            instance = view.get_object()
            if self.source:
                try:
                    instance = get_attribute(instance, self.source.split("."))
                except AttributeError:
                    instance = None
            return instance
