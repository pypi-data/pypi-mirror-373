from random import randint

import pytest

from wbcore.metadata.configs.display.instance_display.styles import Style
from wbcore.metadata.configs.display.instance_display.utils import (
    grid_definition,
    repeat,
    repeat_field,
    split_list_into_grid_template_area_sublists,
)


def test_repeat():
    assert repeat(2, Style.px(20)) == "repeat(2, 20px)"


def test_repeat_field():
    assert repeat_field(2, Style.px(20)) == "20px 20px"


def test_grid_definition():
    assert grid_definition(Style.px(20), Style.px(10), Style.px(20)) == "20px 10px 20px"


@pytest.mark.parametrize(
    ("input", "output"),
    [
        ([], [[".", ".", "."]]),
        (["abc", "d"], [["abc", "d", "."]]),
        (["abc", "d", "ef"], [["abc", "d", "ef"]]),
        (["dh", "faf", "fsefs", "ss"], [["dh", "faf", "fsefs"], ["ss", ".", "."]]),
        (["dh", "faf", "fsefs", "ss", "rty", "dthf"], [["dh", "faf", "fsefs"], ["ss", "rty", "dthf"]]),
    ],
)
def test_split_list_into_grid_template_area_sublists(input, output):
    assert split_list_into_grid_template_area_sublists(input, 3) == output


def test_split_list_into_grid_template_area_sublists_error():
    with pytest.raises(ValueError):
        split_list_into_grid_template_area_sublists(["abc"], -3)


def test_split_list_into_grid_template_area_sublists_random():
    column_number = randint(1, 5)
    field_list = ["Test" for _ in range(0, 15)]
    for sublist in split_list_into_grid_template_area_sublists(field_list, column_number):
        assert len(sublist) == column_number
