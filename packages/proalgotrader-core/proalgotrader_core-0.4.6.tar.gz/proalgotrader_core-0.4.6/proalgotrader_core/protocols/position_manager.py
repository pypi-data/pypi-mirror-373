from abc import abstractmethod, ABC

from proalgotrader_core.protocols.algorithm import AlgorithmProtocol
from proalgotrader_core.protocols.position import PositionProtocol


class PositionManagerProtocol(ABC):
    @abstractmethod
    def __init__(self, algorithm: AlgorithmProtocol) -> None: ...

    @abstractmethod
    async def initialize(self) -> None: ...

    @abstractmethod
    async def on_position_open(self, position: PositionProtocol) -> None: ...

    @abstractmethod
    async def on_position_closed(self, position: PositionProtocol) -> None: ...

    @abstractmethod
    async def next(self) -> None: ...
