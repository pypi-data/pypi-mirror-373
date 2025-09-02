from typing import Optional

from django.utils.translation import gettext as _

from wbcore.contrib.icons import WBIcon
from wbcore.enums import Unit
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
)
from wbcore.metadata.configs.display.instance_display.utils import repeat_field
from wbcore.metadata.configs.display.view_config import DisplayViewConfig


class ReleaseNoteDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="user_read_icon", label=" ", width=Unit.PIXEL(40)),
                dp.Field(key="module", label=_("Module")),
                dp.Field(key="version", label=_("Version")),
                dp.Field(key="release_date", label=_("Release Date")),
                dp.Field(key="summary", label=_("Summary")),
            ],
            legends=[
                dp.Legend(
                    key="read_unread",
                    items=[
                        dp.LegendItem(
                            icon=WBIcon.VIEW.icon,
                            label=_("Read"),
                            value="read",
                        ),
                        dp.LegendItem(
                            icon=WBIcon.IGNORE.icon,
                            label=_("Unread"),
                            value="unread",
                        ),
                    ],
                )
            ],
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                ["module", "version", "release_date"],
                [repeat_field(3, "summary")],
                [repeat_field(3, "notes")],
            ]
        )
