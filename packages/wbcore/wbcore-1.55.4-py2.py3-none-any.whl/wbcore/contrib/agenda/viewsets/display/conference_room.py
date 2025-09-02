from typing import Optional

from django.utils.translation import gettext as _

from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
)
from wbcore.metadata.configs.display.instance_display.utils import repeat_field
from wbcore.metadata.configs.display.view_config import DisplayViewConfig


class BuildingDisplay(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="name", label=_("Name")),
                dp.Field(key="address", label=_("Address")),
            ]
        )

    def get_instance_display(self) -> Display:
        return create_simple_display([["name", "address"]])


class ConferenceRoomDisplay(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="name", label=_("Name")),
                dp.Field(key="email", label=_("E-Mail-Address")),
                dp.Field(key="building", label=_("Building")),
                dp.Field(key="capacity", label=_("Capacity")),
                dp.Field(key="is_videoconference_capable", label=_("Capable of Videoconferencing")),
            ]
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [[repeat_field(2, "name"), "email"], ["building", "capacity", "is_videoconference_capable"]]
        )
