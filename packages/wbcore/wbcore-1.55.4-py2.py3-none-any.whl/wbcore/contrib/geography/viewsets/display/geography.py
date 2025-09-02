from typing import Optional

from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
)
from wbcore.metadata.configs.display.view_config import DisplayViewConfig


class GeographyDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="name", label="Name"),
                dp.Field(key="parent", label="Parent"),
                dp.Field(key="code_2", label="Alpha 2 Country Code"),
                dp.Field(key="code_3", label="Alpha 3 Country Code"),
            ]
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                [
                    "name",
                    "parent",
                    "code_2",
                    "code_3",
                ]
            ]
        )
