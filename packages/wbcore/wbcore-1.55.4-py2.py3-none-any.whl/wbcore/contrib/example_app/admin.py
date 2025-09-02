from django.contrib import admin

from wbcore.contrib.example_app.models import (
    Event,
    EventType,
    League,
    Match,
    Player,
    Role,
    Sport,
    SportPerson,
    Stadium,
    Team,
    TeamResults,
)


@admin.register(SportPerson)
class SportPersonAdmin(admin.ModelAdmin):
    search_fields = ("first_name", "last_name")
    list_display = ("id", "first_name", "last_name")
    raw_id_fields = ["roles"]


@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("id", "name", "rules", "match_duration")


@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = (
        "id",
        "name",
        "sport",
        "points_per_win",
        "points_per_draw",
        "points_per_loss",
        "country",
        "established_date",
        "commissioner",
        "website",
    )


@admin.register(Stadium)
class StadiumAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("id", "name", "city", "total_capacity", "seating_capacity", "standing_capacity")


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("id", "name", "city", "founded_date", "coach", "home_stadium")
    raw_id_fields = ["opponents"]


@admin.register(Player)
class PlayerAdmin(SportPersonAdmin):
    list_display = SportPersonAdmin.list_display + ("position", "current_team", "transfer_value")
    raw_id_fields = ["former_teams"]


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    search_fields = ("title",)
    list_display = ("id", "title")


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    search_fields = ("home", "away")
    list_display = (
        "id",
        "home",
        "away",
        "sport",
        "league",
        "date_time",
        "stadium",
        "status",
        "score_home",
        "score_away",
        "referee",
    )


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    search_fields = ("person", "event_type", "match")
    list_display = ("id", "person", "minute", "event_type", "match")


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    search_fields = ("name", "sport")
    list_display = ("id", "name", "sport", "points", "icon")


@admin.register(TeamResults)
class TeamResultsAdmin(admin.ModelAdmin):
    search_fields = ("team", "league")
    list_display = (
        "id",
        "team",
        "league",
        "points",
        "match_point_difference",
        "match_points_for",
        "match_points_against",
        "wins",
        "draws",
        "losses",
        "form",
    )
