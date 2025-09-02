from django.utils.translation import gettext as _

from wbcore.contrib.example_app.utils import get_event_types_for_league
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
from wbcore.metadata.configs.display.instance_display.utils import (
    split_list_into_grid_template_area_sublists,
)
from wbcore.metadata.configs.display.list_display import ListDisplay
from wbcore.metadata.configs.display.view_config import DisplayViewConfig

LEAGUE_FIELDS = [
    dp.Field(key="name", label=_("Name")),
    dp.Field(key="sport", label=_("Sport")),
    dp.Field(key="points_per_win", label=_("Points Per Win")),
    dp.Field(key="points_per_draw", label=_("Points Per Draw")),
    dp.Field(key="points_per_loss", label=_("Points Per Loss")),
    dp.Field(key="country", label=_("Country")),
    dp.Field(key="established_date", label=_("Established")),
    dp.Field(key="commissioner", label=_("Commissioner")),
    dp.Field(key="website", label=_("Website")),
]


class LeagueDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> ListDisplay:
        return dp.ListDisplay(fields=LEAGUE_FIELDS)

    def get_instance_display(self) -> Display:
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
        table_section = Section(
            key="table_section",
            collapsible=False,
            title=_("Table"),
            display=Display(
                pages=[
                    Page(
                        title=_("Table"),
                        layouts={
                            default(): Layout(
                                grid_template_areas=[["table_inline"]],
                                grid_template_columns=[
                                    "minmax(min-content, 1fr)",
                                ],
                                grid_auto_rows=Style.MIN_CONTENT,
                                inlines=[Inline(key="table_inline", endpoint="table")],
                            )
                        },
                    ),
                ]
            ),
        )

        if league_id := self.view.kwargs.get("pk"):
            event_types = get_event_types_for_league(int(league_id))
            player_sections = [
                Section(
                    key=f"player_{event_type['slugified_name']}_section",
                    collapsible=False,
                    title=f"{event_type['name']}s",
                    display=Display(
                        pages=[
                            Page(
                                title=f"{event_type['name']}s",
                                layouts={
                                    default(): Layout(
                                        grid_template_areas=[[f"player_{event_type['slugified_name']}_inline"]],
                                        grid_template_columns=[
                                            "minmax(min-content, 1fr)",
                                        ],
                                        grid_auto_rows=Style.MIN_CONTENT,
                                        inlines=[
                                            Inline(
                                                key=f"player_{event_type['slugified_name']}_inline",
                                                endpoint=f"player_{event_type['slugified_name']}",
                                            )
                                        ],
                                    )
                                },
                            ),
                        ]
                    ),
                )
                for event_type in event_types
            ]
            team_sections = [
                Section(
                    key=f"team_{event_type['slugified_name']}_section",
                    collapsible=False,
                    title=f"{event_type['name']}s",
                    display=Display(
                        pages=[
                            Page(
                                title=f"{event_type['name']}s",
                                layouts={
                                    default(): Layout(
                                        grid_template_areas=[[f"team_{event_type['slugified_name']}_inline"]],
                                        grid_template_columns=[
                                            "minmax(min-content, 1fr)",
                                        ],
                                        grid_auto_rows=Style.MIN_CONTENT,
                                        inlines=[
                                            Inline(
                                                key=f"team_{event_type['slugified_name']}_inline",
                                                endpoint=f"team_{event_type['slugified_name']}",
                                            )
                                        ],
                                    )
                                },
                            ),
                        ]
                    ),
                )
                for event_type in event_types
            ]
            player_section_keys = [section.key for section in player_sections]
            team_section_keys = [section.key for section in team_sections]

            return Display(
                pages=[
                    Page(
                        title=_("Main Information"),
                        layouts={
                            default(): Layout(
                                grid_template_areas=[
                                    ["name", "name", "sport", "matches_section", "matches_section"],
                                    [
                                        "points_per_win",
                                        "points_per_draw",
                                        "points_per_loss",
                                        "matches_section",
                                        "matches_section",
                                    ],
                                    ["country", "commissioner", ".", "matches_section", "matches_section"],
                                    ["established_date", "website", ".", "matches_section", "matches_section"],
                                    [
                                        "table_section",
                                        "table_section",
                                        "table_section",
                                        "table_section",
                                        "table_section",
                                    ],
                                ],
                                grid_auto_columns="minmax(min-content, 1fr)",
                                grid_auto_rows=Style.MIN_CONTENT,
                                column_gap=Style.rem(5),
                                sections=[matches_section, table_section],
                            ),
                            lte(1000): Layout(
                                grid_template_areas=[
                                    ["name", "sport"],
                                    ["points_per_win", "points_per_draw"],
                                    ["points_per_loss", "website"],
                                    ["country", "commissioner"],
                                    ["established_date", "."],
                                    ["table_section", "table_section"],
                                    ["matches_section", "matches_section"],
                                ],
                                grid_auto_columns="minmax(min-content, 1fr)",
                                grid_auto_rows=Style.MIN_CONTENT,
                                column_gap=Style.rem(3),
                                sections=[matches_section, table_section],
                            ),
                            lte(450): Layout(
                                grid_template_areas=[
                                    ["name"],
                                    ["sport"],
                                    ["points_per_win"],
                                    ["points_per_draw"],
                                    ["points_per_loss"],
                                    ["country"],
                                    ["commissioner"],
                                    ["website"],
                                    ["established_date"],
                                ],
                                grid_auto_columns="minmax(min-content, 1fr)",
                                grid_auto_rows=Style.MIN_CONTENT,
                            ),
                        },
                    ),
                    Page(
                        title=_("Player Statistics"),
                        layouts={
                            default(): Layout(
                                grid_template_areas=split_list_into_grid_template_area_sublists(
                                    player_section_keys, 3
                                ),
                                grid_auto_columns="minmax(min-content, 1fr)",
                                grid_auto_rows=Style.MIN_CONTENT,
                                column_gap=Style.rem(5),
                                sections=player_sections,
                            ),
                            lte(1000): Layout(
                                grid_template_areas=split_list_into_grid_template_area_sublists(
                                    player_section_keys, 2
                                ),
                                grid_auto_columns="minmax(min-content, 1fr)",
                                grid_auto_rows=Style.MIN_CONTENT,
                                column_gap=Style.rem(3),
                                sections=player_sections,
                            ),
                            lte(650): Layout(
                                grid_template_areas=split_list_into_grid_template_area_sublists(
                                    player_section_keys, 1
                                ),
                                grid_auto_columns="minmax(min-content, 1fr)",
                                grid_auto_rows=Style.MIN_CONTENT,
                                sections=player_sections,
                            ),
                        },
                    ),
                    Page(
                        title=_("Team Statistics"),
                        layouts={
                            default(): Layout(
                                grid_template_areas=split_list_into_grid_template_area_sublists(team_section_keys, 3),
                                grid_auto_columns="minmax(min-content, 1fr)",
                                grid_auto_rows=Style.MIN_CONTENT,
                                column_gap=Style.rem(5),
                                sections=team_sections,
                            ),
                            lte(1000): Layout(
                                grid_template_areas=split_list_into_grid_template_area_sublists(team_section_keys, 2),
                                grid_auto_columns="minmax(min-content, 1fr)",
                                grid_auto_rows=Style.MIN_CONTENT,
                                column_gap=Style.rem(3),
                                sections=team_sections,
                            ),
                            lte(650): Layout(
                                grid_template_areas=split_list_into_grid_template_area_sublists(team_section_keys, 1),
                                grid_auto_columns="minmax(min-content, 1fr)",
                                grid_auto_rows=Style.MIN_CONTENT,
                                sections=team_sections,
                            ),
                        },
                    ),
                ]
            )
        return Display(
            pages=[
                Page(
                    title=_("Main Information"),
                    layouts={
                        default(): Layout(
                            grid_template_areas=[
                                ["name", "name", "sport"],
                                ["points_per_win", "points_per_draw", "points_per_loss"],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(5),
                        ),
                        lte(800): Layout(
                            grid_template_areas=[
                                ["name", "sport"],
                                ["points_per_win", "points_per_draw"],
                                ["points_per_loss", "."],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(3),
                        ),
                        lte(450): Layout(
                            grid_template_areas=[
                                ["name"],
                                ["sport"],
                                ["points_per_win"],
                                ["points_per_draw"],
                                ["points_per_loss"],
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
                                ["country", "commissioner"],
                                ["established_date", "website"],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(5),
                        ),
                        lte(700): Layout(
                            grid_template_areas=[
                                ["country"],
                                ["commissioner"],
                                ["established_date"],
                                ["website"],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                        ),
                    },
                ),
            ]
        )


class LeagueSportDisplayConfig(LeagueDisplayConfig):
    def get_list_display(self) -> ListDisplay:
        fields = LEAGUE_FIELDS.copy()
        fields.pop(1)
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
                            grid_template_areas=[["name", "points_per_win"], ["points_per_draw", "points_per_loss"]],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(5),
                        ),
                        lte(450): Layout(
                            grid_template_areas=[
                                ["name"],
                                ["points_per_win"],
                                ["points_per_draw"],
                                ["points_per_loss"],
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
                                ["country", "commissioner"],
                                ["established_date", "website"],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(5),
                        ),
                        lte(700): Layout(
                            grid_template_areas=[
                                ["country"],
                                ["commissioner"],
                                ["established_date"],
                                ["website"],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                        ),
                    },
                ),
            ]
        )
