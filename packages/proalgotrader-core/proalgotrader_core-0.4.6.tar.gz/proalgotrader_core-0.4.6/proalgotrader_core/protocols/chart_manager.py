from __future__ import annotations

from typing import Protocol, Tuple
from datetime import datetime, timedelta


class ChartManagerProtocol(Protocol):
    def get_current_candle(self, timeframe: timedelta) -> datetime: ...

    async def fetch_ranges(self, timeframe: timedelta) -> Tuple[datetime, datetime]: ...
