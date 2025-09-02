from django.urls import include, path

from wbcore.contrib.example_app.views import embedded_view_example
from wbcore.routers import WBCoreRouter

from . import viewsets

router = WBCoreRouter()

router.register(r"league", viewsets.LeagueModelViewSet, basename="league")
router.register(r"player", viewsets.PlayerModelViewSet, basename="player")
router.register(r"treeviewplayer", viewsets.TreeViewPlayerModelViewSet, basename="treeviewplayer")
router.register(r"person", viewsets.SportPersonModelViewSet, basename="person")
router.register(r"persontooltip", viewsets.SportPersonToolTipViewset, basename="persontooltip")
router.register(r"stadium", viewsets.StadiumModelViewSet, basename="stadium")
router.register(r"season", viewsets.SeasonModelViewSet, basename="season")
router.register(r"team", viewsets.TeamModelViewSet, basename="team")
router.register(r"sport", viewsets.SportModelViewSet, basename="sport")
router.register(r"role", viewsets.RoleModelViewSet, basename="role")
router.register(r"match", viewsets.MatchModelViewSet, basename="match")
router.register(r"event", viewsets.EventModelViewSet, basename="event")
router.register(r"eventtype", viewsets.EventTypeModelViewSet, basename="eventtype")
router.register(r"teamresults", viewsets.TeamResultsModelViewSet, basename="teamresults")

router.register(r"personrepresentation", viewsets.SportPersonRepresentationViewSet, basename="personrepresentation")
router.register(r"stadiumrepresentation", viewsets.StadiumRepresentationViewSet, basename="stadiumrepresentation")
router.register(r"seasonrepresentation", viewsets.SeasonRepresentationViewSet, basename="seasonrepresentation")
router.register(r"leaguerepresentation", viewsets.LeagueRepresentationViewSet, basename="leaguerepresentation")
router.register(r"sportrepresentation", viewsets.SportRepresentationViewSet, basename="sportrepresentation")
router.register(r"teamrepresentation", viewsets.TeamRepresentationViewSet, basename="teamrepresentation")
router.register(r"rolerepresentation", viewsets.RoleRepresentationViewSet, basename="rolerepresentation")
router.register(r"playerrepresentation", viewsets.PlayerRepresentationViewSet, basename="playerrepresentation")
router.register(r"matchrepresentation", viewsets.MatchRepresentationViewSet, basename="matchrepresentation")
router.register(r"eventrepresentation", viewsets.EventRepresentationViewSet, basename="eventrepresentation")
router.register(
    r"eventtyperepresentation", viewsets.EventTypeRepresentationViewSet, basename="eventtyperepresentation"
)
router.register(
    r"teamresultsrepresentation", viewsets.TeamResultsRepresentationViewSet, basename="teamresultsrepresentation"
)

stadium_router = WBCoreRouter()
stadium_router.register(r"team-stadium", viewsets.TeamStadiumModelViewSet, basename="team-stadium")
stadium_router.register(r"match-stadium", viewsets.MatchStadiumModelViewSet, basename="match-stadium")

sport_router = WBCoreRouter()
sport_router.register(r"league-sport", viewsets.LeagueSportModelViewSet, basename="league-sport")
sport_router.register(r"eventtype-sport", viewsets.EventTypeSportModelViewSet, basename="eventtype-sport")

team_router = WBCoreRouter()
team_router.register(r"player-team", viewsets.PlayerTeamModelViewSet, basename="player-team")
team_router.register(r"match-team", viewsets.MatchModelViewSet, basename="match-team")

match_router = WBCoreRouter()
match_router.register(r"event-match", viewsets.EventMatchModelViewSet, basename="event-match")

league_router = WBCoreRouter()
league_router.register(r"match-league", viewsets.MatchLeagueModelViewSet, basename="match-league")
league_router.register(r"teamresults-league", viewsets.TeamResultsLeagueModelViewSet, basename="teamresults-league")

league_event_type_router = WBCoreRouter()
league_event_type_router.register(
    r"league-player-statistics", viewsets.LeaguePlayerStatisticsModelViewSet, basename="league-player-statistics"
)
league_event_type_router.register(
    r"league-team-statistics", viewsets.LeagueTeamStatisticsModelViewSet, basename="league-team-statistics"
)

player_router = WBCoreRouter()
player_router.register(r"player-statistics", viewsets.PlayerStatisticsChartModelViewSet, basename="player-statistics")

urlpatterns = [
    path("", include(router.urls)),
    path("stadium/<int:stadium_id>/", include(stadium_router.urls)),
    path("sport/<int:sport_id>/", include(sport_router.urls)),
    path("team/<int:team_id>/", include(team_router.urls)),
    path("match/<int:match_id>/", include(match_router.urls)),
    path("league/<int:league_id>/", include(league_router.urls)),
    path("league/<int:league_id>/event_type/<int:event_type_id>/", include(league_event_type_router.urls)),
    path("player/<int:player_id>/", include(player_router.urls)),
    path("embedded/", embedded_view_example),
]
