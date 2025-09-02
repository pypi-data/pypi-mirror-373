from .base import WBCoreViewConfig


class IdentifierViewConfig(WBCoreViewConfig):
    metadata_key = "identifier"
    config_class_attribute = "identifier_config_class"

    # TODO: This does not yet work on the frontend, but should
    def get_metadata(self) -> str | None:
        if (get_identifier := getattr(self.view, "get_identifier", None)) and callable(get_identifier):
            return self.view.get_identifier(self.request)
        elif identifier := getattr(self.view, "IDENTIFIER", None):
            return identifier

        content_type = self.view.get_content_type()  # type: ignore
        identifier = f"{content_type.app_label}:{content_type.model}"

        return identifier


class DependantIdentifierViewConfig(WBCoreViewConfig):
    metadata_key = "dependant_identifier"
    config_class_attribute = "dependant_identifier_config_class"

    # TODO: This should return a list, shouldn't it?
    def get_metadata(self) -> str | None:
        return getattr(self.view, "DEPENDANT_IDENTIFIER", None)
