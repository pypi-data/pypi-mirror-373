from django.utils.translation import gettext as _

from wbcore.metadata.configs.titles import TitleViewConfig


class StepTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return _("Steps")

    def get_create_title(self):
        return _("Create Step")

    def get_instance_title(self):
        return _("Step")


class UserStepTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return _("User Steps")

    def get_create_title(self):
        return _("Create User Step")

    def get_instance_title(self):
        return _("User Step")


class DecisionStepTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return _("Decision Steps")

    def get_create_title(self):
        return _("Create Decision Step")

    def get_instance_title(self):
        return _("Decision Step")


class StartStepTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return _("Start Steps")

    def get_create_title(self):
        return _("Create Start Step")

    def get_instance_title(self):
        return _("Start Step")


class SplitStepTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return _("Split Steps")

    def get_create_title(self):
        return _("Create Split Step")

    def get_instance_title(self):
        return _("Split Step")


class JoinStepTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return _("Join Steps")

    def get_create_title(self):
        return _("Create Join Step")

    def get_instance_title(self):
        return _("Join Step")


class ScriptStepTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return _("Script Steps")

    def get_create_title(self):
        return _("Create Script Step")

    def get_instance_title(self):
        return _("Script Step")


class EmailStepTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return _("Email Steps")

    def get_create_title(self):
        return _("Create Email Step")

    def get_instance_title(self):
        return _("Email Step")


class FinishStepTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return _("Finish Steps")

    def get_create_title(self):
        return _("Create Finish Step")

    def get_instance_title(self):
        return _("Finish Step")
