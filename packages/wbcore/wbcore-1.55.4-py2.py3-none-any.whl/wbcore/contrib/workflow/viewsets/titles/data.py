from django.utils.translation import gettext as _

from wbcore.metadata.configs.titles import TitleViewConfig


class DataTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return _("Data")

    def get_create_title(self):
        return _("Create Data")

    def get_instance_title(self):
        return _("Data")
