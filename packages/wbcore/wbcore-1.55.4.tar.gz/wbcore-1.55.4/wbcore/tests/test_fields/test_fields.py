from rest_framework.test import APIRequestFactory

from wbcore.serializers import AdditionalResourcesField, HyperlinkField


class TestAdditionalResourcesField:
    def setup_method(self):
        self.factory = APIRequestFactory()
        self.field = AdditionalResourcesField()

    def test_not_none(self):
        assert self.field is not None


class TestHyperlinkFieldField:
    def setup_method(self):
        self.factory = APIRequestFactory()
        self.field = HyperlinkField(reverse_name="wbcore:notification-list")

    def test_not_none(self):
        assert self.field is not None

    def test_to_representation(self):
        assert self.field.to_representation("abc") == "abc"
