import re

from django.core.exceptions import ValidationError
from django.db.models import CharField


def validate_color(color_string):
    """Hexadecimal validation."""
    if color_string is None:
        return color_string

    if not re.search(r"^#(?:[0-9a-fA-F]{3}){1,2}$", color_string):
        raise ValidationError("Please provide a valid hexadecimal color.")

    return color_string


class ColorField(CharField):
    description = "A field storing a hexadecimal color value"
    default_validators = [validate_color]

    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = 7
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["max_length"]
        return name, path, args, kwargs
