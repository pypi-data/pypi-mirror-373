from wbcore.serializers.fields.text import CharField
from wbcore.serializers.fields.types import WBCoreType

from .icons import WBIcon


class IconSelectField(CharField):
    field_type = WBCoreType.ICON.value

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_representation(self, value):
        # Try to get its "icon" representation. If the field is not supported, we simply returns the value (This allow custom and hardcoded icon)
        try:
            return WBIcon[value].icon
        except KeyError:
            return value
