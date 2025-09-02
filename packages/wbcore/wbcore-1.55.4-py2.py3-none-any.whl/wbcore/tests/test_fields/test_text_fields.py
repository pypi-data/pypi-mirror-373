import pytest
from rest_framework.exceptions import ValidationError

from wbcore.serializers import CharField, StringRelatedField, TextField
from wbcore.serializers.fields.types import WBCoreType


class TestCharField:
    def setup_method(self):
        self.field = CharField()
        self.field_with_placeholder = CharField(placeholder="Enter Text here")

    def test_not_none(self):
        assert self.field is not None

    @pytest.mark.parametrize("input, expected", [(1, "1"), ("a", "a")])
    def test_to_internal_value(self, input, expected):
        assert self.field.to_internal_value(input) == expected

    def test_to_internal_value_validation_error(self):
        with pytest.raises(ValidationError):
            self.field.to_internal_value(None)

    def test_field_type(self):
        assert self.field.field_type == WBCoreType.TEXT.value

    def test_representation(self):
        assert self.field.get_representation(None, "field_name") == (
            "field_name",
            {
                "key": "field_name",
                "label": None,
                "type": self.field.field_type,
                "required": True,
                "read_only": False,
                "decorators": [],
                "depends_on": [],
            },
        )

    def test_string_placeholder(self):
        assert self.field_with_placeholder.get_representation(None, "field_name") == (
            "field_name",
            {
                "key": "field_name",
                "label": None,
                "type": self.field.field_type,
                "required": True,
                "read_only": False,
                "decorators": [],
                "depends_on": [],
                "placeholder": "Enter Text here",
            },
        )


@pytest.mark.django_db
class TestStringRelatedField:
    def setup_method(self):
        self.field = StringRelatedField()

    def test_not_none(self):
        assert self.field is not None

    # def test_to_representation(self, model_test):
    #     assert self.field.to_representation(model_test) == str(model_test)

    def test_field_type(self):
        assert self.field.field_type == WBCoreType.TEXT.value

    def test_representation(self):
        assert self.field.get_representation(None, "field_name") == (
            "field_name",
            {
                "key": "field_name",
                "label": None,
                "type": self.field.field_type,
                "required": False,
                "read_only": True,
                "decorators": [],
                "depends_on": [],
            },
        )


class TestTextField:
    def setup_method(self):
        self.field = TextField()

    def test_not_none(self):
        assert self.field is not None

    @pytest.mark.parametrize("input, expected", [(123, "123"), ("abc", "abc")])
    def test_to_internal_value(self, input, expected):
        assert self.field.to_internal_value(input) == expected

    def test_to_internal_value_validation_error(self):
        with pytest.raises(ValidationError):
            self.field.to_internal_value(None)

    def test_field_type(self):
        assert self.field.field_type == WBCoreType.TEXTEDITOR.value

    def test_representation(self):
        assert self.field.get_representation(None, "field_name") == (
            "field_name",
            {
                "key": "field_name",
                "content_type": self.field.texteditor_content_type,
                "label": None,
                "type": self.field.field_type,
                "required": True,
                "plugin_configs": {},
                "read_only": False,
                "decorators": [],
                "depends_on": [],
            },
        )
