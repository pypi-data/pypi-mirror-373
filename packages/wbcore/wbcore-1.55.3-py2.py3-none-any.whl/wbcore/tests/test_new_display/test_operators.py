import pytest

from wbcore.metadata.configs.display.instance_display import operators


@pytest.mark.parametrize(
    "method, value, result",
    [
        (operators.lt, 20, "<20"),
        (operators.lte, 20, "<=20"),
        (operators.gt, 20, ">20"),
        (operators.gte, 20, ">=20"),
    ],
)
def test_operator(method, value, result):
    assert method(value) == result
