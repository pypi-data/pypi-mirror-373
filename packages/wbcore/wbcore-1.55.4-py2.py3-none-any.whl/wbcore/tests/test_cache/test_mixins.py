import pytest
from faker import Faker

from wbcore.cache.decorators import cache_table
from wbcore.cache.mixins import CacheMixin
from wbcore.utils.strings import camel_to_snake_case

fake = Faker()


class TestCacheMixin:
    @pytest.fixture
    def view_class(self):
        @cache_table(
            timeout=lambda view: view.timeout,
            key_prefix=lambda view: view.get_parameter_value,
        )
        class CacheTable(CacheMixin):
            timeout = fake.pyint()
            get_parameter_value = fake.word()

        return CacheTable

    def test_get_cache_timeout(self, view_class):
        view = view_class()
        assert view._get_cache_timeout() == view_class.timeout

    def test_get_cache_key(self, view_class):
        view = view_class()
        assert view._get_cache_key() == camel_to_snake_case(view_class.__name__) + "-" + view_class.get_parameter_value
