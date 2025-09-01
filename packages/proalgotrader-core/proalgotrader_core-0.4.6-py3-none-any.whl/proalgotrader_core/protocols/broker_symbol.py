from __future__ import annotations

from typing import Protocol


class BrokerSymbolProtocol(Protocol):
    exchange_token: int
    ltp: float
    total_volume: int
    subscribed: bool

    async def initialize(self) -> None: ...

    async def on_bar(self, ltp: float, total_volume: int) -> None: ...

    async def on_tick(self, tick: Any) -> None: ...

    def __str__(self) -> str: ...