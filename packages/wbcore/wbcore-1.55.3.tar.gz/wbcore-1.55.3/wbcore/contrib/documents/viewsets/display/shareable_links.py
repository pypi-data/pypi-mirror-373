from typing import Optional

from django.utils.translation import gettext as _

from wbcore.contrib.color.enums import WBColor
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
    create_simple_section,
)
from wbcore.metadata.configs.display.instance_display.utils import repeat_field
from wbcore.metadata.configs.display.view_config import DisplayViewConfig


class ShareableLinkModelDisplay(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="valid_until", label=_("Valid Until")),
                dp.Field(key="one_time_link", label=_("One Time Link")),
                dp.Field(key="link", label=_("Link")),
            ],
            legends=[
                dp.Legend(
                    key="valid",
                    items=[
                        dp.LegendItem(
                            icon=WBColor.GREEN_LIGHT.value,
                            label=_("Valid"),
                            value=True,
                        ),
                    ],
                )
            ],
            formatting=[
                dp.Formatting(
                    column="valid",
                    formatting_rules=[
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.GREEN_LIGHT.value},
                            condition=("==", True),
                        ),
                    ],
                ),
            ],
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [["link", "link"], ["valid_until", "one_time_link"], [repeat_field(2, "hits_section")]],
            [create_simple_section("hits_section", _("Hits"), [["hits"]], "hits", collapsed=False)],
        )


class ShareableLinkAccessModelDisplay(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="accessed", label=_("Date")),
                dp.Field(key="metadata_repr", label=_("Meta Data")),
            ],
        )

    def get_instance_display(self) -> Display:
        return create_simple_display([["accessed", "metadata"]])
