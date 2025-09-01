from abc import abstractmethod, ABC

from proalgotrader_core.protocols.algorithm import AlgorithmProtocol


class SignalManagerProtocol(ABC):
    @abstractmethod
    def __init__(self, *, algorithm: AlgorithmProtocol, symbol_name: str) -> None: ...

    @abstractmethod
    async def initialize(self) -> None: ...

    @abstractmethod
    async def next(self) -> None: ...
