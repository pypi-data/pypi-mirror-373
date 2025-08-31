from datetime import datetime

from proalgotrader_core.broker_symbol import BrokerSymbol


class Tick:
    def __init__(
        self,
        *,
        broker_symbol: BrokerSymbol,
        current_timestamp: int,
        ltp: float,
        total_volume: int,
    ) -> None:
        self.broker_symbol = broker_symbol
        self.current_timestamp = current_timestamp
        self.ltp = ltp
        self.total_volume = total_volume

        dt = datetime.fromtimestamp(current_timestamp)
        self.current_datetime = dt
