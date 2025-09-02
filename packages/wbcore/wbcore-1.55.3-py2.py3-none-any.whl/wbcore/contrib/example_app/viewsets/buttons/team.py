from django.utils.translation import gettext as _

from wbcore.contrib.icons import WBIcon
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.buttons.view_config import ButtonViewConfig


class TeamButtonConfig(ButtonViewConfig):
    def get_custom_instance_buttons(self) -> set:
        return {
            bt.DropDownButton(
                label=_("Website & Coach"),
                icon=WBIcon.UNFOLD.icon,
                buttons=(
                    bt.HyperlinkButton(key="website", label=_("Homepage"), icon=WBIcon.LINK.icon, weight=1),
                    bt.WidgetButton(
                        label=_("Coach"),
                        icon=WBIcon.PERSON.icon,
                        key="coach",
                        weight=2,
                    ),
                ),
            )
        }
