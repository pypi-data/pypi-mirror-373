from django.utils.translation import gettext as _
from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences.types import StringPreference

wbcore_section = Section("wbcore")


@global_preferences_registry.register
class DefaultEmptyImagePlaceholderPreference(StringPreference):
    section = wbcore_section
    name = "default_empty_image_placeholder"
    default = "https://stainly-cdn.fra1.cdn.digitaloceanspaces.com/icons/empty_image_placeholder.png"

    verbose_name = _("Default Empty Image Placeholder")
    help_text = _("Default empty image placeholder URL")
