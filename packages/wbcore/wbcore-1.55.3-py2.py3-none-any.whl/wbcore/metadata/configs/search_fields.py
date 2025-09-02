from .base import WBCoreViewConfig


class SearchFieldsViewConfig(WBCoreViewConfig):
    metadata_key = "search_fields"
    config_class_attribute = "search_fields_config_class"

    def get_metadata(self) -> list[str]:
        return getattr(self.view, "search_fields", [])
