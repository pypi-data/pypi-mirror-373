from django.utils.translation import gettext as _

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


class StadiumDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> ListDisplay:
        return dp.ListDisplay(
            fields=(
                dp.Field(key="name", label=_("Name")),
                dp.Field(key="city", label=_("City")),
                dp.Field(key="guest_rating", label=_("Rating")),
                dp.Field(
                    key="capacity",
                    label=_("Capacity"),
                    open_by_default=False,
                    children=[
                        dp.Field(key="total_capacity", label=_("Total Capacity")),
                        dp.Field(key="seating_capacity", label=_("Seated"), show="open"),
                        dp.Field(key="standing_capacity", label=_("Standing"), show="open"),
                    ],
                ),
            )
        )

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
        teams_section = Section(
            key="teams_section",
            title=_("Teams"),
            display=Display(
                pages=[
                    Page(
                        title=_("Teams"),
                        layouts={
                            default(): Layout(
                                grid_template_areas=[["teams_inline"]],
                                grid_template_columns=[
                                    "minmax(min-content, 1fr)",
                                ],
                                grid_auto_rows=Style.MIN_CONTENT,
                                inlines=[Inline(key="teams_inline", endpoint="teams_playing")],
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
                    layouts={
                        default(): Layout(
                            grid_template_areas=(
                                [
                                    ["name", "city", "matches_section", "matches_section"],
                                    ["capacity", ".", "matches_section", "matches_section"],
                                    ["guest_rating", ".", "matches_section", "matches_section"],
                                    ["teams_section", "teams_section", "teams_section", "teams_section"],
                                ]
                                if not is_create_display
                                else [["name", "city", "capacity"]]
                            ),
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(5),
                            sections=[teams_section, matches_section],
                        ),
                        lte(1100): Layout(
                            grid_template_areas=(
                                [
                                    ["name", "city", "capacity"],
                                    ["matches_section", "matches_section", "matches_section"],
                                    ["teams_section", "teams_section", "teams_section"],
                                    ["guest_rating", ".", "."],
                                ]
                                if not is_create_display
                                else [["name", "city", "capacity"]]
                            ),
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(3),
                            row_gap=Style.rem(3),
                            sections=[teams_section, matches_section],
                        ),
                        lte(600): Layout(
                            grid_template_areas=(
                                [
                                    ["name", "city"],
                                    ["capacity", "."],
                                    ["matches_section", "matches_section"],
                                    ["teams_section", "teams_section"],
                                    ["guest_rating", "."],
                                ]
                                if not is_create_display
                                else [["name", "city"], ["capacity", "."]]
                            ),
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            sections=[teams_section, matches_section],
                        ),
                        lte(430): Layout(
                            grid_template_areas=[
                                ["name"],
                                ["city"],
                                ["capacity"],
                                ["guest_rating"],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                        ),
                    }
                )
            ]
        )
