from typing import Optional

from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.view_config import DisplayViewConfig


class CalendarItemDisplay(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.Calendar(
            title="title",
            period="period",
            endpoint="endpoint",
            all_day="all_day",
            color="color",
            icon="icon",
            entities="entity_list",
        )
