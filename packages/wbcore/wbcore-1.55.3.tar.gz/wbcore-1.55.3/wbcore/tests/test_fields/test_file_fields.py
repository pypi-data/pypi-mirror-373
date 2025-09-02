from wbcore.serializers import FileField, ImageField
from wbcore.serializers.fields.types import WBCoreType


class TestImageField:
    def setup_method(self):
        self.field = ImageField()

    def test_not_none(self):
        assert self.field is not None

    def test_field_type(self):
        assert self.field.field_type == WBCoreType.IMAGE.value

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


class TestFileField:
    def setup_method(self):
        self.field = FileField()

    def test_not_none(self):
        assert self.field is not None

    def test_field_type(self):
        assert self.field.field_type == WBCoreType.FILE.value

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
