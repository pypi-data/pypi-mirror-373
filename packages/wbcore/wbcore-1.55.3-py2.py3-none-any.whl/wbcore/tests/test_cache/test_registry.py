import pytest
from django.core.cache import cache
from dynamic_preferences.models import global_preferences_registry
from faker import Faker

from wbcore.cache.registry import CachedClass
from wbcore.contrib.authentication.factories import UserFactory
from wbcore.viewsets import ChartViewSet

fake = Faker()


class TestClass(ChartViewSet):
    test = fake.word()

    def _get_dataframe(self):
        return {"figure": "b"}

    def _get_cache_key(self) -> str:
        return "test-class-cache"


@pytest.mark.django_db
class TestCachedClass:
    @pytest.fixture()
    def system_user(self):
        return UserFactory.create(
            is_superuser=True, email=global_preferences_registry.manager()["wbcore__system_user_email"]
        )

    @pytest.fixture()
    def cache_class(self, view_kwargs, get_parameters):
        return CachedClass(
            view_class=TestClass,
            view_kwargs=view_kwargs,
            get_parameters=get_parameters,
        )

    @pytest.mark.parametrize("get_parameters, view_kwargs", [([{"a": "b"}], [{}])])
    def test__get_requests(self, get_parameters, view_kwargs, system_user, cache_class):
        request = list(cache_class._get_requests())[0]
        assert request.user == system_user
        assert request.GET.dict() == get_parameters[0]

    @pytest.mark.parametrize("get_parameters, view_kwargs", [(lambda: [{"a": TestClass.test}], [{}])])
    def test__get_requests_callable(self, system_user, cache_class):
        request = list(cache_class._get_requests())[0]
        assert request.user == system_user
        assert request.GET.dict() == {"a": cache_class.view_class.test}

    @pytest.mark.parametrize("get_parameters, view_kwargs", [([{}], [{"a": "b"}])])
    def test_fetch_cache(self, system_user, cache_class):
        cache.set(
            "test-class-cache", {"other_figure": "c"}
        )  # ensure that fetch cache clear cache before refetching result

        res = cache_class.fetch_cache()[0]
        assert res == {"figure": "b"}
