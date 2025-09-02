from typing import Optional

from django.utils.translation import gettext as _

from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display import DisplayViewConfig
from wbcore.metadata.configs.display.instance_display import (
    Display,
    Layout,
    Page,
    Style,
)
from wbcore.metadata.configs.display.instance_display.operators import default


class ConditionDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        fields = [
            dp.Field(key="transition", label=_("Transition")),
            dp.Field(key="attribute_name", label=_("Attribute Name")),
            dp.Field(key="operator", label=_("Operator")),
            dp.Field(key="negate_operator", label=_("Negate Operator")),
            dp.Field(key="expected_value", label=_("Expected Value")),
        ]

        if "transition_id" in self.view.kwargs:
            fields.pop(0)

        return dp.ListDisplay(
            fields=fields,
        )

    def get_instance_display(self) -> Display:
        return Display(
            pages=[
                Page(
                    layouts={
                        default(): Layout(
                            grid_template_areas=[
                                ["transition", "attribute_name"],
                                ["operator", "negate_operator"],
                                ["expected_value", "."],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(5),
                        ),
                    },
                ),
            ]
        )
