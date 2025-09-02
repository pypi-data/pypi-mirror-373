from enum import Enum

from django.forms import ValidationError
from django.utils.translation import gettext as _

from wbcore import serializers
from wbcore.contrib.example_app.models import League, Team, TeamResults
from wbcore.contrib.example_app.serializers import (
    LeagueRepresentationSerializer,
    TeamRepresentationSerializer,
)


class ResultErrorMessages(Enum):
    result_exists = _("Results for this team and league already exist.")


class TeamResultsModelSerializer(serializers.ModelSerializer):
    _team = TeamRepresentationSerializer(source="team")
    _league = LeagueRepresentationSerializer(source="league")
    games_played = serializers.IntegerField(label=_("Games"), default=0)

    def validate(self, data: dict) -> dict:
        team: Team | None = data.get("team", None)
        league: League | None = data.get("league", None)
        if team and league:
            team_results = TeamResults.objects.filter(team=team, league=league)
            if obj := self.instance:
                team_results = team_results.exclude(id=obj.id)
            if team_results.exists():
                raise ValidationError({"team": ResultErrorMessages.result_exists.value})
        return super().validate(data)

    class Meta:
        model = TeamResults
        fields = "__all__"


class TeamResultsRepresentationSerializer(serializers.RepresentationSerializer):
    _detail = serializers.HyperlinkField(reverse_name="example_app:teamresults-detail")

    class Meta:
        model = TeamResults
        fields = ("id", "team", "league", "_detail")
