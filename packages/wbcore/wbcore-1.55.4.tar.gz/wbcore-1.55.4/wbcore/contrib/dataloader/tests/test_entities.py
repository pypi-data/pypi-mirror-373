import pytest

from wbcore.contrib.dataloader.tests.test.models import EntityTest


@pytest.mark.django_db
class TestEntities:
    def test_entity_factory(self, entity_test):
        assert entity_test.id, "The Test Entity should have an id if the factory created it"

    def test_entity_creation(self):
        entity_test = EntityTest.objects.create(name="test", dl_parameters={"data": {"path": "abc", "parameters": {}}})
        assert entity_test.id, "It should be possible to create an EntityTest model"
