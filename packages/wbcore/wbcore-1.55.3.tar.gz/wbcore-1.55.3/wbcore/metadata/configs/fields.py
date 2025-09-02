from collections import defaultdict

from .base import WBCoreViewConfig


class FieldsViewConfig(WBCoreViewConfig):
    metadata_key = "fields"
    config_class_attribute = "fields_config_class"

    def get_metadata(self) -> dict:
        fields = defaultdict(dict)
        if (serializer_class := getattr(self.view, "get_serializer", None)) and (serializer := serializer_class()):
            for field_name, field in serializer.fields.items():
                field_key, field_representation = field.get_representation(self.request, field_name)
                fields[field_key].update(field_representation)

        return fields
