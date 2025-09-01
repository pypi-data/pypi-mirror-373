from enum import Enum


class CandleType(Enum):
    """Enum for different candle types supported by the chart system."""

    REGULAR = "regular"
    HEIKEN_ASHI = "heiken_ashi"
    RENKO = "renko"
