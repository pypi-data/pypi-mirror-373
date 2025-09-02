from django.utils.translation import gettext as _

from wbcore.metadata.configs.titles import TitleViewConfig


class TransitionTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return _("Transitions")

    def get_create_title(self):
        return _("Create Transition")

    def get_instance_title(self):
        return _("Transition")
