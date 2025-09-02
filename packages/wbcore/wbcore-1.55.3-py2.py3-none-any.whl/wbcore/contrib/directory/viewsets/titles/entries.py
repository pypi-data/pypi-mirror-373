from django.utils.translation import gettext as _

from wbcore.metadata.configs.titles import TitleViewConfig


class PersonModelTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return _("Persons")

    def get_instance_title(self):
        return _("Person: {{first_name}} {{last_name}}")

    def get_create_title(self):
        return _("New Person")


class CompanyModelTitleConfig(TitleViewConfig):
    def get_instance_title(self):
        return _("Company: {{name}}")

    def get_list_title(self):
        return _("Companies")

    def get_create_title(self):
        return _("New Company")


class UserIsManagerTitleConfig(TitleViewConfig):
    def get_list_title(self) -> str:
        return _("Your Clients/Prospects/Contacts")
