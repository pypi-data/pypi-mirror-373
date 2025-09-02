import pytest
from django.core.exceptions import ValidationError

from wbcore.models.fields import validate_year


class TestYearField:
    @pytest.mark.parametrize(
        ("input", "valid"),
        [
            (3, False),
            (24, False),
            (165, False),
            (41877, False),
            (2065, True),
            (1969, True),
            (1283, True),
            (None, True),
        ],
    )
    def test_year_validator(self, input, valid):
        if valid:
            validate_year(input)
        else:
            with pytest.raises(ValidationError):
                validate_year(input)
