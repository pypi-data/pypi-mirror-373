from django.utils.translation import gettext as _

from wbcore.metadata.configs.titles import TitleViewConfig


class CustomerStatusTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return _("Customer Statuses")

    def get_create_title(self):
        return _("New Customer Status")

    def get_instance_title(self):
        return _("Customer Status")


class PositionTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return _("Company Positions")

    def get_create_title(self):
        return _("New Company Position")

    def get_instance_title(self):
        return _("Company Position")


class CompanyTypeTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return _("Company Types")

    def get_create_title(self):
        return _("New Company Type")

    def get_instance_title(self):
        return _("Company Type")


class SpecializationTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return _("Specializations")

    def get_create_title(self):
        return _("New Specialization")

    def get_instance_title(self):
        return _("Specialization")
