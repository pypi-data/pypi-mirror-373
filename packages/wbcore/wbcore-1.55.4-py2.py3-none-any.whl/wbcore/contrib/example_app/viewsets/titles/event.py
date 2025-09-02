from django.utils.translation import gettext as _

from wbcore.contrib.example_app.models import Player, Sport
from wbcore.metadata.configs.titles import TitleViewConfig


class EventTitleConfig(TitleViewConfig):
    def get_list_title(self) -> str:
        return _("Events")

    def get_create_title(self) -> str:
        return _("Create Event")

    def get_instance_title(self) -> str:
        return _("Event")


class PlayerStatisticsChartTitleConfig(TitleViewConfig):
    def get_list_title(self) -> str:
        player_name = Player.objects.get(id=self.view.kwargs["player_id"])
        return _("Player Statistics {}").format(player_name.computed_str)


class EventTypeTitleConfig(TitleViewConfig):
    def get_list_title(self) -> str:
        return _("Event Types")

    def get_create_title(self) -> str:
        return _("Create Event Type")

    def get_instance_title(self) -> str:
        return _("Event Type")


class EventTypeSportTitleConfig(EventTypeTitleConfig):
    def get_create_title(self) -> str:
        if sport_id := self.view.kwargs.get("sport_id"):
            try:
                return _("Create {} Event Type").format(Sport.objects.get(id=sport_id).name)
            except Sport.DoesNotExist:
                pass
        return super().get_create_title()
