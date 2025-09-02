from typing import Optional

from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.view_config import DisplayViewConfig


class CurrencyFXRatesCurrencyDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(fields=[dp.Field(key="date", label="Date"), dp.Field(key="value", label="Value")])
