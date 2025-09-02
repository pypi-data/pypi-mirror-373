from .base import WBCoreViewConfig


class PaginationViewConfig(WBCoreViewConfig):
    metadata_key = "pagination"
    config_class_attribute = "pagination_config_class"

    def get_metadata(self) -> str | None:
        if pagination := getattr(self.view, "pagination_class", None):
            return pagination.__name__[: -len("Pagination")].lower()
        return None
