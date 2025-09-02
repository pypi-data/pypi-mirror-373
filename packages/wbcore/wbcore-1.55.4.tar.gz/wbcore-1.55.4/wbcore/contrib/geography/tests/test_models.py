from typing import Callable

import pytest

from wbcore.contrib.geography.models import Geography


class TestModels:
    @pytest.fixture
    def geography(self):
        return Geography(name="Test Geography")

    def test_endpoint_basename(self, geography):
        assert isinstance(geography.get_endpoint_basename, Callable)

    def test_representation_endpoint(self, geography):
        assert isinstance(geography.get_representation_endpoint, Callable)

    def test_representation_value_key(self, geography):
        assert geography.get_representation_value_key() == "id"

    def test_representation_label_key(self, geography):
        assert geography.get_representation_label_key is not None

    def test_str(self, geography):
        assert isinstance(str(geography), str)
        assert str(geography) == geography.name
