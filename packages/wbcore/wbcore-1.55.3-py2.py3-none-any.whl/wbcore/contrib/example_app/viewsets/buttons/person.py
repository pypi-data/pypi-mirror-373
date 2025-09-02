from django.utils.translation import gettext as _
from rest_framework.reverse import reverse

from wbcore.contrib.icons import WBIcon
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.buttons.view_config import ButtonViewConfig


class PlayerButtonConfig(ButtonViewConfig):
    def get_custom_instance_buttons(self) -> set:
        if player_id := self.view.kwargs.get("pk"):
            return {
                bt.WidgetButton(
                    label=_("Statistics"),
                    icon=WBIcon.TABLE.icon,
                    endpoint=reverse("example_app:player-statistics-list", args=[player_id], request=self.request),
                ),
            }
        return set()
