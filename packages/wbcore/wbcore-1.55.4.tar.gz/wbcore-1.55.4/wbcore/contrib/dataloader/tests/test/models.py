from django.db import models

from wbcore.contrib.dataloader.models import Entity
from wbcore.contrib.dataloader.tests.test.dataloaders.proxies import (
    EntityTestDataloaderProxy,
)


class EntityTest(Entity):
    dl_proxy = EntityTestDataloaderProxy
    name = models.CharField(max_length=255)
