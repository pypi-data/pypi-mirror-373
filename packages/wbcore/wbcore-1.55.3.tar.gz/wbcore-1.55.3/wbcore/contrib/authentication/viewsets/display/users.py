from typing import Optional

from django.utils.translation import gettext as _

from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
    create_simple_section,
)
from wbcore.metadata.configs.display.instance_display.utils import repeat_field
from wbcore.metadata.configs.display.view_config import DisplayViewConfig


class UserPermissionModelDisplay(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="name", label=_("Name")),
                dp.Field(key="codename", label=_("Code Name")),
                dp.Field(key="content_type_repr", label=_("Content Type")),
            ]
        )


class UserProfileModelDisplay(DisplayViewConfig):
    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                [repeat_field(3, "profile_image"), "prefix", "first_name", "last_name"],
                [repeat_field(3, "profile_image"), repeat_field(2, "email"), "birthday"],
                [repeat_field(3, "profile_image"), repeat_field(2, "profile"), "username"],
                [repeat_field(6, "token_section")],
            ],
            [
                create_simple_section(
                    "token_section",
                    _("Token (Sensitive information: handle with care)"),
                    [["generic_auth_token_key"], ["calendar_subscription_link"]],
                )
            ],
        )


class UserModelDisplay(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="email", label=_("Email")),
                dp.Field(key="is_active", label=_("Is Active")),
                dp.Field(key="date_joined", label=_("Joined")),
                dp.Field(key="last_connection", label=_("Latest Connection")),
            ]
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                ["username", "email"],
                [repeat_field(2, "profile")],
                [repeat_field(2, "is_active")],
                [repeat_field(2, "groups_section")],
                [repeat_field(2, "permissions_section")],
                [repeat_field(2, "user_activity_section")],
            ],
            [
                create_simple_section("groups_section", _("Groups"), [["groups"]], collapsed=True),
                create_simple_section("permissions_section", _("Permissions"), [["user_permissions"]], collapsed=True),
                create_simple_section(
                    "user_activity_section", _("User Activity"), [["user_activity"]], "user_activity", collapsed=True
                ),
            ],
        )
