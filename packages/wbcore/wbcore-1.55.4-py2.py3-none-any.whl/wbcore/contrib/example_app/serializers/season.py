from django.forms import ValidationError
from django.utils import timezone

from wbcore import serializers
from wbcore.contrib.example_app.models import Season
from wbcore.contrib.example_app.serializers import (
    LeagueRepresentationSerializer,
    PlayerRepresentationSerializer,
    TeamRepresentationSerializer,
)


class SeasonModelSerializer(serializers.ModelSerializer):
    _league = LeagueRepresentationSerializer(source="league", many=False)
    _winner = TeamRepresentationSerializer(source="winner", many=False)
    _top_scorer = PlayerRepresentationSerializer(source="top_scorer")

    def validate(self, data):
        date_range = data.get("date_range", None)
        winner = data.get("winner", None)
        top_scorer = data.get("top_scorer", None)

        if date_range and date_range.upper > timezone.now().date():
            if winner:
                raise ValidationError({"winner": "You cannot choose a winner, when the season is not finished"})
            if top_scorer:
                raise ValidationError(
                    {"top_scorer": "You cannot choose a top scorer, when the season is not finished"}
                )

        return super().validate(data)

    class Meta:
        model = Season
        fields = [
            "id",
            "name",
            "league",
            "_league",
            "date_range",
            "file",
            "winner",
            "_winner",
            "top_scorer",
            "_top_scorer",
        ]


class SeasonRepresentationSerializer(serializers.RepresentationSerializer):
    _detail = serializers.HyperlinkField(reverse_name="example_app:season-detail")

    class Meta:
        model = Season
        fields = ("id", "name", "_detail")
