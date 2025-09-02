from wbcore import serializers
from wbcore.contrib.i18n.serializers.fields import TranslationJSONField


class ModelTranslateSerializerMixin(serializers.ModelSerializer):
    _i18n = TranslationJSONField(source="i18n")

    def update(self, instance, validated_data):
        i18n_data = validated_data.pop("i18n", {}) or {}
        if instance.i18n is None:
            instance.i18n = {}
        instance.i18n.update(i18n_data)
        return super().update(instance, validated_data)
