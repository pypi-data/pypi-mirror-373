from rest_framework import serializers

from .mixins import WBCoreSerializerFieldMixin
from .types import WBCoreType


class PrimaryKeyField(WBCoreSerializerFieldMixin, serializers.IntegerField):
    field_type = WBCoreType.PRIMARY_KEY.value

    def __init__(self, *args, **kwargs):
        kwargs["read_only"] = True
        kwargs["required"] = False
        super().__init__(*args, **kwargs)


class PrimaryKeyCharField(WBCoreSerializerFieldMixin, serializers.CharField):
    field_type = WBCoreType.PRIMARY_KEY.value

    def __init__(self, *args, **kwargs):
        kwargs["read_only"] = True
        kwargs["required"] = False
        super().__init__(*args, **kwargs)
