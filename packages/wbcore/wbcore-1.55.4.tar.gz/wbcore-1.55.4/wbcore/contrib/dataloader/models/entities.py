from django.db import models

from wbcore.contrib.dataloader.dataloaders import DataloaderProxy
from wbcore.contrib.dataloader.models.querysets import EntityQuerySet


class Entity(models.Model):
    """An abstract model representing an entity with associated dataloaders.

    This model serves as a base for entities that store data and have dataloaders
    attached for data retrieval and processing. It includes specialized fields to
    facilitate the use of dataloaders:

    Attributes:
        dl_proxy (DataloaderProxy): A reference to the DataloaderProxy. This should be
            set when using this model to manage the associated dataloaders.
        dl_parameters (models.JSONField): A field to store parameters for various
            dataloaders. It is structured in the format:
            `{"dataloader_name": {"path": "path.to.dataloader", "parameters": {}}}`.
        objects (EntityQuerySet): A custom model manager providing an interface to a
            dataloader proxy. This proxy can be accessed through the 'dl' method on a
            queryset, e.g., `Entity.objects.all().dl`.
    """

    dl_proxy: DataloaderProxy
    dl_parameters = models.JSONField(default=dict, blank=True)
    objects = EntityQuerySet.as_manager()

    class Meta:
        abstract = True
