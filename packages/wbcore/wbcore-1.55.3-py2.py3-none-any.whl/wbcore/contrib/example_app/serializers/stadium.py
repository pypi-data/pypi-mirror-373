from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework.reverse import reverse

from wbcore import serializers
from wbcore.contrib.example_app.models import Stadium
from wbcore.contrib.geography.serializers import GeographyRepresentationSerializer


class StadiumModelSerializer(serializers.ModelSerializer):
    _city = GeographyRepresentationSerializer(filter_params={"level": 3}, source="city")
    total_capacity = serializers.DecimalField(decimal_places=0, max_digits=10, read_only=True)
    guest_rating = serializers.EmojiRatingField()

    def validate_guest_rating(self, value):
        if value < 0 or value > 4:
            raise ValidationError(_("Guest rating must be between 0 and 4."))
        return value

    @serializers.register_only_instance_resource()
    def teams_inline(self, instance: Stadium, request, user, view, **kwargs) -> dict[str, str]:
        if not self.context.get("request"):
            return {}
        return {
            "teams_playing": reverse(
                "example_app:team-stadium-list", args=[instance.pk], request=self.context["request"]
            )
        }

    @serializers.register_only_instance_resource()
    def matches_inline(self, instance: Stadium, request, user, view, **kwargs) -> dict[str, str]:
        if not self.context.get("request"):
            return {}
        return {
            "recent_matches": reverse(
                "example_app:match-stadium-list", args=[instance.pk], request=self.context["request"]
            )
        }

    class Meta:
        model = Stadium
        fields = (
            "id",
            "name",
            "total_capacity",
            "seating_capacity",
            "standing_capacity",
            "guest_rating",
            "city",
            "_city",
        )


class StadiumRepresentationSerializer(serializers.RepresentationSerializer):
    _detail = serializers.HyperlinkField(reverse_name="example_app:stadium-detail")

    class Meta:
        model = Stadium
        fields = ("id", "name", "_detail")
