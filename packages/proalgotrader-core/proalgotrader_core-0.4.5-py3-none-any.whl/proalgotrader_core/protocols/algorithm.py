from abc import abstractmethod
from typing import Protocol, Optional, TYPE_CHECKING
from proalgotrader_core.broker_symbol import BrokerSymbol
from proalgotrader_core.api import Api

if TYPE_CHECKING:
    from proalgotrader_core.protocols.position_manager import PositionManagerProtocol
    from proalgotrader_core.order_broker_managers.base_order_broker_manager import (
        BaseOrderBrokerManager,
    )


class AlgorithmProtocol(Protocol):
    position_manager: Optional["PositionManagerProtocol"]
    order_broker_manager: "BaseOrderBrokerManager"
    api: Api

    @abstractmethod
    async def initialize(self) -> None: ...

    @abstractmethod
    async def next(self) -> None: ...

    async def add_equity(self, *, symbol_name: str) -> BrokerSymbol: ...
