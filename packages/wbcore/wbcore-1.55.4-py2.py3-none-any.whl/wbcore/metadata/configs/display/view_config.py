from contextlib import suppress

from django.utils.text import slugify
from rest_framework.request import Request
from rest_framework.views import View

from wbcore.metadata.configs.display.instance_display.display import Display
from wbcore.metadata.configs.display.list_display import ListDisplay
from wbcore.metadata.configs.display.windows import Window

from ..base import WBCoreViewConfig
from .models import AppliedPreset


class DisplayViewConfig(WBCoreViewConfig):
    metadata_key = "display"
    config_class_attribute = "display_config_class"

    def __init__(self, view: View, request: Request, instance: bool | None = None):
        self.tooltip = request.GET.get("tooltip", None) == "true"
        self.inline = request.GET.get("inline", None) == "true"
        super().__init__(view, request, instance)

    def get_window(self) -> Window | None:
        return None

    def get_instance_display(self) -> Display | None:
        return None

    def get_list_display(self) -> ListDisplay | None:
        return None

    def get_preview_display(self) -> Display | None:
        return None

    def get_metadata(self) -> dict:
        display = dict()
        instance_display = self.get_instance_display()
        if isinstance(instance_display, Display):
            display["instance"] = instance_display.serialize(view_config=self, view=self.view, request=self.request)
        elif instance_display:
            display["instance"] = list(instance_display)
        else:
            display["instance"] = Display(pages=[]).serialize()

        if not self.instance:
            list_display = self.get_list_display()
            if isinstance(list_display, Display):
                display["list"] = list_display.serialize()
            else:
                display["list"] = dict(list_display or {})

        if window := self.get_window():
            display["window"] = window.serialize()

        display_identifier_path = self.view.display_identifier_config_class(
            self.view, self.request, self.instance
        ).display_identifier_path()

        with suppress(AppliedPreset.DoesNotExist):
            display["preset"] = AppliedPreset.objects.get(
                user=self.request.user, display_identifier_path=display_identifier_path
            ).display

        return display


class DisplayIdentifierViewConfig(WBCoreViewConfig):
    metadata_key = "display_identifier"
    config_class_attribute = "display_identifier_config_class"

    def display_identifier_path(self) -> str:
        display = self.view.display_config_class
        slugified_display_module = slugify(display.__module__.replace(".", "-"))
        slugified_display_class = slugify(display.__name__)
        display_identifier_path = f"{slugified_display_module}-{slugified_display_class}"

        # We get the path from the header (if it exists, only for nested tables inside forms) and then join it
        # with the current display identifier. If there is an applied preset for this user - we return it.
        if inline_path := self.request.META.get("HTTP_WB_DISPLAY_IDENTIFIER", None):
            display_identifier_path = f"{inline_path}.{display_identifier_path}"
        return display_identifier_path

    def get_metadata(self):
        return self.display_identifier_path()
