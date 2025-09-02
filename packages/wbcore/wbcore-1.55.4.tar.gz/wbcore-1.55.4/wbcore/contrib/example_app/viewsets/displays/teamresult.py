from django.utils.translation import gettext as _

from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.list_display import ListDisplay
from wbcore.metadata.configs.display.view_config import DisplayViewConfig

TEAMRESULTS_FIELDS = [
    dp.Field(key="league", label=_("League")),
    dp.Field(key="team", label=_("Team")),
    dp.Field(key="games_played", label=_("Games")),
    dp.Field(key="wins", label=_("Wins")),
    dp.Field(key="draws", label=_("Draws")),
    dp.Field(key="losses", label=_("Losses")),
    dp.Field(key="match_points_for", label=_("Match Points For")),
    dp.Field(key="match_points_against", label=_("Match Points Against")),
    dp.Field(key="match_point_difference", label=_("Match Point Difference")),
    dp.Field(key="points", label=_("Points")),
    dp.Field(key="form", label=_("Form")),
]


class TeamResultsDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> ListDisplay:
        return dp.ListDisplay(fields=TEAMRESULTS_FIELDS)


class TeamResultsLeagueDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> ListDisplay:
        fields = TEAMRESULTS_FIELDS.copy()
        fields.pop(0)
        return dp.ListDisplay(fields=fields)
