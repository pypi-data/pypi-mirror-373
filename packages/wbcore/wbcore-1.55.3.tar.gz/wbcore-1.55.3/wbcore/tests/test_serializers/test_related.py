import pytest
from rest_framework.test import APIRequestFactory

from wbcore.contrib.authentication.factories import UserFactory
from wbcore.contrib.authentication.models import User
from wbcore.serializers import PrimaryKeyRelatedField, RepresentationSerializer


class TestRepresentationSerializer:
    @pytest.fixture()
    def test_representation_serializer(self):
        class TestFixtureRepresentationSerializer(RepresentationSerializer):
            filter_params = {"a": "a"}

            class Meta:
                model = User
                fields = ("id",)

        return TestFixtureRepresentationSerializer

    @pytest.fixture()
    def option_request(self):
        factory = APIRequestFactory()
        return factory.get("/")

    def test_filter_params(self, test_representation_serializer, option_request):
        serializer = test_representation_serializer(source="source")
        assert serializer._get_filter_params(option_request) == {"a": "a"}

        assert serializer.get_representation(option_request, "id")[1]["endpoint"]["url"].endswith("?a=a")
        # assert kwargs override class attribute
        serializer = test_representation_serializer(source="source", filter_params={"b": "b"})
        assert serializer._get_filter_params(option_request) == {"b": "b"}

        serializer = test_representation_serializer(source="source", ignore_filter=True)
        assert serializer._get_filter_params(option_request) == dict()

    def test_filter_params_with_method(self, option_request):
        class TestFixtureRepresentationSerializer(RepresentationSerializer):
            def get_filter_params(self, *args):
                return {"c": "c"}

            class Meta:
                model = User
                fields = ("id",)

        serializer = TestFixtureRepresentationSerializer(source="source", filter_params={"b": "b"})
        assert serializer._get_filter_params(option_request) == {
            "b": "b"
        }  # kwargs or class attributes take precedance

        serializer = TestFixtureRepresentationSerializer(source="source")
        assert serializer._get_filter_params(option_request) == {
            "c": "c"
        }  # kwargs or class attributes take precedance

    def test_queryset_unset_if_read_only_callable(self):
        u1 = UserFactory.build()
        UserFactory.build()  # noisy user
        queryset = [u1]
        # test that the queryset is properly unset if the readonly attribute is a callable and behave normally otherwise
        related_field = PrimaryKeyRelatedField(read_only=False, queryset=queryset)
        assert related_field.queryset == queryset
        with pytest.raises(AssertionError):
            PrimaryKeyRelatedField(read_only=True, queryset=queryset)

        related_field = PrimaryKeyRelatedField(read_only=lambda: True, queryset=queryset)
        assert related_field.queryset is None

    def test_related_field_binding_reinstate_queryset_on_readonly_callable(self, test_representation_serializer):
        u1 = UserFactory.build()
        UserFactory.build()  # noisy user
        queryset = [u1]
        parent = test_representation_serializer(context={"view": object()})
        related_field = PrimaryKeyRelatedField(read_only=lambda view: False, queryset=queryset)
        assert related_field.queryset is None
        related_field.bind("related_field", parent)
        assert related_field.queryset == queryset
