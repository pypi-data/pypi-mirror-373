"""Indicators package.

Provides category-grouped access to indicator classes for IDE autocomplete.

Policy summary:
- TV-first: Prefer TradingView-style variants (suffix `_TV`) when available.
- polars_talib-only: Implement all indicators using polars_talib; avoid custom logic
  unless explicitly requested for indicators missing in polars_talib (e.g., Supertrend).
- Avoid duplicates: When TV and TA are equivalent, expose only `_TV`.
- Custom indicators: Extend CustomIndicator class to implement any polars_talib indicator.

Example:
    from proalgotrader_core.indicators import CustomIndicator
    import polars_talib as pta
    import polars as pl

    class MyRSI(CustomIndicator):
        def __init__(self, timeperiod: int = 14):
            super().__init__()
            self.timeperiod = timeperiod

        def build(self, df: pl.DataFrame) -> List[pl.Expr]:
            return [pta.rsi(pl.col("close"), timeperiod=self.timeperiod).alias("my_rsi")]

        def output_columns(self) -> List[str]:
            return ["my_rsi"]

        def required_columns(self) -> List[str]:
            return ["close"]

Direct imports continue to work as well, e.g.:
    from proalgotrader_core.indicators.momentum.rsi import RSI
"""

from .momentum.rsi import RSI
from .momentum.macd import MACD
from .momentum.adx import ADX
from .momentum.stoch import STOCH
from .momentum.stochrsi import STOCHRSI
from .momentum.cci import CCI
from .momentum.williams_r import WilliamsR
from .momentum.aroon import AROON
from .momentum.adx_tv import ADX_TV
from .momentum.rsi_tv import RSI_TV
from .momentum.macd_tv import MACD_TV
from .momentum.stoch_tv import STOCH_TV

# Overlap
from .overlap.sma import SMA
from .overlap.ema import EMA
from .overlap.bbands import BBANDS
from .overlap.sma_tv import SMA_TV
from .overlap.ema_tv import EMA_TV
from .overlap.bbands_tv import BBANDS_TV

# Volatility
from .volatility.atr import ATR
from .volatility.atr_tv import ATR_TV
from .volume.obv import OBV
from .volume.vwap import VWAP
from .volume.mfi import MFI

# Custom indicators
from .custom_indicator import CustomIndicator

# Trend
from .trend.supertrend import Supertrend


class Indicators:
    class Momentum:
        RSI = RSI
        RSI_TV = RSI_TV
        MACD = MACD
        MACD_TV = MACD_TV
        ADX = ADX
        ADX_TV = ADX_TV
        STOCH = STOCH
        STOCH_TV = STOCH_TV
        STOCHRSI = STOCHRSI
        CCI = CCI
        WilliamsR = WilliamsR
        AROON = AROON

    class Overlap:
        SMA = SMA
        SMA_TV = SMA_TV
        EMA = EMA
        EMA_TV = EMA_TV
        BBANDS = BBANDS
        BBANDS_TV = BBANDS_TV

    class Volatility:
        ATR = ATR
        ATR_TV = ATR_TV

    class Trend:
        Supertrend = Supertrend

    class Volume:
        OBV = OBV
        VWAP = VWAP
        MFI = MFI

    class Custom:
        Indicator = CustomIndicator


__all__ = [
    "Indicators",
    "CustomIndicator",
]
