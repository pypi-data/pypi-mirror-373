from typing import Any, Iterable

from rest_framework import serializers

from .mixins import WBCoreSerializerFieldMixin
from .types import WBCoreType


class BooleanField(WBCoreSerializerFieldMixin, serializers.BooleanField):
    field_type = WBCoreType.BOOLEAN.value

    def __init__(
        self,
        labels: Iterable[str] | None = None,
        values: Iterable[Any] | None = None,
        background_color: str | Iterable[str] | None = None,
        color: str | Iterable[str] | None = None,
        active_background_color: str | Iterable[str] | None = None,
        active_color: str | Iterable[str] | None = None,
        **kwargs,
    ):
        self.labels = labels
        self.values = values
        self.background_color = background_color
        self.color = color
        self.active_background_color = active_background_color
        self.active_color = active_color
        super().__init__(**kwargs)

    def get_representation(self, request, field_name) -> tuple[str, dict]:
        field_name, representation = super().get_representation(request, field_name)

        if self.labels:
            representation["labels"] = self.labels

        if self.values:
            representation["values"] = self.values

        if self.background_color:
            representation["background_color"] = self.background_color

        if self.color:
            representation["color"] = self.color

        if self.active_background_color:
            representation["active_background_color"] = self.active_background_color

        if self.active_color:
            representation["active_color"] = self.active_color

        return field_name, representation
