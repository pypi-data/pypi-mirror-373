from rest_framework import serializers

from .mixins import WBCoreSerializerFieldMixin
from .types import WBCoreType


class ImageField(WBCoreSerializerFieldMixin, serializers.ImageField):
    field_type = WBCoreType.IMAGE.value


class UnsafeImageField(WBCoreSerializerFieldMixin, serializers.FileField):
    field_type = WBCoreType.IMAGE.value


class ImageURLField(WBCoreSerializerFieldMixin, serializers.URLField):
    field_type = WBCoreType.IMAGE.value


class FileField(WBCoreSerializerFieldMixin, serializers.FileField):
    field_type = WBCoreType.FILE.value
