from django.utils.translation import gettext_lazy as _

from wbcore.contrib.icons import WBIcon
from wbcore.enums import RequestType
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.buttons.enums import ButtonDefaultColor
from wbcore.metadata.configs.buttons.view_config import ButtonViewConfig
from wbcore.metadata.configs.display.instance_display import create_simple_display

from ...serializers import ChangePasswordSerializer


class UserProfileButtonConfig(ButtonViewConfig):
    CUSTOM_INSTANCE_BUTTONS = {
        bt.WidgetButton(label=_("See Profile"), icon=WBIcon.PERSON.icon, key="see_profile"),
        bt.ActionButton(
            method=RequestType.PATCH,
            identifiers=("authentication:userprofile",),
            action_label=_("Resetting Settings"),
            key="reset_settings",
            description_fields=_("<p>This will reset all widgets on all pages.</p>"),
            icon=WBIcon.UNDO.icon,
            title=_("Reset Settings"),
            label=_("Reset Settings"),
        ),
        bt.ActionButton(
            method=RequestType.PATCH,
            identifiers=("authentication:userprofile",),
            action_label=_("Changing Password"),
            key="change_password",
            description_fields=_("<p>Change Password</p>"),
            serializer=ChangePasswordSerializer,
            icon=WBIcon.EDIT.icon,
            title=_("Change Password"),
            label=_("Change Password"),
            instance_display=create_simple_display([["old_password"], ["new_password"], ["confirm_password"]]),
        ),
    }


class UserModelButtonConfig(ButtonViewConfig):
    CUSTOM_INSTANCE_BUTTONS = CUSTOM_LIST_INSTANCE_BUTTONS = {
        bt.ActionButton(
            method=RequestType.GET,
            identifiers=("authentication:user",),
            action_label=_("Resetting Password"),
            key="reset_password",
            description_fields=_("<p>Reset Password</p>"),
            icon=WBIcon.REGENERATE.icon,
            color=ButtonDefaultColor.WARNING,
            title=_("Reset Password"),
            label=_("Reset Password"),
        ),
        bt.WidgetButton(key="user_activity_chart", label=_("User Activity"), icon=WBIcon.CHART_BARS_HORIZONTAL.icon),
        bt.WidgetButton(key="profile", label=_("Profile"), icon=WBIcon.PERSON.icon),
    }
