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


class SportDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> ListDisplay:
        return dp.ListDisplay(
            fields=(
                dp.Field(key="name", label=_("Name")),
                dp.Field(key="match_duration", label=_("Match Duration")),
                dp.Field(key="rules", label=_("Rules")),
            )
        )

    def get_instance_display(self) -> Display:
        leagues_section = Section(
            key="leagues_section",
            collapsible=False,
            title=_("Leagues"),
            display=Display(
                pages=[
                    Page(
                        title=_("Leagues"),
                        layouts={
                            default(): Layout(
                                grid_template_areas=[["leagues_inline"]],
                                grid_template_columns=[
                                    "minmax(min-content, 1fr)",
                                ],
                                grid_auto_rows=Style.MIN_CONTENT,
                                inlines=[Inline(key="leagues_inline", endpoint="existing_leagues")],
                            )
                        },
                    ),
                ]
            ),
        )
        event_types_section = Section(
            key="event_types_section",
            title=_("Event Types"),
            display=Display(
                pages=[
                    Page(
                        title=_("Event Types"),
                        layouts={
                            default(): Layout(
                                grid_template_areas=[["event_types_inline"]],
                                grid_template_columns=["minmax(min-content, 1fr)"],
                                grid_auto_rows=Style.MIN_CONTENT,
                                inlines=[Inline(key="event_types_inline", endpoint="associated_event_types")],
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
                            grid_template_areas=[
                                ["name", "leagues_section"],
                                ["match_duration", "leagues_section"],
                                ["rules", "leagues_section"],
                                ["event_types_section", "event_types_section"],
                            ]
                            if not is_create_display
                            else [["name", "match_duration", "rules"]],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(5),
                            sections=[leagues_section, event_types_section],
                        ),
                        lte(1000): Layout(
                            grid_template_areas=[
                                ["name", "match_duration"],
                                ["rules", "rules"],
                                ["leagues_section", "leagues_section"],
                                ["event_types_section", "event_types_section"],
                            ]
                            if not is_create_display
                            else [["name", "match_duration"], ["rules", "rules"]],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(3),
                            sections=[leagues_section, event_types_section],
                        ),
                        lte(650): Layout(
                            grid_template_areas=[
                                ["name"],
                                ["match_duration"],
                                ["rules"],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                        ),
                    },
                ),
            ]
        )
