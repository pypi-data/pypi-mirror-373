from django.utils.translation import gettext as _

from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display import Display, Layout, Page, Style
from wbcore.metadata.configs.display.instance_display.enums import NavigationType
from wbcore.metadata.configs.display.instance_display.operators import default, lte
from wbcore.metadata.configs.display.list_display import ListDisplay
from wbcore.metadata.configs.display.view_config import DisplayViewConfig

PERSON_FIELDS = [
    dp.Field(key="first_name", label=_("First Name")),
    dp.Field(key="last_name", label=_("Last Name")),
    dp.Field(key="roles", label=_("Roles")),
]

PLAYER_FIELDS = [
    dp.Field(key="position", label=_("Position")),
    dp.Field(key="current_team", label=_("Current Team")),
    dp.Field(key="former_teams", label=_("Former Teams")),
    dp.Field(key="player_strength", label=_("Rating")),
    dp.Field(key="game_activity", label=_("Activities")),
    dp.Field(key="transfer_value", label=_("Market Value")),
]


class SportPersonDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> ListDisplay:
        return dp.ListDisplay(fields=PERSON_FIELDS)

    def get_instance_display(self) -> Display:
        return Display(
            pages=[
                Page(
                    layouts={
                        default(): Layout(
                            grid_template_areas=[
                                ["profile_image", ".", "."],
                                ["first_name", "last_name", "roles"],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(5),
                        ),
                        lte(800): Layout(
                            grid_template_areas=[
                                ["profile_image", "."],
                                ["first_name", "last_name"],
                                ["roles", "."],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(3),
                        ),
                        lte(550): Layout(
                            grid_template_areas=[
                                ["first_name"],
                                ["last_name"],
                                ["roles"],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(3),
                        ),
                    },
                ),
            ]
        )


class PlayerDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> ListDisplay:
        return dp.ListDisplay(fields=PERSON_FIELDS + PLAYER_FIELDS)

    def get_instance_display(self) -> Display:
        return Display(
            navigation_type=NavigationType.PAGE,
            pages=[
                Page(
                    title=_("Person"),
                    layouts={
                        default(): Layout(
                            grid_template_areas=[
                                ["profile_image", ".", "."],
                                ["first_name", "last_name", "roles"],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(5),
                        ),
                        lte(800): Layout(
                            grid_template_areas=[
                                ["profile_image", "."],
                                ["first_name", "last_name"],
                                ["roles", "."],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(3),
                        ),
                        lte(550): Layout(
                            grid_template_areas=[
                                ["first_name"],
                                ["last_name"],
                                ["roles"],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(3),
                        ),
                    },
                ),
                Page(
                    title=_("Player"),
                    layouts={
                        default(): Layout(
                            grid_template_areas=[
                                ["position", "current_team"],
                                ["former_teams", "transfer_value"],
                                ["player_strength", "game_activity"],
                                ["is_active", "is_injured"],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(5),
                        ),
                        lte(650): Layout(
                            grid_template_areas=[
                                ["position"],
                                ["current_team"],
                                ["former_teams"],
                                ["transfer_value"],
                                ["player_strength"],
                                ["game_activity"],
                                ["is_active"],
                                ["is_injured"],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                        ),
                    },
                ),
            ],
        )


class SportPersonToolTipDisplayConfig(DisplayViewConfig):
    def get_instance_display(self) -> Display | None:
        return Display(
            navigation_type=NavigationType.PAGE,
            pages=[
                Page(
                    title=_("Person"),
                    layouts={
                        default(): Layout(
                            grid_template_areas=[
                                ["profile_image", "profile_image"],
                                ["first_name", "last_name"],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(5),
                        ),
                    },
                ),
            ],
        )


class TreeViewPlayerDisplay(DisplayViewConfig):
    def get_list_display(self) -> ListDisplay:
        return dp.ListDisplay(fields=[dp.Field(key="computed_str", label=_("Name"))])


class PlayerTeamDisplayConfig(PlayerDisplayConfig):
    def get_list_display(self) -> ListDisplay:
        player_fields = PLAYER_FIELDS.copy()
        player_fields.pop(1)
        return dp.ListDisplay(fields=PERSON_FIELDS + player_fields)

    def get_instance_display(self) -> Display:
        if "pk" in self.view.kwargs:
            return super().get_instance_display()

        return Display(
            navigation_type=NavigationType.PAGE,
            pages=[
                Page(
                    title=_("Person"),
                    layouts={
                        default(): Layout(
                            grid_template_areas=[
                                ["first_name", "last_name", "roles"],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(5),
                        ),
                        lte(800): Layout(
                            grid_template_areas=[
                                ["first_name", "last_name"],
                                ["roles", "."],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(3),
                        ),
                        lte(550): Layout(
                            grid_template_areas=[
                                ["first_name"],
                                ["last_name"],
                                ["roles"],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(3),
                        ),
                    },
                ),
                Page(
                    title=_("Player"),
                    layouts={
                        default(): Layout(
                            grid_template_areas=[
                                ["position", "former_teams", "transfer_value"],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(5),
                        ),
                        lte(800): Layout(
                            grid_template_areas=[
                                ["position", "former_teams"],
                                ["transfer_value", "."],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(3),
                        ),
                        lte(550): Layout(
                            grid_template_areas=[
                                ["position"],
                                ["former_teams"],
                                ["transfer_value"],
                            ],
                            grid_auto_columns="minmax(min-content, 1fr)",
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(3),
                        ),
                    },
                ),
            ],
        )
