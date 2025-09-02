from django.utils.translation import gettext as _

from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display import Display, Layout, Page, Style
from wbcore.metadata.configs.display.instance_display.operators import default, lte
from wbcore.metadata.configs.display.list_display import ListDisplay
from wbcore.metadata.configs.display.view_config import DisplayViewConfig

EVENT_TYPE_FIELDS = [
    dp.Field(key="name", label=_("Name")),
    dp.Field(key="sport", label=_("Sport")),
    dp.Field(key="points", label=_("Points")),
    dp.Field(key="icon", label=_("Icon")),
    dp.Field(key="color", label=_("Color")),
]
EVENT_FIELDS = [
    dp.Field(key="match", label=_("Match")),
    dp.Field(key="event_type", label=_("Event Type")),
    dp.Field(key="person", label=_("Person")),
    dp.Field(key="minute", label=_("Minute")),
]


class EventDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> ListDisplay:
        return dp.ListDisplay(fields=EVENT_FIELDS)

    def get_instance_display(self) -> Display:
        return Display(
            pages=[
                Page(
                    layouts={
                        default(): Layout(
                            grid_template_areas=[
                                ["match", "event_type"],
                                ["person", "minute"],
                                ["event_description", "event_description"],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(5),
                        ),
                        lte(650): Layout(
                            grid_template_areas=[
                                ["match"],
                                ["event_type"],
                                ["person"],
                                ["minute"],
                                ["event_description"],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                        ),
                    },
                ),
            ]
        )


class LeaguePlayerStatisticsDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> ListDisplay:
        return dp.ListDisplay(
            fields=(dp.Field(key="person_name", label=_("Person")), dp.Field(key="count", label=_(" "))),
        )


class LeagueTeamStatisticsDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> ListDisplay:
        return dp.ListDisplay(
            fields=(dp.Field(key="team_name", label=_("Team")), dp.Field(key="count", label=_(" "))),
        )


class EventMatchDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> ListDisplay:
        fields = EVENT_FIELDS.copy()
        fields.pop(0)
        return dp.ListDisplay(fields=fields)

    def get_instance_display(self) -> Display:
        return Display(
            pages=[
                Page(
                    layouts={
                        default(): Layout(
                            grid_template_areas=[
                                ["event_type", "person", "minute"],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(5),
                        ),
                        lte(800): Layout(
                            grid_template_areas=[
                                ["event_type", "."],
                                ["person", "minute"],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(3),
                        ),
                        lte(450): Layout(
                            grid_template_areas=[
                                ["event_type"],
                                ["person"],
                                ["minute"],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                        ),
                    },
                ),
            ]
        )


class EventTypeDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> ListDisplay:
        return dp.ListDisplay(fields=EVENT_TYPE_FIELDS)

    def get_instance_display(self) -> Display:
        return Display(
            pages=[
                Page(
                    layouts={
                        default(): Layout(
                            grid_template_areas=[
                                ["name", "sport"],
                                ["points", "icon"],
                                ["color", "color"],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(5),
                        ),
                        lte(650): Layout(
                            grid_template_areas=[
                                ["name"],
                                ["sport"],
                                ["points"],
                                ["icon"],
                                ["color"],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                        ),
                    },
                ),
            ]
        )


class EventTypeSportDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> ListDisplay:
        fields = EVENT_TYPE_FIELDS.copy()
        fields.pop(1)
        return dp.ListDisplay(fields=fields)

    def get_instance_display(self) -> Display:
        return Display(
            pages=[
                Page(
                    layouts={
                        default(): Layout(
                            grid_template_areas=[
                                ["name", "points"],
                                ["icon", "color"],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(5),
                        ),
                        lte(650): Layout(
                            grid_template_areas=[
                                ["name"],
                                ["sport"],
                                ["points"],
                                ["icon"],
                                ["color"],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                        ),
                    },
                ),
            ]
        )
