from django.db import models

from wbcore.contrib.dataloader.dataloaders.proxies import DataloaderProxy


class EntityQuerySet(models.QuerySet):
    """A custom QuerySet for entities that provides an interface to a dataloader proxy.

    This QuerySet subclass adds a method to interact with the associated dataloader
    proxy. It is designed to be used with models that inherit from the `Entity` class,
    providing a streamlined way to access dataloader functionality directly from
    QuerySet instances.
    """

    @property
    def dl(self) -> DataloaderProxy:
        """Provides access to the dataloader proxy for the entities in the QuerySet.

        This method allows for easy retrieval of the DataloaderProxy instance
        associated with the QuerySet. It enables the utilization of dataloader
        functionalities directly from the QuerySet, facilitating data fetching and
        processing tasks.

        Returns:
            DataloaderProxy: An instance of DataloaderProxy associated with the
                entities in the QuerySet.
        """
        return self.model.dl_proxy(self)
