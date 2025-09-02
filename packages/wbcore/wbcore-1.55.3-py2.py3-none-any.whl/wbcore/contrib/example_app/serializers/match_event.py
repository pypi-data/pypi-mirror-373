from datetime import datetime
from enum import Enum

from django.db.models import Q
from django.forms import ValidationError
from django.utils import timezone
from django.utils.translation import gettext as _
from rest_framework.reverse import reverse

from wbcore import serializers
from wbcore.contrib.example_app.models import (
    Event,
    EventType,
    League,
    Match,
    Player,
    Role,
    Sport,
    SportPerson,
    Team,
)
from wbcore.contrib.example_app.serializers import (
    LeagueRepresentationSerializer,
    SportPersonRepresentationSerializer,
    SportRepresentationSerializer,
    StadiumRepresentationSerializer,
    TeamRepresentationSerializer,
)
from wbcore.enums import RequestType
from wbcore.metadata.configs.buttons import ActionButton
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    create_simple_display,
)


class MatchErrorMessages(Enum):
    same_teams = _("Team cannot play against itself.")
    same_match = _("A match between these teams at this time already exists.")
    wrong_sport = _("League doesn't match the specified sport.")


class EventTypeErrorMessages(Enum):
    same_name = _("An event type with this name already exists for this sport.")


class EventErrorMessages(Enum):
    same_event = _("This event already exists.")
    wrong_duration = _("Event outside of match duration.")
    wrong_event_type = _("Please select a {} event type.")


class MatchModelSerializer(serializers.ModelSerializer):
    _home = TeamRepresentationSerializer(
        source="home",
        optional_get_parameters={"away": "opponent"},
    )
    _away = TeamRepresentationSerializer(
        source="away",
        optional_get_parameters={"home": "opponent"},
    )
    _league = LeagueRepresentationSerializer(
        source="league",
        optional_get_parameters={"sport": "sport"},
        depends_on=[{"field": "sport", "options": {}}],
    )
    _stadium = StadiumRepresentationSerializer(source="stadium")
    _referee = SportPersonRepresentationSerializer(
        source="referee",
        filter_params=lambda request: {"roles": (Role.objects.get(title="Referee").pk)}
        if Role.objects.filter(title="Referee").exists()
        else {},
    )

    _sport = SportRepresentationSerializer(source="sport")

    def validate(self, data: dict) -> dict:
        home: Team | None = data.get("home", self.instance.home if self.instance else None)
        away: Team | None = data.get("away", self.instance.away if self.instance else None)
        date_time: datetime | None = data.get("date_time", self.instance.date_time if self.instance else None)
        sport: Sport | None = data.get("sport", self.instance.sport if self.instance else None)
        if "league" in data:
            league: League = data["league"]
        else:
            league: League | None = self.instance.league if self.instance else None

        if home and away:
            if home.pk == away.pk:
                raise ValidationError({"away": MatchErrorMessages.same_teams.value})
            if date_time:
                match = Match.objects.filter(away=away, date_time=date_time, home=home)
                if obj := self.instance:
                    match = match.exclude(id=obj.pk)
                if match.exists():
                    raise ValidationError({"home": MatchErrorMessages.same_match.value})

        if league and sport:
            if league.sport.pk != sport.pk:
                raise ValidationError({"league": MatchErrorMessages.wrong_sport.value})
        return super().validate(data)

    @serializers.register_dynamic_button()
    def event_type_buttons(self, instance: Match, request, user) -> list:
        def get_current_match_minute() -> int | None:
            """Returns the current match minute based on the match's start time if inside the match duration boundaries

            Returns:
                int|None: The current minute
            """
            minutes_since_match_start = (timezone.now() - instance.date_time).total_seconds() / 60
            if 0 < minutes_since_match_start < instance.sport.match_duration:
                return int(minutes_since_match_start)
            return None

        class EventButtonSerializer(serializers.Serializer):
            _person = SportPersonRepresentationSerializer(source="person", filter_params={"match": instance.pk})
            person = serializers.PrimaryKeyRelatedField(
                label=_("Person"),
                queryset=SportPerson.objects.filter(
                    Q(coached_team__home_matches=instance)
                    | Q(coached_team__away_matches=instance)
                    | Q(refereed_matches=instance)
                    | Q(
                        id__in=Player.objects.filter(
                            Q(current_team__home_matches=instance) | Q(current_team__away_matches=instance)
                        ).values("id")
                    )
                ).distinct(),
            )
            minute = serializers.IntegerField(label=_("Minute"), default=get_current_match_minute)

            def validate(self, data: dict) -> dict:
                match: Match | None = data.get("match", self.instance.match if self.instance else None)
                minute: int | None = data.get("minute", self.instance.minute if self.instance else None)

                if match and minute:
                    if (duration := match.sport.match_duration) < minute:
                        raise ValidationError(
                            {"minute": _("Event outside of match duration ({} min).").format(duration)}
                        )

                return super().validate(data)

        buttons = []
        if instance.status == Match.MatchStatus.ONGOING:
            for event_type in instance.sport.event_types.all():
                button = ActionButton(
                    method=RequestType.PATCH,
                    identifiers=("example_app:event-match",),
                    endpoint=f"{reverse('example_app:event-matchevent', args=[], request=request)}?event_type={event_type.pk}&match={instance.pk}",
                    action_label=event_type.name,
                    title=event_type.name,
                    label=event_type.name,
                    icon=event_type.icon,
                    description_fields="",
                    serializer=EventButtonSerializer,
                    instance_display=create_simple_display([["person"], ["minute"]]),
                )
                button.request = request

                buttons.append(button)
        return buttons

    @serializers.register_only_instance_resource()
    def events_inline(self, instance: Match, request, user, view, **kwargs) -> dict[str, str]:
        if not self.context.get("request"):
            return {}
        return {
            "event_list": reverse("example_app:event-match-list", args=[instance.pk], request=self.context["request"])
        }

    class Meta:
        model = Match
        fields = (
            "id",
            "home",
            "_home",
            "away",
            "_away",
            "sport",
            "_sport",
            "league",
            "_league",
            "date_time",
            "referee",
            "_referee",
            "stadium",
            "_stadium",
            "status",
            "score_home",
            "score_away",
            "computed_str",
            "_additional_resources",
            "_buttons",
        )


class ReadOnlyMatchModelSerializer(MatchModelSerializer):
    class Meta(MatchModelSerializer.Meta):
        read_only_fields = MatchModelSerializer.Meta.fields


class MatchRepresentationSerializer(serializers.RepresentationSerializer):
    _detail = serializers.HyperlinkField(reverse_name="example_app:match-detail")

    class Meta:
        model = Match
        fields = ("id", "computed_str", "_detail")


class EventTypeModelSerializer(serializers.ModelSerializer):
    _sport = SportRepresentationSerializer(source="sport")
    color = serializers.ColorPickerField(required=False)

    def validate(self, data: dict) -> dict:
        name: str | None = data.get("name", self.instance.name if self.instance else None)
        sport: Sport | None = data.get("sport", self.instance.sport if self.instance else None)

        if name and sport:
            event_type = EventType.objects.filter(name=name, sport=sport)
            if obj := self.instance:
                event_type = event_type.exclude(id=obj.pk)
            if event_type.exists():
                raise ValidationError({"name": EventTypeErrorMessages.same_name.value})
        return super().validate(data)

    class Meta:
        model = EventType
        fields = "__all__"


class EventTypeRepresentationSerializer(serializers.RepresentationSerializer):
    _detail = serializers.HyperlinkField(reverse_name="example_app:eventtype-detail")

    class Meta:
        model = EventType
        fields = ("id", "name", "_detail")


class EventModelSerializer(serializers.ModelSerializer):
    _person = SportPersonRepresentationSerializer(source="person")
    _match = MatchRepresentationSerializer(source="match")
    _event_type = EventTypeRepresentationSerializer(source="event_type")
    event_description = serializers.TextAreaField(required=False)

    def validate(self, data: dict) -> dict:
        person: SportPerson | None = data.get("person", self.instance.person if self.instance else None)
        match: Match | None = data.get("match", self.instance.match if self.instance else None)
        minute: int | None = data.get("minute", self.instance.minute if self.instance else None)
        event_type: EventType | None = data.get("event_type", self.instance.event_type if self.instance else None)

        if match:
            if minute:
                if match.sport.match_duration < minute:
                    raise ValidationError({"minute": EventErrorMessages.wrong_duration.value})
                if person and event_type:
                    event = Event.objects.filter(minute=minute, match=match, person=person, event_type=event_type)
                    if obj := self.instance:
                        event = event.exclude(id=obj.pk)
                    if event.exists():
                        raise ValidationError({"non_field_errors": EventErrorMessages.same_event.value})
            if event_type and match.sport.pk != event_type.sport.pk:
                raise ValidationError(
                    {"event_type": EventErrorMessages.wrong_event_type.value.format(match.sport.name)}
                )

        return super().validate(data)

    class Meta:
        model = Event
        fields = "__all__"


class LeaguePlayerStatisticsModelSerializer(serializers.ModelSerializer):
    person_id = serializers.IntegerField()
    person_name = serializers.CharField()
    count = serializers.IntegerField()
    id = serializers.PrimaryKeyCharField()

    class Meta:
        model = Event
        fields = ("id", "person_id", "person_name", "count")


class LeagueTeamStatisticsModelSerializer(serializers.ModelSerializer):
    team_id = serializers.IntegerField()
    team_name = serializers.CharField()
    count = serializers.IntegerField()
    id = serializers.PrimaryKeyCharField()

    class Meta:
        model = Event
        fields = (
            "id",
            "team_id",
            "count",
            "team_name",
        )


class EventRepresentationSerializer(serializers.RepresentationSerializer):
    _detail = serializers.HyperlinkField(reverse_name="example_app:event-detail")

    class Meta:
        model = Event
        fields = ("id", "event_type", "minute", "person", "_detail")
