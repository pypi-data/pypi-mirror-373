from django.utils.translation import gettext as _
from rest_framework.reverse import reverse

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

TEAM_FIELDS = [
    dp.Field(key="city", label=_("City")),
    dp.Field(key="founded_date", label=_("Founded Date")),
    dp.Field(key="coach", label=_("Coach"), tooltip=dp.Tooltip(key="coach_tooltip")),
    dp.Field(key="home_stadium", label=_("Home Stadium")),
    dp.Field(
        key="computed_str",
        label=_("Name"),
        formatting_rules=[dp.FormattingRule(style={"fontWeight": "bold"}, condition=("==", "Altona 93"))],
    ),
]


class TeamDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> ListDisplay:
        return dp.ListDisplay(
            fields=TEAM_FIELDS,
            tree=True,
            tree_group_field="computed_str",
            tree_group_level_options=[
                dp.TreeGroupLevelOption(
                    filter_depth=1,
                    lookup="current_players__id",
                    filter_key="current_team",
                    list_endpoint=reverse("example_app:treeviewplayer-list", args=[], request=self.request),
                    reorder_endpoint=reverse("example_app:treeviewplayer-list", args=[], request=self.request)
                    + "{{id}}/reorder/",
                    reparent_endpoint=reverse("example_app:treeviewplayer-list", args=[], request=self.request)
                    + "{{id}}/reparent/",
                    parent_field="id",
                )
            ],
        )

    def get_instance_display(self) -> Display:
        players_section = Section(
            key="players_section",
            title=_("Players"),
            display=Display(
                pages=[
                    Page(
                        title=_("Players"),
                        layouts={
                            default(): Layout(
                                grid_template_areas=[["players_inline"]],
                                grid_template_columns=[
                                    "minmax(min-content, 1fr)",
                                ],
                                grid_auto_rows=Style.MIN_CONTENT,
                                inlines=[Inline(key="players_inline", endpoint="players")],
                            )
                        },
                    ),
                ]
            ),
        )
        matches_section = Section(
            key="matches_section",
            collapsible=False,
            title=_("Recent Matches"),
            display=Display(
                pages=[
                    Page(
                        title=_("Recent Matches"),
                        layouts={
                            default(): Layout(
                                grid_template_areas=[["matches_inline"]],
                                grid_template_columns=[
                                    "minmax(min-content, 1fr)",
                                ],
                                grid_auto_rows=Style.MIN_CONTENT,
                                inlines=[Inline(key="matches_inline", endpoint="recent_matches")],
                            )
                        },
                    ),
                ]
            ),
        )

        is_create_display = "pk" not in self.view.kwargs

        return Display(
            pages=[
                Page(
                    title=_("Main Information"),
                    layouts={
                        default(): Layout(
                            grid_template_areas=(
                                [
                                    [
                                        "name",
                                        "coach",
                                        "matches_section",
                                        "matches_section",
                                    ],
                                    [
                                        "home_stadium",
                                        ".",
                                        "matches_section",
                                        "matches_section",
                                    ],
                                    [".", ".", "matches_section", "matches_section"],
                                    [
                                        "players_section",
                                        "players_section",
                                        "players_section",
                                        "players_section",
                                    ],
                                ]
                                if not is_create_display
                                else [
                                    ["name", "name", "coach", "coach"],
                                    ["home_stadium", "home_stadium", ".", "."],
                                ]
                            ),
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(5),
                            sections=[players_section, matches_section],
                        ),
                        lte(1000): Layout(
                            grid_template_areas=(
                                [
                                    ["name", "coach"],
                                    ["home_stadium", "."],
                                    ["matches_section", "matches_section"],
                                    ["players_section", "players_section"],
                                ]
                                if not is_create_display
                                else [["name", "coach"], ["home_stadium", "."]]
                            ),
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(3),
                            sections=[players_section, matches_section],
                        ),
                        lte(450): Layout(
                            grid_template_areas=[
                                ["name"],
                                ["coach"],
                                ["home_stadium"],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                        ),
                    },
                ),
                Page(
                    title=_("Details"),
                    layouts={
                        default(): Layout(
                            grid_template_areas=[
                                ["city", "founded_date"],
                                ["phone_number", "email"],
                                ["duration_since_last_win", "."],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(5),
                        ),
                        lte(550): Layout(
                            grid_template_areas=[
                                ["city"],
                                ["founded_date"],
                                ["phone_number"],
                                ["email"],
                                ["duration_since_last_win"],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                        ),
                    },
                ),
            ],
        )


class TeamStadiumDisplayConfig(TeamDisplayConfig):
    def get_list_display(self) -> ListDisplay:
        fields = TEAM_FIELDS.copy()
        fields.insert(0, dp.Field(key="computed_str", label=_("Name")))
        fields.pop(4)
        return dp.ListDisplay(fields=fields)

    def get_instance_display(self) -> Display:
        if "pk" in self.view.kwargs:
            return super().get_instance_display()

        return Display(
            pages=[
                Page(
                    title=_("Main Information"),
                    layouts={
                        default(): Layout(
                            grid_template_areas=[["name", "coach", "league"]],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(5),
                        ),
                        lte(1000): Layout(
                            grid_template_areas=[["name", "coach"], ["league", "."]],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(3),
                        ),
                        lte(450): Layout(
                            grid_template_areas=[
                                ["name"],
                                ["coach"],
                                ["league"],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                        ),
                    },
                ),
                Page(
                    title=_("Details"),
                    layouts={
                        default(): Layout(
                            grid_template_areas=[["city", "founded_date"]],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(5),
                        ),
                        lte(550): Layout(
                            grid_template_areas=[["city"], ["founded_date"]],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                        ),
                    },
                ),
            ],
        )
