from collections import OrderedDict

from django.utils.translation import gettext as _
from rest_framework.reverse import NoReverseMatch, reverse

from wbcore import serializers
from wbcore.contrib.agenda.models import CalendarItem


class CalendarItemRepresentationSerializer(serializers.RepresentationSerializer):
    _detail = serializers.SerializerMethodField()

    def get__detail(self, obj) -> str:
        try:
            return reverse(f"{obj.endpoint_basename}-detail", args=[obj.id], request=self.context["request"])
        except (NoReverseMatch, KeyError):
            return ""

    class Meta:
        model = CalendarItem
        fields = (
            "id",
            "title",
            "_detail",
        )


class CalendarItemModelSerializer(serializers.ModelSerializer):
    activity_id = serializers.CharField()
    endpoint = serializers.SerializerMethodField()
    is_confidential = serializers.BooleanField(default=False, read_only=True)
    is_draggable = serializers.BooleanField(default=False, read_only=True)
    is_private = serializers.BooleanField(default=False, read_only=True)

    def get_endpoint(self, obj):
        try:
            return reverse(f"{obj.endpoint_basename}-detail", args=[obj.id], request=self.context["request"])
        except (NoReverseMatch, KeyError):
            return ""

    def to_representation(self, instance: CalendarItem) -> OrderedDict:
        representation = super().to_representation(instance)

        is_private: bool
        if (is_private := representation.get("is_private", False)) or representation.get("is_confidential", False):
            item_type = instance.item_type.split(".")[1] if instance.item_type else _("Item")
            representation["title"] = (
                _("Private {}").format(item_type) if is_private else _("Confidential {}").format(item_type)
            )
            if not is_private:
                representation["_entities"] = ""
                representation["entities"] = ""
                representation["entity_list"] = ""

        return representation

    class Meta:
        model = CalendarItem
        read_only_fields = ("is_cancelled",)
        fields = (
            "id",
            "title",
            "entities",
            "all_day",
            "activity_id",
            "color",
            "endpoint",
            "entity_list",
            "icon",
            "is_cancelled",
            "is_confidential",
            "is_draggable",
            "is_private",
            "period",
            "is_deletable",
        )
        read_only_fields = ("endpoint",)
