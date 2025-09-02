import pytest
from django.db.models import F
from django.db.models.expressions import OrderBy

from wbcore.viewsets.mixins import map_ordering


class TestWBCoreOrderingFilter:
    @pytest.mark.parametrize(
        ("input", "output"),
        [
            ("test_str", OrderBy(F("test_str"))),
            ("-test_str", OrderBy(F("test_str"), descending=True)),
            ("test_str__nulls_last", OrderBy(F("test_str"), nulls_last=True)),
            ("-test_str__nulls_last", OrderBy(F("test_str"), nulls_last=True, descending=True)),
            ("test_str__nulls_first", OrderBy(F("test_str"), nulls_first=True)),
            ("-test_str__nulls_first", OrderBy(F("test_str"), nulls_first=True, descending=True)),
        ],
    )
    def test_map_ordering(self, input, output):
        assert map_ordering(input) == output
