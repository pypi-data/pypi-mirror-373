from typing import Optional

from django.utils.translation import gettext as _

from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.view_config import DisplayViewConfig


class DocumentModelRelationshipViewConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="content_type", label=_("Type")),
                dp.Field(key="content_object_repr", label=_("Instance"), width=500),
            ],
        )

    def get_instance_display(self) -> dp.Display:
        return dp.create_simple_display([["content_type"], ["object_id"]])
