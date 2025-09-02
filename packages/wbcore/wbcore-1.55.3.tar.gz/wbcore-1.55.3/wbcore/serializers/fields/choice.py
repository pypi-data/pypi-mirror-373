from rest_framework import serializers

from .list import ListFieldMixin
from .mixins import WBCoreSerializerFieldMixin
from .types import WBCoreType


class ChoiceMixin:
    choices: dict[str, str]

    def __init__(self, *args, group_key_mapping: dict[str, str] | None = None, **kwargs):
        """

        Args:
            group_key_mapping (dict[str, str] | None, optional): An optional mapping that provides
                a group for every choice value to group the choices in the drop down by. Defaults to None.
        """
        self.group_key_mapping = group_key_mapping or dict()
        super().__init__(*args, **kwargs)

    def _get_choices_representation(self):
        return [
            {"group": self.group_key_mapping.get(value), "value": value, "label": label}
            for value, label in self.choices.items()
        ]


class ChoiceField(WBCoreSerializerFieldMixin, ChoiceMixin, serializers.ChoiceField):
    field_type = WBCoreType.SELECT.value

    def get_representation(self, request, field_name) -> tuple[str, dict]:
        key, representation = super().get_representation(request, field_name)
        representation["choices"] = self._get_choices_representation()
        return key, representation


class MultipleChoiceField(ListFieldMixin, WBCoreSerializerFieldMixin, ChoiceMixin, serializers.MultipleChoiceField):
    field_type = WBCoreType.SELECT.value

    def get_representation(self, request, field_name) -> tuple[str, dict]:
        key, representation = super().get_representation(request, field_name)
        representation["multiple"] = True
        representation["choices"] = self._get_choices_representation()
        return key, representation

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        if isinstance(data, set):
            data = list(data)
        return data

    def to_representation(self, data):
        data = super().to_representation(data)
        if isinstance(data, set):
            data = list(data)
        return data


class LanguageChoiceField(ChoiceField):
    field_type = WBCoreType.LANGUAGE.value
