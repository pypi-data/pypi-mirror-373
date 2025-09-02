from .base import WBCoreViewConfig


class OrderingFieldsViewConfig(WBCoreViewConfig):
    metadata_key = "ordering_fields"
    config_class_attribute = "ordering_fields_config_class"

    def get_metadata(self) -> dict[str, str]:
        ordering_fields = dict()

        for ordering_field in self.view.get_ordering_fields():
            field_name = ordering_field.replace("__nulls_last", "").replace("__nulls_first", "")

            # TODO: Potentially refactor
            serializer = None
            if serializer_method := getattr(self.view, "get_serializer", None):
                serializer = serializer_method()

            if "__" in ordering_field and (not serializer or field_name not in serializer.fields.keys()):
                field_name = field_name.split("__")[0]

            ordering_fields[field_name] = ordering_field

        return ordering_fields
