from typing import Protocol
from proalgotrader_core.broker_symbol import BrokerSymbol
from proalgotrader_core.protocols.enums.position_type import PositionType

class PositionProtocol(Protocol):
    broker_symbol: BrokerSymbol
    position_type: PositionType
