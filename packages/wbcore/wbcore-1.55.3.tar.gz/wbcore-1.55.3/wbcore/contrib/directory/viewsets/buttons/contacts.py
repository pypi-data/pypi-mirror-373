from django.utils.translation import gettext as _

from wbcore.contrib.icons import WBIcon
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.buttons.view_config import ButtonViewConfig


class TelephoneContactButtonConfig(ButtonViewConfig):
    def get_custom_list_instance_buttons(self):
        return {
            bt.WidgetButton(
                key="new_call", label=_("Create New Call Activity"), new_mode=True, icon=WBIcon.PHONE_ADD.icon
            ),
        }

    def get_custom_instance_buttons(self):
        return self.get_custom_list_instance_buttons()
