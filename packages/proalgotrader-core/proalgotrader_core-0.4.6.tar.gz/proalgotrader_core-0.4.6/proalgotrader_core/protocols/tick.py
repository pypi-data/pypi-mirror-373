from __future__ import annotations

from typing import Protocol, Any
from datetime import datetime


class TickProtocol(Protocol):
    ltp: float
    total_volume: int
    current_timestamp: Any
    current_datetime: datetime
    broker_symbol: Any
