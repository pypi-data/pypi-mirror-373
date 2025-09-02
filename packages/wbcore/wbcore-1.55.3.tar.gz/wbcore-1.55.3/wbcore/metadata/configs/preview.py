from wbcore.metadata.configs.display.instance_display.shortcuts import Display

from .base import WBCoreViewConfig


class PreviewViewConfig(WBCoreViewConfig):
    metadata_key = "preview"
    config_class_attribute = "preview_config_class"

    DISPLAY_TYPE = "instance_display"

    def get_buttons(self):
        return []

    def _get_buttons(self):
        return [dict(button) for button in self.get_buttons()]

    def get_display(self) -> Display | None:
        return None

    def _get_display(self):
        if display := self.get_display():
            if self.DISPLAY_TYPE == "instance_display":
                return display.serialize()
            return display
        return None

    def _get_display_type(self):
        return self.DISPLAY_TYPE

    def get_metadata(self) -> dict:
        buttons = self._get_buttons()
        display = self._get_display()

        preview = dict()
        if len(buttons) > 0 or display is not None:
            preview["buttons"] = buttons
            preview["display"] = display
            preview["type"] = self._get_display_type()

        return preview
