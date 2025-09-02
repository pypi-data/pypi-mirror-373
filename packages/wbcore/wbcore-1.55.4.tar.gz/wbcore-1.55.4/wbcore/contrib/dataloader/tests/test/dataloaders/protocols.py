from typing import Iterator, Protocol


class EntityTestDataProtocol(Protocol):
    def data(self, n: int) -> Iterator[int]: ...
