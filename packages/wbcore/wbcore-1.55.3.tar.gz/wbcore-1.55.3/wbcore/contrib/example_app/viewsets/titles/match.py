from django.utils.translation import gettext as _

from wbcore.contrib.example_app.models import League, Stadium
from wbcore.metadata.configs.titles import TitleViewConfig


class MatchTitleConfig(TitleViewConfig):
    def get_list_title(self) -> str:
        return _("Matches")

    def get_create_title(self) -> str:
        return _("Create Match")

    def get_instance_title(self) -> str:
        return _("Match")


class MatchStadiumTitleConfig(MatchTitleConfig):
    def get_create_title(self) -> str:
        if stadium_id := self.view.kwargs.get("stadium_id"):
            try:
                return _("Create Match In {}").format(Stadium.objects.get(id=stadium_id).name)
            except Stadium.DoesNotExist:
                pass
        return super().get_create_title()


class MatchLeagueTitleConfig(MatchTitleConfig):
    def get_create_title(self) -> str:
        if league_id := self.view.kwargs.get("league_id"):
            try:
                return _("Create Match In {}").format(League.objects.get(id=league_id).name)
            except League.DoesNotExist:
                pass
        return super().get_create_title()
