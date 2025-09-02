from django.utils.translation import gettext as _

from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display import Display, Layout, Page, Style
from wbcore.metadata.configs.display.instance_display.enums import NavigationType
from wbcore.metadata.configs.display.instance_display.operators import default, lte
from wbcore.metadata.configs.display.list_display import ListDisplay
from wbcore.metadata.configs.display.view_config import DisplayViewConfig

SEASON_FIELDS = [
    dp.Field(key="name", label=_("Season Name")),
    dp.Field(key="league", label=_("League")),
    dp.Field(key="date_range", label=_("Range")),
    dp.Field(key="duration", label=_("Duration")),
    dp.Field(key="winner", label=_("Winner")),
    dp.Field(key="top_scorer", label=_("Top Scorer")),
]


class SeasonDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> ListDisplay:
        return dp.ListDisplay(
            fields=(
                dp.Field(key="name", label=_("Season Name")),
                dp.Field(key="league", label=_("League")),
                dp.Field(key="winner", label=_("Winner")),
                dp.Field(key="top_scorer", label=_("Top Scorer")),
                dp.Field(key="date_range", label=_("Range")),
            )
        )

    def get_instance_display(self) -> Display:
        return Display(
            navigation_type=NavigationType.PAGE,
            pages=[
                Page(
                    title=_("Season"),
                    layouts={
                        default(): Layout(
                            grid_template_areas=[
                                ["name", "league"],
                                ["date_range", "date_range"],
                                ["winner", "top_scorer"],
                                ["file", "."],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(5),
                        ),
                        lte(550): Layout(
                            grid_template_areas=[
                                ["name"],
                                ["league"],
                                ["date_range"],
                                ["winner"],
                                ["top_scorer"],
                                ["file"],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(3),
                        ),
                    },
                ),
            ],
        )
