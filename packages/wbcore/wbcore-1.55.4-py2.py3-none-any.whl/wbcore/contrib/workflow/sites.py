from dataclasses import dataclass, field
from typing import Callable

from django.utils.functional import cached_property
from django.utils.module_loading import autodiscover_modules, import_string


class CachedDict(dict):
    def __init__(self):
        super().__init__()
        self._cache = {}

    def __getitem__(self, key):
        if key in self._cache:
            return self._cache[key]
        value = super().get(key)
        self._cache[key] = import_string(value)
        return self._cache[key]


@dataclass
class WorkflowSite:
    registered_assignees_methods: dict[str, Callable] = field(default_factory=dict)
    registered_assignees_names: dict[str, str] = field(default_factory=dict)
    registered_model_classes_serializer_map: CachedDict = field(default_factory=CachedDict)

    @cached_property
    def assignees_choices(self) -> tuple[str, str]:
        autodiscover_modules("workflows")  # we have to do that because the filter choices loads at runtime
        return tuple(self.registered_assignees_names.items())

    @cached_property
    def assignees_methods(self) -> tuple[str, Callable]:
        return tuple(self.registered_assignees_methods.items())

    @cached_property
    def model_content_types(self):
        return [
            (model._meta.app_label, model.__name__) for model in self.registered_model_classes_serializer_map.keys()
        ]


workflow_site = WorkflowSite()
