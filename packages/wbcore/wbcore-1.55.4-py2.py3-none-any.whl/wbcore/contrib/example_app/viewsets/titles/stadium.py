from django.utils.translation import gettext as _

from wbcore.metadata.configs.titles import TitleViewConfig


class StadiumTitleConfig(TitleViewConfig):
    def get_list_title(self) -> str:
        return _("Stadiums")

    def get_create_title(self) -> str:
        return _("Create Stadium")

    def get_instance_title(self) -> str:
        return _("Stadium")
