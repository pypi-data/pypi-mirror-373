from django.utils.translation import gettext as _

from wbcore.metadata.configs.titles import TitleViewConfig


class TeamResultsTitleConfig(TitleViewConfig):
    def get_list_title(self) -> str:
        return _("Team Results")


class TeamResultsLeagueTitleConfig(TitleViewConfig):
    def get_list_title(self) -> str:
        return _("Table")
