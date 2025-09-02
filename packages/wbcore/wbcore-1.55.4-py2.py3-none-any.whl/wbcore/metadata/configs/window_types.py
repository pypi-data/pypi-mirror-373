from wbcore.enums import WidgetType  # TODO: Rename to WindowType

from .base import WBCoreViewConfig


class WindowTypeViewConfig(WBCoreViewConfig):
    metadata_key = "type"
    config_class_attribute = "window_type_config_class"

    def get_metadata(self) -> str:
        if window_type := getattr(self.view, "WIDGET_TYPE", None):
            return window_type
        return WidgetType.INSTANCE.value if self.instance else WidgetType.LIST.value
