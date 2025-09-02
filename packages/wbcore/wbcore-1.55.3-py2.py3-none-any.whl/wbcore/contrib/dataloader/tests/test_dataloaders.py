from typing import Iterator

import pytest

from wbcore.contrib.dataloader.tests.test.dataloaders.proxies import (
    EntityTestDataloaderProxy,
)
from wbcore.contrib.dataloader.tests.test.models import EntityTest


@pytest.mark.django_db
class TestEntityTestDataloader:
    def test_dataloader_proxy(self, entity_test):
        dl_proxy = EntityTest.objects.filter(id=entity_test.id).dl
        assert isinstance(dl_proxy, EntityTestDataloaderProxy), "The proxy should exist"

    def test_dataloader(self, entity_test):
        result = EntityTest.objects.filter(id=entity_test.id).dl.data(10)
        assert isinstance(result, Iterator), "The result of a dataloader should be an iterator"
        assert len(list(result)) == 10, "The result should have a length of 10 items"
        assert all(isinstance(item, int) for item in result), "All items in the result list should be integers"

    def test_multiple_entries_dataloader(self, entity_test_factory):
        entity_test_factory.create()
        entity_test_factory.create()
        entity_test_factory.create()
        result = EntityTest.objects.all().dl.data(10)
        assert len(list(result)) == 30, "The result should have a length of 30 (3 EntityTest x 10) items"

    def test_multiple_dataloader(self, entity_test, entity_test_over_1000):
        result = EntityTest.objects.all().dl.data(10)
        assert (
            len(list(result)) == 20
        ), "The result should have a length of 20 (1 EntityTest x 2 Dataloader x 10) items"

    def test_empty_dataloader(self):
        result = list(EntityTest.objects.all().dl.data(10))
        assert len(result) == 0, "Having no entities, should result in an empty list"
