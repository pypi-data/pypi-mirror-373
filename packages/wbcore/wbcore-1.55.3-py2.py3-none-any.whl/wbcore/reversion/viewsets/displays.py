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


class RevisionDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="date_created", label=_("Created At")),
                dp.Field(key="user", label=_("User")),
            ]
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [["date_created", "user"], [repeat_field(2, "versions_section")]],
            [create_simple_section("versions_section", _("Versions"), [["versions"]], "versions", collapsed=False)],
        )


class VersionDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="id", label=_("ID")),
                dp.Field(key="revision", label=_("Revision")),
                dp.Field(key="date_created", label=_("Creation Date")),
                # dp.Field(key="object_repr", label=_("Object repr")),
            ]
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [["revision", "date_created"], ["object_repr", "object_id"], [repeat_field(2, "serialized_data")]]
        )
