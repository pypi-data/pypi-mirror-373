import pycountry
from django.forms import ValidationError
from django.utils.translation import gettext as _
from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences.types import IntegerPreference, StringPreference

from .models.entries import Company

general = Section("directory")


@global_preferences_registry.register
class MainCompanyPreference(IntegerPreference):
    section = general
    name = "main_company"
    default = 0

    verbose_name = _("Main Workbench Company")
    help_text = _(
        'The main company of the Workbench. All employees of this company are considered to have "employee" status and have more permissions than other users.'
    )

    def validate(self, value):
        if not Company.objects.filter(id=value).exists():
            raise ValidationError(_("Please select a valid company."))


@global_preferences_registry.register
class CountryCodePreference(StringPreference):
    section = general
    name = "main_country_code"
    default = "US"
    verbose_name = _("Main Country Code")
    help_text = _(
        "Determines the country code currently used exclusively for parsing of phone numbers. Should be the country where the phone number is being dialled from."
    )

    def validate(self, value):
        if not pycountry.countries.get(alpha_2=value):
            raise ValidationError(_("Only exact alpha_2 country codes (e.g. DE, CH) allowed."))


@global_preferences_registry.register
class PersonSalutationStringPreference(StringPreference):
    section = general
    name = "person_salutation"
    default = _("Dear {0} {1}")

    verbose_name = _("Person Salutation")
    help_text = _("Salutation that can be used in mails for a person")


@global_preferences_registry.register
class CompanySalutationStringPreference(StringPreference):
    section = general
    name = "company_salutation"
    default = _("To everyone from {0}")

    verbose_name = _("Company Salutation")
    help_text = _("Salutation that can be used in mails for a company")
