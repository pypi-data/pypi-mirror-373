from contextlib import suppress
from typing import TYPE_CHECKING, Generic, Iterator, Type, TypeVar

from django.utils.module_loading import import_string

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from wbcore.contrib.dataloader.dataloaders import Dataloader
    from wbcore.contrib.dataloader.models import Entity


T = TypeVar("T")


class DataloaderProxy(Generic[T]):
    """Manages and facilitates data loading from remote resources using dataloaders.

    This class serves as a proxy for various dataloader instances. Each dataloader is
    a subclass of `Dataloader`, designed to fetch data from a remote resource. The
    `DataloaderProxy` class enables the splicing of a queryset into parts, where each
    part uses a specific dataloader, thus abstracting the complexity of data fetching
    from multiple sources.

    The key responsibility of this class includes:
    - Splicing a queryset into segments, ensuring each segment uses the corresponding dataloader.
    - Providing an external interface to interact with different dataloaders, which allows
      for efficient data retrieval and processing.

    To utilize this class, it should be subclassed and associated with a Django model
    that can be processed by the `Dataloader` subclasses. This setup facilitates the
    dynamic and efficient retrieval of data, tailored to the specific needs of the application.

    Attributes:
        queryset (QuerySet[Entity]): A Django queryset that represents a collection of
            entities to be processed by the dataloaders.
    """

    def __init__(self, queryset: "QuerySet[Entity]"):
        self.queryset = queryset

    @staticmethod
    def load_dataloader(path: str) -> Type["Dataloader"]:
        """Loads a Dataloader object from a given path.

        This static method imports a Dataloader class from the specified path string.

        Args:
            path (str): The dot-delimited path to the Dataloader class to be imported.
                For example, 'module.submodule.ClassName'.

        Returns:
            Type["Dataloader"]: An instance of the Dataloader class loaded from the given path.

        Raises:
            ImportError: If the path does not correspond to a valid class.
        """
        return import_string(path)

    def iterate_dataloaders(self, dl_name: str) -> Iterator[T]:
        """Iterates over distinct dataloaders specified by a given name.

        This method retrieves a distinct list of paths associated with the specified
        dataloader name, then iterates over these paths. For each path, it loads a
        dataloader instance and filters the queryset based on the path, then yields
        this dataloader.

        The type `T` represents the specific type of the dataloaders that will be loaded and
        iterated over.

        Args:
            dl_name (str): The name of the dataloader to be iterated over. This name
                is used to construct the path key for querying distinct dataloader paths.

        Returns:
            Iterator[T]: An iterator of dataloader instances of the generic type `T` corresponding
            to each distinct path found in the queryset.
        """
        dl_path = f"dl_parameters__{dl_name}__path"
        for path in self.queryset.distinct(dl_path).values_list(dl_path, flat=True):
            with suppress(AttributeError):
                yield self.load_dataloader(path)(self.queryset.filter(**{dl_path: path}))
