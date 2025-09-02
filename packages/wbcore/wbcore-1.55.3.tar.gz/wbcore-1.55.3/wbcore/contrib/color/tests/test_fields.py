import pytest
from django.core.exceptions import ValidationError
from wbcore.contrib.color.fields import validate_color


class TestColorield:
    @pytest.mark.parametrize(
        ("input", "valid"),
        [
            ("#1234567", False),
            ("259868", False),
            ("#25986", False),
            ("", False),
            ("#d225b0", True),
            ("#4839a3", True),
            ("#259868", True),
            (None, True),
        ],
    )
    def test_color_validator(self, input, valid):
        if valid:
            assert input == validate_color(input)
        else:
            with pytest.raises(ValidationError):
                validate_color(input)
