from django.utils.translation import gettext as _

from wbcore.metadata.configs.titles import TitleViewConfig


class BuildingTitleConfig(TitleViewConfig):
    def get_instance_title(self):
        return _("Building: {{name}}")

    def get_list_title(self):
        return _("Buildings")

    def get_create_title(self):
        return _("New Building")


class ConferenceRoomTitleConfig(TitleViewConfig):
    def get_instance_title(self):
        return _("Conference Room: {{name}}")

    def get_list_title(self):
        return _("Conference Rooms")

    def get_create_title(self):
        return _("New Conference Room")
