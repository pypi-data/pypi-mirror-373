from abc import abstractmethod, ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from proalgotrader_core.algorithm import Algorithm


class SignalManagerProtocol(ABC):
    @abstractmethod
    def __init__(self, *, algorithm: "Algorithm", symbol_name: str) -> None: ...

    @abstractmethod
    async def initialize(self) -> None: ...

    @abstractmethod
    async def next(self) -> None: ...
