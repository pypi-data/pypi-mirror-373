from django.utils.translation import gettext as _

from wbcore.metadata.configs.titles import TitleViewConfig


class SportTitleConfig(TitleViewConfig):
    def get_list_title(self) -> str:
        return _("Sports")

    def get_create_title(self) -> str:
        return _("Create Sport")

    def get_instance_title(self) -> str:
        return _("Sport")
