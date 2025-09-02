from wbcore.serializers import ListField
from wbcore.serializers.fields.types import WBCoreType


class TestListField:
    def setup_method(self):
        self.field = ListField()

    def test_not_none(self):
        assert self.field is not None

    def test_field_type(self):
        assert self.field.field_type == WBCoreType.LIST.value

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
