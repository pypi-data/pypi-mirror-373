from django.conf import settings

from wbcore.serializers.fields import JSONField


class TranslationJSONField(JSONField):
    field_type = "translation_field"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.read_only = False
        self.required = False
        self.allow_null = True

    def get_representation(self, request, field_name) -> tuple[str, dict]:
        key, representation = super().get_representation(request, field_name)
        representation["default_language"] = settings.LANGUAGE_CODE
        representation["languages"] = settings.MODELTRANS_AVAILABLE_LANGUAGES
        representation["fields"] = self.parent.Meta.model._meta.get_field("i18n").fields
        return key, representation
