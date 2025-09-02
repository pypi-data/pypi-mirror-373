import factory

from .models import EntityTest


class EntityTestFactory(factory.django.DjangoModelFactory):
    dl_parameters = {
        "data": {"path": "wbcore.contrib.dataloader.tests.test.dataloaders.dataloaders.RandomData", "parameters": {}}
    }
    name = factory.Faker("pystr")

    class Meta:
        model = EntityTest
