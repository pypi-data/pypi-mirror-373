from typing import Optional

from django.utils.translation import gettext as _

from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display import DisplayViewConfig
from wbcore.metadata.configs.display.instance_display import (
    Display,
    Inline,
    Layout,
    Page,
    Section,
    Style,
)
from wbcore.metadata.configs.display.instance_display.operators import default


class TransitionDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=(
                dp.Field(key="name", label=_("Name")),
                dp.Field(key="from_step", label=_("From")),
                dp.Field(key="to_step", label=_("To")),
                dp.Field(key="icon", label=_("Icon")),
            ),
        )

    def get_instance_display(self) -> Display:
        conditions_section = Section(
            key="conditions_section",
            collapsible=True,
            title=_("Conditions"),
            display=Display(
                pages=[
                    Page(
                        title=_("Conditions"),
                        layouts={
                            default(): Layout(
                                grid_template_areas=[["conditions_inline"]],
                                grid_template_columns=[
                                    "minmax(min-content, 1fr)",
                                ],
                                grid_auto_rows=Style.MIN_CONTENT,
                                inlines=[Inline(key="conditions_inline", endpoint="conditions")],
                            )
                        },
                    ),
                ]
            ),
        )

        return Display(
            pages=[
                Page(
                    layouts={
                        default(): Layout(
                            grid_template_areas=[
                                ["name", "icon"],
                                ["from_step", "to_step"],
                                [
                                    "conditions_section",
                                    "conditions_section",
                                ]
                                if "pk" in self.view.kwargs
                                else [".", "."],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(3),
                            sections=[conditions_section],
                        ),
                    },
                ),
            ]
        )
