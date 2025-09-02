from django.utils.translation import gettext as _

from wbcore.contrib.example_app.models import Team
from wbcore.metadata.configs.titles import TitleViewConfig


class SportPersonTitleConfig(TitleViewConfig):
    def get_list_title(self) -> str:
        return _("Persons")

    def get_create_title(self) -> str:
        return _("Create Person")

    def get_instance_title(self) -> str:
        return _("Person")


class PlayerTitleConfig(TitleViewConfig):
    def get_list_title(self) -> str:
        return _("Players")

    def get_create_title(self) -> str:
        return _("Create Player")

    def get_instance_title(self) -> str:
        return _("Player")


class PlayerTeamTitleConfig(PlayerTitleConfig):
    def get_create_title(self) -> str:
        if team_id := self.view.kwargs.get("team_id"):
            try:
                return _("Create Player For {}").format(Team.objects.get(id=team_id).name)
            except Team.DoesNotExist:
                pass
        return super().get_create_title()
