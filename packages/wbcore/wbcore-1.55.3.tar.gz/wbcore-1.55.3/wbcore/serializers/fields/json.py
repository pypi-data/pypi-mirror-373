from rest_framework import serializers
from rest_framework.reverse import reverse

from .mixins import WBCoreSerializerFieldMixin
from .types import ReturnContentType, WBCoreType


class AbstractJSONField(serializers.JSONField):
    def __init__(self, serializer_class=None, flatten_field_names=None, *args, **kwargs):
        self.serializer_class = serializer_class
        if isinstance(flatten_field_names, list):
            self.flatten_field_names = flatten_field_names
        super().__init__(*args, **kwargs)


class JSONField(WBCoreSerializerFieldMixin, AbstractJSONField):
    field_type = WBCoreType.JSON.value


class JSONTableField(WBCoreSerializerFieldMixin, AbstractJSONField):
    field_type = WBCoreType.JSONTABLE.value


class JSONTextEditorField(WBCoreSerializerFieldMixin, serializers.JSONField):
    field_type = WBCoreType.TEXTEDITOR.value
    texteditor_content_type = ReturnContentType.JSON.value

    def get_representation(self, request, field_name) -> tuple[str, dict]:
        key, representation = super().get_representation(request, field_name)
        representation["content_type"] = self.texteditor_content_type
        return key, representation


class TemplatedJSONTextEditor(WBCoreSerializerFieldMixin, serializers.JSONField):
    field_type = WBCoreType.TEMPLATED_TEXTEDITOR.value

    def __init__(self, templates, default_editor_config=None, *args, **kwargs):
        self.templates = templates
        self.default_editor_config = default_editor_config
        super().__init__(*args, **kwargs)

    def get_representation(self, request, field_name) -> tuple[str, dict]:
        key, representation = super().get_representation(request, field_name)

        if callable(self.templates):
            representation["template_url"] = self.templates(request)
        else:
            representation["template_url"] = reverse(self.templates, request=request)

        if self.default_editor_config:
            if callable(self.default_editor_config):
                representation["default_editor_config"] = self.default_editor_config(request)
            else:
                representation["default_editor_config"] = self.default_editor_config

        return key, representation
