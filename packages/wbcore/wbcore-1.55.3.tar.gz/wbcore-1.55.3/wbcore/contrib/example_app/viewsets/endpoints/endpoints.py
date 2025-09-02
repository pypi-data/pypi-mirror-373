from rest_framework.reverse import reverse

from wbcore.metadata.configs.endpoints import EndpointViewConfig


class PlayerTeamEndpointConfig(EndpointViewConfig):
    def get_create_endpoint(self, **kwargs) -> str:
        endpoint: str = super().get_create_endpoint(**kwargs)
        if team_id := self.view.kwargs.get("team_id"):
            endpoint += f"?team={team_id}"
        return endpoint

    def get_endpoint(self, **kwargs) -> str:
        return reverse("example_app:player-team-list", args=[self.view.kwargs["team_id"]], request=self.request)


class MatchStadiumEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs) -> str:
        return reverse("example_app:match-stadium-list", args=[self.view.kwargs["stadium_id"]], request=self.request)


class MatchLeagueEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs) -> str:
        return reverse("example_app:match-league-list", args=[self.view.kwargs["league_id"]], request=self.request)


class TeamStadiumEndpointConfig(EndpointViewConfig):
    def get_create_endpoint(self, **kwargs) -> str:
        endpoint: str = super().get_create_endpoint(**kwargs)
        if stadium_id := self.view.kwargs.get("stadium_id"):
            endpoint += f"?stadium={stadium_id}"
        return endpoint

    def get_endpoint(self, **kwargs) -> str:
        return reverse("example_app:team-stadium-list", args=[self.view.kwargs["stadium_id"]], request=self.request)


class LeagueSportEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs) -> str:
        return reverse("example_app:league-sport-list", args=[self.view.kwargs["sport_id"]], request=self.request)


class EventTypeSportEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs) -> str:
        return reverse("example_app:eventtype-sport-list", args=[self.view.kwargs["sport_id"]], request=self.request)


class EventEndpointConfig(EndpointViewConfig):
    def get_delete_endpoint(self, **kwargs) -> None:
        return None


class LeagueStatisticsEndpointConfig(EndpointViewConfig):
    def get_delete_endpoint(self, **kwargs) -> None:
        return None

    def get_create_endpoint(self, **kwargs) -> None:
        return None

    def get_instance_endpoint(self, **kwargs) -> None:
        return None


class EventMatchEndpointConfig(EventEndpointConfig):
    def get_endpoint(self, **kwargs) -> str:
        return reverse("example_app:event-match-list", args=[self.view.kwargs["match_id"]], request=self.request)

    def get_create_endpoint(self, **kwargs) -> None:
        return None


class TeamResultsEndpointConfig(EndpointViewConfig):
    def get_delete_endpoint(self, **kwargs) -> None:
        return None

    def get_instance_endpoint(self, **kwargs) -> None:
        return None

    def get_create_endpoint(self, **kwargs) -> None:
        return None
