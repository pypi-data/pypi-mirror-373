from unittest.mock import patch

import pytest

from wbcore.contrib.example_app.models import Match
from wbcore.contrib.example_app.viewsets.displays.match import (
    get_match_status_formatting,
    get_match_status_legend,
)


@pytest.mark.django_db
class TestMatch:
    @patch("wbcore.contrib.example_app.models.Match.MatchStatus.get_color_map")
    def test_get_match_status_legend(self, mock_color_map):
        mock_color_map.return_value = [
            (Match.MatchStatus.FINISHED, "firstcolor"),
            (Match.MatchStatus.ONGOING, "secondcolor"),
            (Match.MatchStatus.SCHEDULED, "lastcolor"),
        ]
        assert [(y.icon, y.label, y.value) for y in get_match_status_legend()[0].items] == [
            ("firstcolor", Match.MatchStatus.FINISHED.label, Match.MatchStatus.FINISHED.value),
            ("secondcolor", Match.MatchStatus.ONGOING.label, Match.MatchStatus.ONGOING.value),
            ("lastcolor", Match.MatchStatus.SCHEDULED.label, Match.MatchStatus.SCHEDULED.value),
        ]
        assert mock_color_map.called

    @patch("wbcore.contrib.example_app.models.Match.MatchStatus.get_color_map")
    def test_get_match_status_formatting(self, mock_color_map):
        mock_color_map.return_value = [
            (Match.MatchStatus.ONGOING, "firstcolor"),
            (Match.MatchStatus.SCHEDULED, "secondcolor"),
            (Match.MatchStatus.FINISHED, "lastcolor"),
        ]
        assert [
            (y.style["backgroundColor"], y.condition[1]) for y in get_match_status_formatting()[0].formatting_rules
        ] == [
            ("firstcolor", Match.MatchStatus.ONGOING.value),
            ("secondcolor", Match.MatchStatus.SCHEDULED.value),
            ("lastcolor", Match.MatchStatus.FINISHED.value),
        ]
