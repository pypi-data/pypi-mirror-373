from django.utils.translation import gettext_lazy as _
from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences.types import IntegerPreference

authentication = Section("authentication")


@global_preferences_registry.register
class HoursBeforeDeletingUnregisteredAccountPreference(IntegerPreference):
    section = authentication
    name = "hours_before_deleting_unregistered_account"
    default = 48

    verbose_name = _("Immunity Period")
    help_text = _("Set the maximum number of hours a user can remain without registration")


@global_preferences_registry.register
class DefaultTokenValidityInHoursPreference(IntegerPreference):
    section = authentication
    name = "default_token_validity_in_hours"
    default = 24

    verbose_name = _("Default Token Validity (in Hours)")
    help_text = _("If not specified, a newly created token will be valid for that amount of hours")
