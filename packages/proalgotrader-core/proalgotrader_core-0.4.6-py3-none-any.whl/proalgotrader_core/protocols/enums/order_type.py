from enum import Enum


class OrderType(Enum):
    LIMIT_ORDER = "LIMIT_ORDER"
    MARKET_ORDER = "MARKET_ORDER"
    STOP_ORDER = "STOP_ORDER"
    STOP_LIMIT_ORDER = "STOP_LIMIT_ORDER"
