from django.utils.translation import gettext as _

from wbcore.contrib.icons import WBIcon
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
)
from wbcore.metadata.configs.preview import PreviewViewConfig


class AddressPreviewConfig(PreviewViewConfig):
    def get_display(self) -> Display:
        return create_simple_display([["street", "zip", "geography_city"]])

    def get_buttons(self):
        return [
            bt.WidgetButton(key="addresses", icon=WBIcon.LOCATION.icon, label=_("Show all addresses")),
        ]
