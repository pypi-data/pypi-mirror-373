from django.utils.translation import gettext as _

from wbcore.metadata.configs.titles import TitleViewConfig


class RoleTitleConfig(TitleViewConfig):
    def get_list_title(self) -> str:
        return _("Roles")

    def get_create_title(self) -> str:
        return _("Create Role")

    def get_instance_title(self) -> str:
        return _("Role")
