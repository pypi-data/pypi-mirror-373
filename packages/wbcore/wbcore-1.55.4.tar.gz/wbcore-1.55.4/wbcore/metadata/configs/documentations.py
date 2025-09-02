from .base import WBCoreViewConfig


class DocumentationViewConfig(WBCoreViewConfig):
    metadata_key = "documentation"
    config_class_attribute = "documentation_config_class"

    def get_metadata(self) -> str | None:
        if url := self.view._get_documentation_url(self.instance):  # type: ignore
            return url
        return None
