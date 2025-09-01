from __future__ import annotations

from typing import Protocol
from datetime import datetime, date


class AlgoSessionProtocol(Protocol):
    current_datetime: datetime
    current_date: date
