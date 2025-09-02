from django.utils.translation import gettext as _

from wbcore.contrib.icons import WBIcon
from wbcore.enums import RequestType
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.buttons.view_config import ButtonViewConfig


class ShareableLinkModelButtonConfig(ButtonViewConfig):
    def get_custom_list_instance_buttons(self):
        return {
            bt.ActionButton(
                method=RequestType.PATCH,
                key="manually_invalidate",
                label=_("Invalidate"),
                icon=WBIcon.UNLINK.icon,
                description_fields=_("<p> Are you sure you want to invalidate this link? </p>"),
                title=_("Invalidate"),
                action_label=_("Invalidation"),
            )
        }
