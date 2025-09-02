from rest_framework.reverse import reverse

from wbcore import serializers
from wbcore.contrib.example_app.models import Sport


class SportModelSerializer(serializers.ModelSerializer):
    @serializers.register_only_instance_resource()
    def leagues_inline(self, instance: Sport, request, user, view, **kwargs) -> dict[str, str]:
        if not self.context.get("request"):
            return {}
        return {
            "existing_leagues": reverse(
                "example_app:league-sport-list", args=[instance.pk], request=self.context["request"]
            )
        }

    @serializers.register_only_instance_resource()
    def event_types_inline(self, instance: Sport, request, user, view, **kwargs) -> dict[str, str]:
        if not self.context.get("request"):
            return {}
        return {
            "associated_event_types": reverse(
                "example_app:eventtype-sport-list", args=[instance.pk], request=self.context["request"]
            )
        }

    class Meta:
        model = Sport
        fields = "__all__"


class SportRepresentationSerializer(serializers.RepresentationSerializer):
    _detail = serializers.HyperlinkField(reverse_name="example_app:sport-detail")

    class Meta:
        model = Sport
        fields = ("id", "name", "_detail")
