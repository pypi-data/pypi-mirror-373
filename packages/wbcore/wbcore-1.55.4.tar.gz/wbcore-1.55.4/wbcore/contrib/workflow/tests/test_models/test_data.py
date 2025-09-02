from datetime import date, datetime
from unittest.mock import patch

import pytest
from wbcore.contrib.workflow.models import Data


@pytest.mark.django_db
class TestData:
    @pytest.mark.parametrize(
        ("type", "field_name"),
        [
            (Data.DataType.CHAR, "CharField"),
            (Data.DataType.BOOL, "BooleanField"),
            (Data.DataType.DATE, "DateField"),
            (Data.DataType.DATETIME, "DateTimeField"),
            (Data.DataType.INT, "IntegerField"),
        ],
    )
    @patch("wbcore.contrib.workflow.models.data.Data.cast_value_to_datatype")
    def test_get_serializer_field(self, mock_cast, data_factory, type, field_name):
        data = data_factory(help_text=None, data_type=type)
        field = data.get_serializer_field()
        assert field.__class__.__name__ == field_name
        assert field.label == data.label
        assert field.required == data.required
        assert "default" not in field._kwargs
        assert "help_text" not in field._kwargs
        assert not mock_cast.called

    @patch("wbcore.contrib.workflow.models.data.Data.cast_value_to_datatype")
    def test_get_serializer_field_help_text(self, mock_cast, data_factory):
        data = data_factory()
        field = data.get_serializer_field()
        assert field.label == data.label
        assert field.required == data.required
        assert "default" not in field._kwargs
        assert field.help_text == data.help_text
        assert not mock_cast.called

    @patch("wbcore.contrib.workflow.models.data.Data.cast_value_to_datatype")
    def test_get_serializer_field_default(self, mock_cast, data_factory):
        data_type = Data.DataType.INT
        default_value = "50"
        casted_default_value = 50
        data = data_factory(default=default_value, data_type=data_type)
        mock_cast.return_value = casted_default_value
        field = data.get_serializer_field()
        assert mock_cast.call_args.args == (data_type, default_value)
        assert field.label == data.label
        assert field.required == data.required
        assert field.default == casted_default_value
        assert field.help_text == data.help_text

    @pytest.mark.parametrize(
        ("data_type", "value", "expected"),
        [
            (Data.DataType.BOOL, "True", True),
            (Data.DataType.BOOL, "true", True),
            (Data.DataType.BOOL, "False", False),
            (Data.DataType.BOOL, "false", False),
            (Data.DataType.DATE, "12.07.1054", date(1054, 7, 12)),
            (Data.DataType.DATETIME, "12.07.1054 13:47:09", datetime(1054, 7, 12, 13, 47, 9)),
            (Data.DataType.CHAR, "123456", "123456"),
            (Data.DataType.INT, "123456", 123456),
        ],
    )
    def test_cast_value_to_datatype(self, data_type, value, expected):
        assert Data.cast_value_to_datatype(data_type, value) == expected

    @pytest.mark.parametrize(
        ("data_type", "value"),
        [
            (Data.DataType.BOOL, "Test"),
            (Data.DataType.BOOL, "1"),
            (Data.DataType.BOOL, "0"),
            (Data.DataType.DATE, "07/12/1054"),
            (Data.DataType.DATETIME, "07/12/1054 13:47:09"),
            (Data.DataType.INT, "Test"),
        ],
    )
    def test_cast_value_to_datatype_error(self, data_type, value):
        with pytest.raises(ValueError):
            Data.cast_value_to_datatype(data_type, value)

    @pytest.mark.parametrize(
        ("target", "data_type"),
        [
            (datetime(2003, 8, 28, 7, 18, 4), Data.DataType.DATETIME),
            (date(2003, 8, 28), Data.DataType.DATE),
            (True, Data.DataType.BOOL),
            (False, Data.DataType.BOOL),
            (69, Data.DataType.INT),
            ("Test", Data.DataType.CHAR),
        ],
    )
    @patch("wbcore.contrib.workflow.models.data.Data.cast_value_to_datatype")
    def test_cast_value_from_target_object(self, mock_cast, target, data_type):
        Data.cast_value_from_target_object(target, "Test")
        assert mock_cast.call_args.args == (data_type, "Test")

    @pytest.mark.parametrize(
        "target",
        [None, Data, str, {}, []],
    )
    def test_cast_value_from_target_object_error(self, target):
        with pytest.raises(ValueError):
            Data.cast_value_from_target_object(target, "Test")

    @pytest.mark.parametrize(
        ("data_object", "data_type", "expected"),
        [
            (datetime(2003, 8, 28, 7, 18, 4), Data.DataType.DATETIME, "28.08.2003 07:18:04"),
            (date(2003, 8, 28), Data.DataType.DATE, "28.08.2003"),
            (True, Data.DataType.BOOL, "True"),
            (False, Data.DataType.BOOL, "False"),
            (69, Data.DataType.INT, "69"),
            ("Test", Data.DataType.CHAR, "Test"),
        ],
    )
    def test_cast_datatype_to_string(self, data_type, data_object, expected):
        assert Data.cast_datatype_to_string(data_type, data_object) == expected

    @pytest.mark.parametrize(
        ("data_object", "data_type"),
        [
            (69, Data.DataType.DATETIME),
            ("Test", Data.DataType.DATE),
            (datetime(2003, 8, 28, 7, 18, 4), Data.DataType.BOOL),
        ],
    )
    def test_cast_datatype_to_string_error(self, data_type, data_object):
        with pytest.raises(ValueError):
            Data.cast_datatype_to_string(data_type, data_object)
