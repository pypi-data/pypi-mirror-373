from abc import abstractmethod
from typing import Protocol
from proalgotrader_core.broker_symbol import BrokerSymbol


class AlgorithmProtocol(Protocol):
    @abstractmethod
    async def initialize(self) -> None: ...

    @abstractmethod
    async def next(self) -> None: ...

    async def add_equity(self, *, symbol_name: str) -> BrokerSymbol: ...
