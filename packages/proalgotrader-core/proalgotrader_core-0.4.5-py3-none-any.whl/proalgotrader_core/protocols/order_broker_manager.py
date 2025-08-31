from typing import Protocol, Any, Dict

if "BrokerSymbol" not in globals():
    from proalgotrader_core.broker_symbol import BrokerSymbol

class NotificationManagerProtocol(Protocol):
    async def send_message(self, data: Dict[str, Any]) -> None:
        ...

class BaseOrderBrokerManagerProtocol(Protocol):
    notification_manager: NotificationManagerProtocol

    async def fetch_quotes(self, broker_symbol: "BrokerSymbol") -> None:
        ...

    async def subscribe(self, broker_symbol: "BrokerSymbol") -> None:
        ...
