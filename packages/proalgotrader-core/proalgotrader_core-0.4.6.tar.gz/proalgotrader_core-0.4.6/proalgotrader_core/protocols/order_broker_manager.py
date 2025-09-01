from typing import Protocol, Any, Dict

from proalgotrader_core.protocols.broker_symbol import BrokerSymbolProtocol


class NotificationManagerProtocol(Protocol):
    async def send_message(self, data: Dict[str, Any]) -> None:
        ...


class BaseOrderBrokerManagerProtocol(Protocol):
    notification_manager: NotificationManagerProtocol

    async def fetch_quotes(self, broker_symbol: "BrokerSymbolProtocol") -> None:
        ...

    async def subscribe(self, broker_symbol: "BrokerSymbolProtocol") -> None:
        ...
