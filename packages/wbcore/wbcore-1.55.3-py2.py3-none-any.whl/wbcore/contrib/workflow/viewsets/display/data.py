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


class DataDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        fields = [
            dp.Field(key="label", label=_("Label")),
            dp.Field(key="workflow", label=_("Workflow")),
            dp.Field(key="data_type", label=_("Data Type")),
            dp.Field(key="required", label=_("Required")),
            dp.Field(key="help_text", label=_("Help Text")),
            dp.Field(key="default", label=_("Default")),
        ]

        if "workflow_id" in self.view.kwargs:
            fields.pop(1)

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
                                ["label", "workflow", "data_type"],
                                ["required", "help_text", "default"],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(5),
                        ),
                    },
                ),
            ]
        )
