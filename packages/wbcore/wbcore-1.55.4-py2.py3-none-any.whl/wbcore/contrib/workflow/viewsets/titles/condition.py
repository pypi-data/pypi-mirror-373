from django.utils.translation import gettext as _

from wbcore.metadata.configs.titles import TitleViewConfig


class ConditionTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return _("Conditions")

    def get_create_title(self):
        return _("Create Condition")

    def get_instance_title(self):
        return _("Condition")
