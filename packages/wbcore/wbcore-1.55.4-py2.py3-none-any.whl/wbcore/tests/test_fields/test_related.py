from rest_framework.fields import Field

from wbcore.serializers import PrimaryKeyRelatedField
from wbcore.serializers.fields.mixins import WBCoreSerializerFieldMixin
from wbcore.serializers.fields.related import WBCoreManyRelatedField

# from tests.models import ModelTest


class TestWBCoreManyRelatedField:
    def setup_method(self):
        class TestSubClass(WBCoreSerializerFieldMixin, Field):
            field_type = "field_type"

        self.TestSubClass = TestSubClass
        self.field = WBCoreManyRelatedField

    def test_not_none(self):
        assert self.field(child_relation=self.TestSubClass()) is not None

    def test_required_allowed_null(self):
        field = self.field(child_relation=self.TestSubClass(), required=False)
        assert field.allow_null

    def test_validation_allow_null(self):
        field = self.field(child_relation=self.TestSubClass(), required=False)
        validated_data = field.run_validation(None)

        assert validated_data == []

    def test_get_representation(self):
        field = self.field(child_relation=self.TestSubClass())
        assert field.get_representation(None, "field_name")[1]["multiple"]


class TestPrimaryKeyRelatedField:
    def setup_method(self):
        self.field = PrimaryKeyRelatedField

    def test_is_not_none_read_only(self):
        assert self.field(read_only=True) is not None

    # def test_is_not_none_queryset(self):
    #     assert self.field(queryset=ModelTest.objects.all()) is not None

    # def test_many_is_not_none(self):
    #     field = self.field.many_init(required=True, queryset=ModelTest.objects.all())
    #     assert field is not None
    #     assert isinstance(field, WBCoreManyRelatedField)

    # def test_get_representation(self):
    #     assert self.field(queryset=ModelTest.objects.all()).get_representation(None, "field_name") == {
    #         "key": "field_name",
    #         "label": None,
    #         "type": WBCoreType.SELECT.value,
    #         "required": True,
    #         "read_only": False,
    #         "decorators": [],
    #         "depends_on": [],
    #
    #     }

    # def test_get_representation_multiple(self):
    #     assert self.field.many_init(queryset=ModelTest.objects.all()).get_representation(None, "field_name") == {
    #         "key": "field_name",
    #         "label": "",
    #         "type": WBCoreType.SELECT.value,
    #         "required": True,
    #         "read_only": False,
    #         "multiple": True,
    #         "decorators": [],
    #         "depends_on": [],
    #
    #     }

    # @pytest.mark.django_db
    # def test_run_validation(self, model_test):
    #     validated_data = self.field(required=False, queryset=ModelTest.objects.all()).run_validation(
    #         data=model_test.pk
    #     )
    #     assert validated_data == model_test
