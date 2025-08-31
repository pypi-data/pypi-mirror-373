from abc import abstractmethod, ABC
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from proalgotrader_core.algorithm import Algorithm
    from proalgotrader_core.position import Position


class PositionManagerProtocol(ABC):
    @abstractmethod
    def __init__(self, algorithm: "Algorithm") -> None: ...

    @abstractmethod
    async def initialize(self) -> None: ...

    @abstractmethod
    async def on_position_open(self, position: "Position") -> None: ...

    @abstractmethod
    async def on_position_closed(self, position: "Position") -> None: ...

    @abstractmethod
    async def next(self) -> None: ...
