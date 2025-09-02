from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences.types import StringPreference

io = Section("io")


@global_preferences_registry.register
class AdministratorMailsPreference(StringPreference):
    section = io
    name = "administrator_mails"
    default = ""

    verbose_name = "Administrator mails"
    help_text = "The mails (as comma separated string) of the person allow to send directly to the mail backend"
