from django.utils.translation import gettext as _

from wbcore.metadata.configs.titles import TitleViewConfig


class ShareableLinkModelTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return _("Shareable Links")

    def get_instance_title(self):
        return _("Shareable Link")

    def get_create_title(self):
        return _("New Shareable Link")
