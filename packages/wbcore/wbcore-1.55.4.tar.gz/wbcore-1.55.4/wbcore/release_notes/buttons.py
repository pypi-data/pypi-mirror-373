from django.utils.translation import gettext as _
from rest_framework.reverse import reverse

from wbcore.contrib.icons import WBIcon
from wbcore.enums import RequestType
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.buttons.view_config import ButtonViewConfig


class ReleaseNotesButtonConfig(ButtonViewConfig):
    def get_custom_buttons(self):
        if not self.view.kwargs.get("pk", None):
            return {
                bt.ActionButton(
                    method=RequestType.PATCH,
                    action_label=_("Reading all release notes"),
                    endpoint=reverse("wbcore:releasenote-mark-all-as-read", request=self.request),
                    description_fields=_("Do you want to mark all release notes as read?"),
                    label=_("Mark all as read"),
                    icon=WBIcon.VIEW.icon,
                    confirm_config=bt.ButtonConfig(label=_("Read all")),
                    cancel_config=bt.ButtonConfig(label=_("Cancel")),
                    identifiers=("wbcore:releasenote",),
                ),
            }
        return dict()
