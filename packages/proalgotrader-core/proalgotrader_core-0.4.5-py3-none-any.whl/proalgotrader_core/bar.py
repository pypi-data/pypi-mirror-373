from datetime import datetime
from typing import Any, List

from proalgotrader_core.broker_symbol import BrokerSymbol


class Bar:
    def __init__(
        self,
        *,
        broker_symbol: BrokerSymbol,
        current_timestamp: int,
        open: float,
        high: float,
        low: float,
        close: float,
        volume: int = 0,
    ) -> None:
        self.broker_symbol = broker_symbol
        self.current_timestamp = current_timestamp
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume

        dt = datetime.fromtimestamp(current_timestamp)
        self.current_candle = dt
        self.current_datetime = dt

    def get_item(self) -> List[Any]:
        return [
            self.current_candle,
            self.current_timestamp,
            self.current_datetime,
            self.broker_symbol,
            self.open,
            self.high,
            self.low,
            self.close,
            self.volume,
        ]
