from wbcore.serializers import PrimaryKeyCharField, PrimaryKeyField
from wbcore.serializers.fields.types import WBCoreType


class TestPrimaryKeyField:
    def setup_method(self):
        self.field = PrimaryKeyField()

    def test_not_none(self):
        assert self.field is not None

    def test_field_type(self):
        assert self.field.field_type == WBCoreType.PRIMARY_KEY.value

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


class TestPrimaryKeyCharField:
    def setup_method(self):
        self.field = PrimaryKeyCharField()

    def test_not_none(self):
        assert self.field is not None

    def test_field_type(self):
        assert self.field.field_type == WBCoreType.PRIMARY_KEY.value

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
