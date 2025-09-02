from django.utils.translation import gettext as _

from wbcore.metadata.configs.titles import TitleViewConfig


class ProcessTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return _("Processes")

    def get_instance_title(self):
        return _("Process")


class ProcessStepTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return _("Process Steps")

    def get_instance_title(self):
        return _("Process Step")


class AssignedProcessStepTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return _("Assigned Process Steps")

    def get_instance_title(self):
        return _("Assigned Process Step")
