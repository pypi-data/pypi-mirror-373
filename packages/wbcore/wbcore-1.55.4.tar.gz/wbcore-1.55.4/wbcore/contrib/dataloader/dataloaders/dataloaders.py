from typing import TYPE_CHECKING, Generator

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from wbcore.contrib.dataloader.models.entities import Entity


class Dataloader:
    """Base class for dataloaders, providing a foundational structure for subclasses.

    This class includes an attribute `entities`, which is a Django queryset of Entity objects.
    It is designed to be subclassed by other classes which will implement specific methods.

    Attributes:
        entities (QuerySet[Entity]): A Django queryset of Entity objects.
    """

    def __init__(self, entities: "QuerySet[Entity]"):
        self.entities = entities
        super().__init__()

    @property
    def entity_ids(self) -> Generator[int, None, None]:
        return self.entities.values_list("id", flat=True)
