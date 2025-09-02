import pytest
from rest_framework.test import APIRequestFactory

from .. import resolve_profile
from ..factories import UserFactory


@pytest.mark.django_db
class TestSpecifics:
    def test_resolve_profile(self):
        request = APIRequestFactory().get("")
        request.user = UserFactory(is_active=True, is_superuser=True)
        result = resolve_profile(request)
        assert result
        assert result.get("endpoint")
