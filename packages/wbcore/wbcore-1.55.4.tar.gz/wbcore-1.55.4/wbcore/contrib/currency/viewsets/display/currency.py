from typing import Optional

from django.utils.translation import gettext_lazy as _

from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
    create_simple_section,
)
from wbcore.metadata.configs.display.instance_display.utils import repeat_field
from wbcore.metadata.configs.display.view_config import DisplayViewConfig


class CurrencyDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="title", label="Title"),
                dp.Field(key="symbol", label="Sybmol"),
                dp.Field(key="key", label="Key"),
                dp.Field(key="rates_sparkline", label="Rates"),
            ]
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [["title", "symbol", "key"], [repeat_field(3, "currencyfxrates_section")]],
            [
                create_simple_section(
                    "currencyfxrates_section",
                    _("Rates"),
                    [["currency_currencyfxrates"]],
                    "currency_currencyfxrates",
                    collapsed=False,
                )
            ],
        )
