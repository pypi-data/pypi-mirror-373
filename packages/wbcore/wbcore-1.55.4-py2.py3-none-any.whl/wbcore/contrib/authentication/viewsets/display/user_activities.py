from datetime import date, timedelta
from typing import Optional

from django.utils.translation import gettext as _

from wbcore.contrib.color.enums import WBColor
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.view_config import DisplayViewConfig

from ...models import UserActivity


class UserActivityModelDisplay(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="IP", label=_("IP")),
                dp.Field(key="user", label=_("User")),
                dp.Field(key="date", label=_("First Login")),
                dp.Field(key="latest_refresh", label=_("Latest Refresh")),
                dp.Field(key="time_online_minute", label=_("Time Online (Minutes)")),
                dp.Field(key="user_agent_info", label=_("Agent Info")),
            ],
            formatting=[
                dp.Formatting(
                    column="status",
                    formatting_rules=[
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.GREEN_LIGHT.value},
                            condition=("==", UserActivity.SUCCESS),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.RED_LIGHT.value},
                            condition=("==", UserActivity.FAILED),
                        ),
                    ],
                )
            ],
            legends=[
                dp.Legend(
                    key="status",
                    items=[
                        dp.LegendItem(
                            icon=WBColor.GREEN_LIGHT.value,
                            label=UserActivity.SUCCESS,
                            value=UserActivity.SUCCESS,
                        ),
                        dp.LegendItem(
                            icon=WBColor.RED_LIGHT.value,
                            label=UserActivity.FAILED,
                            value=UserActivity.FAILED,
                        ),
                    ],
                )
            ],
        )


class UserActivityModelUserDisplay(UserActivityModelDisplay):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="IP", label=_("IP")),
                dp.Field(key="user", label=_("User")),
                dp.Field(key="date", label=_("First Login")),
                dp.Field(key="latest_refresh", label=_("Latest Refresh")),
                dp.Field(key="time_online_minute", label=_("Time Online (Minutes)")),
                dp.Field(key="user_agent_info", label=_("Agent Info")),
            ],
            formatting=super().get_list_display().formatting,
            legends=super().get_list_display().legends,
        )


class UserActivityTableDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        today = date.today()
        display = dp.ListDisplay(
            fields=[
                dp.Field(key="user_repr", label=_("User")),
                dp.Field(key="beforeyesterday_activity", label=f"{today - timedelta(days=2)}"),
                dp.Field(key="yesterday_activity", label=f"{today - timedelta(days=1)}"),
                dp.Field(key="today_activity", label=f"{today}"),
            ]
        )
        return display
