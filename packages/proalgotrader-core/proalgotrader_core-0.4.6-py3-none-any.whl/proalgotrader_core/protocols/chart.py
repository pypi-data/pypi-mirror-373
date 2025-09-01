from __future__ import annotations

from typing import Protocol, Any, Tuple
from datetime import datetime, date, timedelta


class ChartManagerProtocol(Protocol):
    def get_current_candle(self, timeframe: timedelta) -> datetime: ...

    async def fetch_ranges(self, timeframe: timedelta) -> Tuple[datetime, datetime]: ...


class AlgoSessionProtocol(Protocol):
    current_datetime: datetime
    current_date: date


class TickProtocol(Protocol):
    ltp: float
    total_volume: int
    current_timestamp: Any
    current_datetime: datetime
    broker_symbol: Any
