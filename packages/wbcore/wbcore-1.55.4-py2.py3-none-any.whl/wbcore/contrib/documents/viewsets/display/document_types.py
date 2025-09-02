from typing import Optional

from django.utils.translation import gettext as _

from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
)
from wbcore.metadata.configs.display.view_config import DisplayViewConfig


class DocumentTypeModelDisplay(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="name", label=_("Name")),
                dp.Field(key="parent", label=_("Parent")),
                dp.Field(key="document_count", label=_("Number of Documents")),
            ],
        )

    def get_instance_display(self) -> Display:
        return create_simple_display([["name", "parent"]])
