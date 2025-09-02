from django.utils.translation import gettext as _

from wbcore.contrib.example_app.models import Stadium
from wbcore.metadata.configs.titles import TitleViewConfig


class TeamTitleConfig(TitleViewConfig):
    def get_list_title(self) -> str:
        return _("Teams")

    def get_create_title(self) -> str:
        return _("Create Team")

    def get_instance_title(self) -> str:
        return _("Team")


class TeamStadiumTitleConfig(TeamTitleConfig):
    def get_create_title(self) -> str:
        if stadium_id := self.view.kwargs.get("stadium_id"):
            try:
                return _("Create Team In {}").format(Stadium.objects.get(id=stadium_id).name)
            except Stadium.DoesNotExist:
                pass
        return super().get_create_title()
