from abc import ABC, abstractmethod
from typing import Dict, Optional
from proalgotrader_core.protocols.enums.candle_type import CandleType


class BaseCandleProcessor(ABC):
    """Base class for candle type processors."""

    def __init__(self):
        self.previous_close: Optional[float] = None
        self.previous_open: Optional[float] = None
        self.previous_high: Optional[float] = None
        self.previous_low: Optional[float] = None

    @abstractmethod
    async def process_candle(
        self,
        open_price: float,
        high_price: float,
        low_price: float,
        close_price: float,
        volume: int,
    ) -> Dict[str, float]:
        """Process candle data and return OHLCV values."""
        pass

    @abstractmethod
    async def process_new_candle(self, ltp: float, volume: int) -> Dict[str, float]:
        """Process new candle data when starting a new candle."""
        pass

    @abstractmethod
    async def process_existing_candle(
        self,
        current_open: float,
        current_high: float,
        current_low: float,
        current_close: float,
        ltp: float,
        volume: int,
    ) -> Dict[str, float]:
        """Process existing candle data when updating current candle."""
        pass


class RegularCandleProcessor(BaseCandleProcessor):
    """Processor for regular candlestick charts."""

    async def process_candle(
        self,
        open_price: float,
        high_price: float,
        low_price: float,
        close_price: float,
        volume: int,
    ) -> Dict[str, float]:
        """Process regular candle data."""
        return {
            "open": round(open_price, 2),
            "high": round(high_price, 2),
            "low": round(low_price, 2),
            "close": round(close_price, 2),
            "volume": volume,
        }

    async def process_new_candle(self, ltp: float, volume: int) -> Dict[str, float]:
        """Process new regular candle."""
        rounded_ltp = round(ltp, 2)
        return {
            "open": rounded_ltp,
            "high": rounded_ltp,
            "low": rounded_ltp,
            "close": rounded_ltp,
            "volume": volume,
        }

    async def process_existing_candle(
        self,
        current_open: float,
        current_high: float,
        current_low: float,
        current_close: float,
        ltp: float,
        volume: int,
    ) -> Dict[str, float]:
        """Process existing regular candle."""
        return {
            "open": round(current_open, 2),
            "high": round(max(current_high, ltp), 2),
            "low": round(min(current_low, ltp), 2),
            "close": round(ltp, 2),
            "volume": volume,
        }


class HeikenAshiCandleProcessor(BaseCandleProcessor):
    """Processor for Heiken Ashi candlestick charts."""

    async def process_candle(
        self,
        open_price: float,
        high_price: float,
        low_price: float,
        close_price: float,
        volume: int,
    ) -> Dict[str, float]:
        """Process Heiken Ashi candle data."""
        # Heiken Ashi formulas:
        # HA_Close = (Open + High + Low + Close) / 4
        # HA_Open = (Previous HA_Open + Previous HA_Close) / 2
        # HA_High = max(High, HA_Open, HA_Close)
        # HA_Low = min(Low, HA_Open, HA_Close)

        ha_close = (open_price + high_price + low_price + close_price) / 4

        if self.previous_open is None or self.previous_close is None:
            # For the first candle, use regular OHLC as initial values
            ha_open = open_price
        else:
            ha_open = (self.previous_open + self.previous_close) / 2

        ha_high = max(high_price, ha_open, ha_close)
        ha_low = min(low_price, ha_open, ha_close)

        # Update previous values for next calculation
        self.previous_open = ha_open
        self.previous_close = ha_close

        return {
            "open": round(ha_open, 2),
            "high": round(ha_high, 2),
            "low": round(ha_low, 2),
            "close": round(ha_close, 2),
            "volume": volume,
        }

    async def process_new_candle(self, ltp: float, volume: int) -> Dict[str, float]:
        """Process new Heiken Ashi candle."""
        # For new candle, calculate Heiken Ashi values
        ha_close = ltp  # For single price, close = ltp

        if self.previous_open is None or self.previous_close is None:
            # First candle - use ltp as both open and close
            ha_open = ltp
        else:
            ha_open = (self.previous_open + self.previous_close) / 2

        ha_high = max(ltp, ha_open, ha_close)
        ha_low = min(ltp, ha_open, ha_close)

        # Update previous values
        self.previous_open = ha_open
        self.previous_close = ha_close

        return {
            "open": round(ha_open, 2),
            "high": round(ha_high, 2),
            "low": round(ha_low, 2),
            "close": round(ha_close, 2),
            "volume": volume,
        }

    async def process_existing_candle(
        self,
        current_open: float,
        current_high: float,
        current_low: float,
        current_close: float,
        ltp: float,
        volume: int,
    ) -> Dict[str, float]:
        """Process existing Heiken Ashi candle."""
        # Recalculate Heiken Ashi values with new close price
        # Use the current OHLC values but update close to ltp
        new_high = max(current_high, ltp)
        new_low = min(current_low, ltp)

        ha_close = (current_open + new_high + new_low + ltp) / 4

        if self.previous_open is None or self.previous_close is None:
            ha_open = current_open
        else:
            ha_open = (self.previous_open + self.previous_close) / 2

        ha_high = max(new_high, ha_open, ha_close)
        ha_low = min(new_low, ha_open, ha_close)

        # Update previous values
        self.previous_open = ha_open
        self.previous_close = ha_close

        return {
            "open": round(ha_open, 2),
            "high": round(ha_high, 2),
            "low": round(ha_low, 2),
            "close": round(ha_close, 2),
            "volume": volume,
        }


class RenkoCandleProcessor(BaseCandleProcessor):
    """Processor for Renko charts."""

    def __init__(self, brick_size: float = 1.0):
        super().__init__()
        self.brick_size = brick_size
        self.current_brick_open: Optional[float] = None
        self.current_brick_close: Optional[float] = None
        self.brick_direction: Optional[str] = None  # "up" or "down"

    async def process_candle(
        self,
        open_price: float,
        high_price: float,
        low_price: float,
        close_price: float,
        volume: int,
    ) -> Dict[str, float]:
        """Process Renko candle data."""
        # Renko charts are based on price movement, not time
        # Each brick represents a fixed price movement
        return {
            "open": round(open_price, 2),
            "high": round(high_price, 2),
            "low": round(low_price, 2),
            "close": round(close_price, 2),
            "volume": volume,
        }

    async def process_new_candle(self, ltp: float, volume: int) -> Dict[str, float]:
        """Process new Renko candle."""
        if self.current_brick_open is None:
            # First brick
            self.current_brick_open = ltp
            self.current_brick_close = ltp
            self.brick_direction = None
        else:
            # Check if price movement warrants a new brick
            if self.current_brick_close is not None:
                price_change = ltp - self.current_brick_close

                if abs(price_change) >= self.brick_size:
                    # Create new brick
                    if price_change > 0:
                        # Upward brick
                        self.current_brick_open = self.current_brick_close
                        self.current_brick_close = (
                            self.current_brick_open + self.brick_size
                        )
                        self.brick_direction = "up"
                    else:
                        # Downward brick
                        self.current_brick_open = self.current_brick_close
                        self.current_brick_close = (
                            self.current_brick_open - self.brick_size
                        )
                        self.brick_direction = "down"
                # No new brick, use current brick values

        # Ensure we have valid values
        brick_open = (
            self.current_brick_open if self.current_brick_open is not None else ltp
        )
        brick_close = (
            self.current_brick_close if self.current_brick_close is not None else ltp
        )

        return {
            "open": round(brick_open, 2),
            "high": round(max(brick_open, brick_close), 2),
            "low": round(min(brick_open, brick_close), 2),
            "close": round(brick_close, 2),
            "volume": volume,
        }

    async def process_existing_candle(
        self,
        current_open: float,
        current_high: float,
        current_low: float,
        current_close: float,
        ltp: float,
        volume: int,
    ) -> Dict[str, float]:
        """Process existing Renko candle."""
        # For Renko, we need to check if price movement creates new bricks
        if self.current_brick_close is not None:
            price_change = ltp - self.current_brick_close

            if abs(price_change) >= self.brick_size:
                # Create new brick
                if price_change > 0:
                    # Upward brick
                    self.current_brick_open = self.current_brick_close
                    self.current_brick_close = self.current_brick_open + self.brick_size
                    self.brick_direction = "up"
                else:
                    # Downward brick
                    self.current_brick_open = self.current_brick_close
                    self.current_brick_close = self.current_brick_open - self.brick_size
                    self.brick_direction = "down"

        # Ensure we have valid values
        brick_open = (
            self.current_brick_open
            if self.current_brick_open is not None
            else current_open
        )
        brick_close = (
            self.current_brick_close
            if self.current_brick_close is not None
            else current_close
        )

        return {
            "open": round(brick_open, 2),
            "high": round(max(brick_open, brick_close), 2),
            "low": round(min(brick_open, brick_close), 2),
            "close": round(brick_close, 2),
            "volume": volume,
        }


class CandleProcessorFactory:
    """Factory for creating candle processors based on candle type."""

    @staticmethod
    async def create_processor(
        candle_type: CandleType, **kwargs
    ) -> BaseCandleProcessor:
        """Create a candle processor based on the candle type."""
        if candle_type == CandleType.REGULAR:
            return RegularCandleProcessor()
        elif candle_type == CandleType.HEIKEN_ASHI:
            return HeikenAshiCandleProcessor()
        elif candle_type == CandleType.RENKO:
            brick_size = kwargs.get("brick_size", 1.0)
            return RenkoCandleProcessor(brick_size=brick_size)
        else:
            raise ValueError(f"Unsupported candle type: {candle_type}")
