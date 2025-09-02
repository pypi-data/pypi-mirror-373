from typing import Iterator

from wbcore.contrib.dataloader.dataloaders import DataloaderProxy

from .protocols import EntityTestDataProtocol


class EntityTestDataloaderProxy(DataloaderProxy[EntityTestDataProtocol]):
    def data(self, n: int) -> Iterator[int]:
        for dl in self.iterate_dataloaders("data"):
            yield from dl.data(n)
