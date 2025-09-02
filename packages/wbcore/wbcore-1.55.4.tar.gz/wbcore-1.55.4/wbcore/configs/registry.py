from contextlib import suppress
from importlib import import_module
from inspect import getmembers
from types import ModuleType
from typing import Any, Iterable

from django.conf import settings
from rest_framework.request import Request


class ConfigRegistry:
    """
    A class that is able to discover all functions that are wrapped in the `@register_config` decorator. This registry
    should never be used from the outside and its sole purpose is to gather all functions, so they are returned
    in the APIView of this module.
    """

    def __init__(self, request: Request, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

    def discover_configs(self) -> Iterable[ModuleType]:
        for app in settings.INSTALLED_APPS:
            with suppress(ModuleNotFoundError):
                module = import_module(f"{app}.configs")
                yield module

    def get_configs(self) -> Iterable[tuple[str, Any]]:
        for module in self.discover_configs():
            for member in getmembers(module, lambda member: hasattr(member, "_is_config")):
                if res := member[1](request=self.request):
                    yield res

    def get_config_dict(self) -> dict[str, Any]:
        return dict(self.get_configs())
