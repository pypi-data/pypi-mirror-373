from datetime import date
from enum import Enum

from django.forms import ValidationError
from django.utils import timezone
from django.utils.translation import gettext as _
from rest_framework.reverse import reverse

from wbcore import serializers
from wbcore.contrib.example_app.models import League, Sport
from wbcore.contrib.example_app.serializers import (
    SportPersonRepresentationSerializer,
    SportRepresentationSerializer,
)
from wbcore.contrib.example_app.utils import get_event_types_for_league
from wbcore.contrib.geography.serializers import GeographyRepresentationSerializer


class LeagueErrorMessages(Enum):
    league_exists = _("A league with this name already exists for this type of sport.")
    wrong_established_date = _("The founding date must be in the past.")


class LeagueModelSerializer(serializers.ModelSerializer):
    _commissioner = SportPersonRepresentationSerializer(source="commissioner")
    _country = GeographyRepresentationSerializer(filter_params={"level": 1}, source="country")
    _sport = SportRepresentationSerializer(source="sport")

    def validate(self, data: dict) -> dict:
        name: str | None = data.get("name", self.instance.name if self.instance else None)
        sport: Sport | None = data.get("sport", self.instance.sport if self.instance else None)
        established_date: date | None = data.get("established_date", None)
        if name and sport:
            league = League.objects.filter(name=name, sport=sport)
            if obj := self.instance:
                league = league.exclude(id=obj.id)
            if league.exists():
                raise ValidationError({"name": LeagueErrorMessages.league_exists.value})
        if established_date and established_date > timezone.now().date():
            raise ValidationError({"established_date": LeagueErrorMessages.wrong_established_date.value})
        return super().validate(data)

    @serializers.register_only_instance_resource()
    def matches_inline(self, instance: League, request, user, view, **kwargs) -> dict[str, str]:
        if not self.context.get("request"):
            return {}
        return {
            "recent_matches": reverse(
                "example_app:match-league-list", args=[instance.pk], request=self.context["request"]
            )
        }

    @serializers.register_only_instance_resource()
    def table_inline(self, instance: League, request, user, view, **kwargs) -> dict[str, str]:
        if not self.context.get("request"):
            return {}
        return {
            "table": reverse(
                "example_app:teamresults-league-list", args=[instance.pk], request=self.context["request"]
            )
        }

    @serializers.register_only_instance_resource()
    def league_statistics_inline(self, instance: League, request, user, view, **kwargs) -> dict[str, str]:
        if not self.context.get("request"):
            return {}
        statistics_inlines = {}
        for event_type in get_event_types_for_league(instance.pk):
            statistics_inlines.update(
                {
                    f"player_{event_type['slugified_name']}": reverse(
                        "example_app:league-player-statistics-list",
                        args=[instance.pk, event_type["id"]],
                        request=self.context["request"],
                    ),
                    f"team_{event_type['slugified_name']}": reverse(
                        "example_app:league-team-statistics-list",
                        args=[instance.pk, event_type["id"]],
                        request=self.context["request"],
                    ),
                },
            )

        return statistics_inlines

    class Meta:
        model = League
        fields = (
            "id",
            "name",
            "sport",
            "_sport",
            "country",
            "_country",
            "points_per_win",
            "points_per_draw",
            "points_per_loss",
            "established_date",
            "commissioner",
            "_commissioner",
            "website",
            "_additional_resources",
        )
        optional_fields = ("teams",)


class LeagueRepresentationSerializer(serializers.RepresentationSerializer):
    _detail = serializers.HyperlinkField(reverse_name="example_app:league-detail")

    class Meta:
        model = League
        fields = ("id", "name", "computed_str", "_detail")
