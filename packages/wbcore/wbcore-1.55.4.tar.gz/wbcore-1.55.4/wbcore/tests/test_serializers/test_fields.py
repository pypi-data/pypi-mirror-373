import pytest
from rest_framework import serializers
from rest_framework.test import APIRequestFactory

from wbcore.serializers.fields import CharField


@pytest.fixture
def char_field_base():
    field_name = "test_field"
    request = APIRequestFactory().get("")
    default_placeholder = "Enter text here"
    secure_flag = True
    return {
        "field_name": field_name,
        "request": request,
        "default_placeholder": default_placeholder,
        "secure_flag": secure_flag,
    }


class TestCharFieldInitialization:
    """Tests for the initialization of the CharField class."""

    def test_default_initialization(self):
        """Test CharField default initialization with no custom parameters."""
        field = CharField()
        assert field.allow_null is True
        assert field.allow_blank is False
        assert field.placeholder is None
        assert field.secure is False

    def test_custom_initialization(self, char_field_base):
        """Test CharField initialization with custom placeholder and secure parameters."""
        field = CharField(placeholder=char_field_base["default_placeholder"], secure=char_field_base["secure_flag"])
        assert field.placeholder == char_field_base["default_placeholder"]
        assert field.secure is True

    def test_empty_string_placeholder(self, char_field_base):
        """Test that an empty string as a placeholder does not appear in the representation."""
        field = CharField(placeholder="")
        assert field.placeholder == ""
        _, representation = field.get_representation(char_field_base["request"], char_field_base["field_name"])
        assert "placeholder" not in representation

    def test_non_boolean_secure(self, char_field_base):
        """
        Test non-boolean values for the 'secure' attribute.

        Non-boolean values are expected to be treated as truthy (e.g., "no" should behave like True).
        """
        field = CharField(secure="no")
        _, representation = field.get_representation(char_field_base["request"], char_field_base["field_name"])
        assert "secure" in representation
        assert representation["secure"] is True


class TestCharFieldRepresentation:
    """Tests for the representation of the CharField class."""

    def test_representation_without_placeholder_and_secure(self, char_field_base):
        """Test CharField representation without custom placeholder or secure attributes."""
        field = CharField()
        _, representation = field.get_representation(char_field_base["request"], char_field_base["field_name"])
        assert "placeholder" not in representation
        assert "secure" not in representation

    def test_representation_with_placeholder(self, char_field_base):
        """Test CharField representation with a custom placeholder."""
        field = CharField(placeholder="Enter text here")
        _, representation = field.get_representation(char_field_base["request"], char_field_base["field_name"])
        assert "placeholder" in representation
        assert representation["placeholder"] == "Enter text here"

    def test_representation_with_secure(self, char_field_base):
        """Test CharField representation with the secure attribute enabled."""
        field = CharField(secure=True)
        _, representation = field.get_representation(char_field_base["request"], char_field_base["field_name"])
        assert "secure" in representation
        assert representation["secure"] is True

    def test_representation_with_placeholder_and_secure(self, char_field_base):
        """Test CharField representation with both placeholder and secure attributes."""
        field = CharField(placeholder="Enter text here", secure=True)
        _, representation = field.get_representation(char_field_base["request"], char_field_base["field_name"])
        assert "placeholder" in representation
        assert representation["placeholder"] == "Enter text here"
        assert "secure" in representation
        assert representation["secure"] is True


class TestCharFieldValidation:
    """Tests for the validation of empty values in the CharField class."""

    def test_validate_empty_with_allow_null_true(self):
        """Test validation when allow_null is True and data is None."""
        field = CharField(allow_null=True, allow_blank=False)
        should_validate, data = field.validate_empty_values(None)
        assert data == ""
        assert should_validate is False

    def test_validate_empty_with_allow_blank_true(self):
        """Test validation when allow_blank is True and data is None."""
        field = CharField(allow_blank=True, allow_null=False)
        should_validate, data = field.validate_empty_values(None)
        assert data == ""
        assert should_validate is False

    def test_validate_empty_with_allow_null_and_allow_blank_false(self):
        """Test validation when both allow_null and allow_blank are False and data is None."""
        field = CharField(allow_null=False, allow_blank=False)
        with pytest.raises(serializers.ValidationError):
            field.validate_empty_values(None)

    def test_validate_empty_with_allow_null_and_allow_blank_true(self):
        """Test validation when both allow_null and allow_blank are True and data is None."""
        field = CharField(allow_null=True, allow_blank=True)
        should_validate, data = field.validate_empty_values(None)
        assert data == ""
        assert should_validate is False

    def test_validate_empty_with_non_none_data(self):
        """Test validation when data is a non-empty string."""
        field = CharField()
        should_validate, data = field.validate_empty_values("Test")
        assert data == "Test"
        assert should_validate is False

    def test_validate_empty_with_empty_string_data(self):
        """Test validation when data is an empty string."""
        field = CharField(allow_blank=True, allow_null=False)
        should_validate, data = field.validate_empty_values("")
        assert data == ""
        assert should_validate is False

    def test_validate_empty_with_whitespace_string_data(self):
        """Test validation when data is a whitespace string."""
        field = CharField(allow_blank=True, allow_null=False)
        should_validate, data = field.validate_empty_values("   ")
        assert data == "   "
        assert should_validate is False
