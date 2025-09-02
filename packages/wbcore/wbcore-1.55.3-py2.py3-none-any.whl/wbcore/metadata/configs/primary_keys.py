from .base import WBCoreViewConfig


class PrimaryKeyViewConfig(WBCoreViewConfig):
    metadata_key = "pk"
    config_class_attribute = "primary_key_config_class"

    def get_metadata(self) -> int | str | None:
        return self.view.kwargs.get("pk", None)
