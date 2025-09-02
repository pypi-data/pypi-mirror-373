import pytest
from rest_framework.exceptions import ValidationError

from wbcore.serializers import ChoiceField
from wbcore.serializers.fields.types import WBCoreType


class TestChoiceField:
    CHOICES = [
        ("choice1", "Choice 1"),
        ("choice2", "Choice 2"),
    ]

    def setup_method(self):
        self.field = ChoiceField(choices=self.CHOICES)

    def test_not_none(self):
        assert self.field is not None

    @pytest.mark.parametrize("choice", [choice for choice, choice_repr in CHOICES])
    def test_to_internal_value(self, choice):
        assert self.field.to_internal_value(choice) == choice

    @pytest.mark.parametrize("choice", [choice for choice, choice_repr in CHOICES])
    def test_to_representation(self, choice):
        assert self.field.to_representation(choice) == choice

    def test_to_internal_value_validation_error(self):
        with pytest.raises(ValidationError):
            self.field.to_internal_value("choice3")

    def test_field_type(self):
        assert self.field.field_type == WBCoreType.SELECT.value

    def test_representation(self):
        choices = [{"label": choice[1], "value": choice[0], "group": None} for choice in self.CHOICES]
        assert self.field.get_representation(None, "field_name") == (
            "field_name",
            {
                "key": "field_name",
                "label": None,
                "type": self.field.field_type,
                "required": True,
                "read_only": False,
                "choices": choices,
                "decorators": [],
                "depends_on": [],
            },
        )

    def test_representation_with_group(self):
        field = ChoiceField(choices=self.CHOICES, group_key_mapping={"choice1": "group1"})
        rep = field.get_representation(None, "field_name")[1]
        assert rep["choices"] == [
            {"label": "Choice 1", "value": "choice1", "group": "group1"},
            {"label": "Choice 2", "value": "choice2", "group": None},
        ]
