from django.utils.translation import gettext as _

from wbcore.contrib.example_app.models import Sport
from wbcore.metadata.configs.titles import TitleViewConfig


class LeagueTitleConfig(TitleViewConfig):
    def get_list_title(self) -> str:
        return _("Leagues")

    def get_create_title(self) -> str:
        return _("Create League")

    def get_instance_title(self) -> str:
        return _("League")


class LeagueSportTitleConfig(LeagueTitleConfig):
    def get_create_title(self) -> str:
        if sport_id := self.view.kwargs.get("sport_id"):
            try:
                return _("Create {} League").format(Sport.objects.get(id=sport_id).name)
            except Sport.DoesNotExist:
                pass
        return super().get_create_title()
