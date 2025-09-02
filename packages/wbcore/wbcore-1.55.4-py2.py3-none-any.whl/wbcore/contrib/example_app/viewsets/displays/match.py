from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _

from wbcore.contrib.example_app.models import Match
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display import (
    Display,
    Inline,
    Layout,
    Page,
    Section,
    Style,
)
from wbcore.metadata.configs.display.instance_display.operators import default, lte
from wbcore.metadata.configs.display.list_display import ListDisplay
from wbcore.metadata.configs.display.view_config import DisplayViewConfig

MATCH_FIELDS = [
    dp.Field(key="home", label=_("Home")),
    dp.Field(key="score_home", label=_("Home Score")),
    dp.Field(key="away", label=_("Away")),
    dp.Field(key="score_away", label=_("Away Score")),
    dp.Field(key="league", label=_("League")),
    dp.Field(key="date_time", label=_("Date Time")),
    dp.Field(key="stadium", label=_("Stadium")),
    dp.Field(key="referee", label=_("Referee")),
]


def get_match_status_legend() -> list[dp.Legend]:
    """Dynamically creates the match legend based on the status enum using the color mapping"""

    legend_items = []
    for status, color in Match.MatchStatus.get_color_map():
        legend_items.append(dp.LegendItem(icon=color, label=status.label, value=status.value))
    return [dp.Legend(key="status", items=legend_items)]


def get_match_status_formatting() -> list[dp.Formatting]:
    """Dynamically creates the match list formatting based on the status enum using the color mapping"""

    formatting_rules = []
    for status, color in Match.MatchStatus.get_color_map():
        formatting_rules.append(dp.FormattingRule(condition=("==", status.value), style={"backgroundColor": color}))
    return [dp.Formatting(column="status", formatting_rules=formatting_rules)]


class MatchDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> ListDisplay:
        return dp.ListDisplay(
            fields=MATCH_FIELDS,
            legends=get_match_status_legend(),
            formatting=get_match_status_formatting(),
        )

    def get_instance_display(self) -> Display:
        events_section = Section(
            key="events_section",
            collapsible=False,
            title=_("Events"),
            display=Display(
                pages=[
                    Page(
                        title=_("Events"),
                        layouts={
                            default(): Layout(
                                grid_template_areas=[["events_inline"]],
                                grid_template_columns=[
                                    "minmax(min-content, 1fr)",
                                ],
                                grid_auto_rows=Style.MIN_CONTENT,
                                inlines=[Inline(key="events_inline", endpoint="event_list")],
                            )
                        },
                    ),
                ]
            ),
        )
        ongoing_or_finished_display = Display(
            pages=[
                Page(
                    title=_("Score"),
                    layouts={
                        default(): Layout(
                            grid_template_areas=[
                                ["score_home", "score_away"],
                                ["home", "away"],
                                ["events_section", "events_section"],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(5),
                            sections=[events_section],
                        ),
                    },
                ),
                Page(
                    title=_("Match Details"),
                    layouts={
                        default(): Layout(
                            grid_template_areas=[
                                ["date_time", "stadium", "referee"],
                                ["sport", "league", "."],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(5),
                        ),
                        lte(900): Layout(
                            grid_template_areas=[
                                ["date_time", "stadium"],
                                ["referee", "sport"],
                                ["league", "."],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(5),
                        ),
                        lte(400): Layout(
                            grid_template_areas=[["date_time"], ["stadium"], ["referee"], ["sport"], ["league"]],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                        ),
                    },
                ),
            ]
        )
        scheduled_display = Display(
            pages=[
                Page(
                    layouts={
                        default(): Layout(
                            grid_template_areas=[
                                ["home", "away", "referee"],
                                ["date_time", "stadium", "."],
                                ["sport", "league", "."],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(5),
                        ),
                        lte(900): Layout(
                            grid_template_areas=[
                                ["home", "away"],
                                ["date_time", "stadium"],
                                ["sport", "league"],
                                ["referee", "."],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(3),
                        ),
                        lte(550): Layout(
                            grid_template_areas=[
                                ["home"],
                                ["away"],
                                ["date_time"],
                                ["stadium"],
                                ["sport"],
                                ["league"],
                                ["referee"],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                        ),
                    },
                ),
            ]
        )

        if match_id := self.view.kwargs.get("pk"):
            # Can this be optimized in any way?
            match_obj = get_object_or_404(Match, pk=match_id)
            if match_obj.status != Match.MatchStatus.SCHEDULED:
                return ongoing_or_finished_display
        return scheduled_display


class MatchStadiumDisplayConfig(MatchDisplayConfig):
    def get_list_display(self) -> ListDisplay:
        fields = MATCH_FIELDS.copy()
        fields.pop(6)
        return dp.ListDisplay(
            fields=fields,
            legends=get_match_status_legend(),
            formatting=get_match_status_formatting(),
        )

    def get_instance_display(self) -> Display:
        if "pk" in self.view.kwargs:
            return super().get_instance_display()

        return Display(
            pages=[
                Page(
                    layouts={
                        default(): Layout(
                            grid_template_areas=[["home", "away", "date_time"], ["league", "referee", "."]],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(5),
                        ),
                        lte(900): Layout(
                            grid_template_areas=[["home", "away"], ["league", "referee"], ["date_time", "."]],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(3),
                        ),
                        lte(600): Layout(
                            grid_template_areas=[["home"], ["away"], ["league"], ["date_time"], ["referee"]],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                        ),
                    },
                ),
            ]
        )


class MatchLeagueDisplayConfig(MatchDisplayConfig):
    def get_list_display(self) -> ListDisplay:
        fields = MATCH_FIELDS.copy()
        fields.pop(4)
        return dp.ListDisplay(
            fields=fields,
            legends=get_match_status_legend(),
            formatting=get_match_status_formatting(),
        )

    def get_instance_display(self) -> Display:
        if "pk" in self.view.kwargs:
            return super().get_instance_display()

        return Display(
            pages=[
                Page(
                    layouts={
                        default(): Layout(
                            grid_template_areas=[["home", "away", "sport"], ["stadium", "date_time", "referee"]],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(5),
                        ),
                        lte(900): Layout(
                            grid_template_areas=[["home", "away"], ["stadium", "date_time"], ["sport", "referee"]],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(3),
                        ),
                        lte(600): Layout(
                            grid_template_areas=[
                                ["home"],
                                ["away"],
                                ["stadium"],
                                ["date_time"],
                                ["sport"],
                                ["referee"],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                        ),
                    },
                ),
            ]
        )
