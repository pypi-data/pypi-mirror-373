from wbcore.serializers import JSONTextEditorField
from wbcore.serializers.fields.types import ReturnContentType, WBCoreType


class TestJSONTextEditorField:
    def setup_method(self):
        self.field = JSONTextEditorField()

    def test_not_none(self):
        assert self.field is not None

    def test_field_type(self):
        assert self.field.field_type == WBCoreType.TEXTEDITOR.value

    def test_representation(self):
        assert self.field.get_representation(None, "field_name") == (
            "field_name",
            {
                "key": "field_name",
                "content_type": ReturnContentType.JSON.value,
                "label": None,
                "type": self.field.field_type,
                "required": True,
                "read_only": False,
                "decorators": [],
                "depends_on": [],
            },
        )
