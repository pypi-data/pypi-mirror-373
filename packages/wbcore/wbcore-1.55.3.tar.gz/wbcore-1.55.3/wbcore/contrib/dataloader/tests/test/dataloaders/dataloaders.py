import random
from typing import Iterator

from wbcore.contrib.dataloader.dataloaders import Dataloader

from .protocols import EntityTestDataProtocol


class RandomData(EntityTestDataProtocol, Dataloader):
    def data(self, n: int) -> Iterator[int]:
        for _ in self.entities:
            yield from map(lambda x: random.randint(0, 1000), range(n))


class RandomDataOver1000(EntityTestDataProtocol, Dataloader):
    def data(self, n: int) -> Iterator[int]:
        for _ in self.entities:
            yield from map(lambda x: random.randint(1000, 10000), range(n))
