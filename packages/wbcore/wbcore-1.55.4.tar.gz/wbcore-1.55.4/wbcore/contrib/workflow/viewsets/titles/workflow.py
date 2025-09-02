from django.utils.translation import gettext as _

from wbcore.metadata.configs.titles import TitleViewConfig


class WorkflowTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return _("Workflows")

    def get_create_title(self):
        return _("Create Workflow")

    def get_instance_title(self):
        return _("Workflow")
