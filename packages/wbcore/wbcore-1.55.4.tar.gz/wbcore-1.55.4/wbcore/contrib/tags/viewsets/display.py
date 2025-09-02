from typing import Optional

from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
    create_simple_section,
)
from wbcore.metadata.configs.display.instance_display.utils import repeat_field
from wbcore.metadata.configs.display.view_config import DisplayViewConfig
from wbcore.metadata.configs.preview import PreviewViewConfig


class TagGroupDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(fields=[dp.Field(key="title", label="Title")])

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [["title"], ["tags_sections"]],
            [create_simple_section("tags_sections", "Tags", [["tags"]], "tags", collapsed=True)],
        )


class TagDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="title", label="Title"),
                dp.Field(key="color", label="Color"),
                dp.Field(key="slug", label="Slug"),
                dp.Field(key="groups", label="Groups"),
                dp.Field(key="content_type", label="Content Type"),
                dp.Field(key="description", label="Description"),
            ]
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                [repeat_field(2, "title"), "slug"],
                ["groups", "color", "content_type"],
                [repeat_field(3, "description")],
            ]
        )


class TagPreviewConfig(PreviewViewConfig):
    def get_display(self):
        return create_simple_display([["title", "groups", "description"]])
