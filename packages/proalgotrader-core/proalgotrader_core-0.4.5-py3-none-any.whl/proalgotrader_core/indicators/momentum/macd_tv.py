import polars as pl
import polars_talib as pta

from typing import List, Optional

from proalgotrader_core.indicators.indicator import Indicator


class MACD_TV(Indicator):
    """
    TradingView-style MACD wrapper with EMA lengths.

    Parameters
    - fastlength (int, default: 12)
    - slowlength (int, default: 26)
    - signal_smoothing (int, default: 9)
    - source (str, default: "close")
    - output_columns (list[str] | None): optional; must contain exactly 3 names in order [macd, signal, hist].
    """

    def __init__(
        self,
        fastlength: int = 12,
        slowlength: int = 26,
        signal_smoothing: int = 9,
        source: str = "close",
        output_columns: Optional[List[str]] = None,
        prefix: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.fastlength = fastlength
        self.slowlength = slowlength
        self.signal_smoothing = signal_smoothing
        self.source = source

        base = (
            prefix or f"macd_tv_{fastlength}_{slowlength}_{signal_smoothing}_{source}"
        )
        self.macd_col = base
        self.signal_col = f"{base}_signal"
        self.hist_col = f"{base}_hist"

        self._requested_output_columns = output_columns

    def build(self) -> pl.Expr:
        return pta.macd(
            real=pl.col(self.source),
            fastperiod=self.fastlength,
            slowperiod=self.slowlength,
            signalperiod=self.signal_smoothing,
        )

    def _exprs(self) -> List[pl.Expr]:
        macd_result = self.build()
        return [
            macd_result.struct.field("macd").alias(self.macd_col),
            macd_result.struct.field("macdsignal").alias(self.signal_col),
            macd_result.struct.field("macdhist").alias(self.hist_col),
        ]

    def output_columns(self) -> List[str]:
        return [self.macd_col, self.signal_col, self.hist_col]

    def required_columns(self) -> List[str]:
        return [self.source]

    def validate_output_columns(self) -> None:
        if self._requested_output_columns is not None:
            if len(self._requested_output_columns) != 3:
                raise ValueError(
                    "MACD_TV expects exactly 3 output column names in 'output_columns'"
                )
            macd_col, signal_col, hist_col = self._requested_output_columns
            cols = [macd_col, signal_col, hist_col]
            if any(not isinstance(c, str) or not c for c in cols):
                raise ValueError("MACD_TV requires three non-empty output column names")
            self.macd_col, self.signal_col, self.hist_col = cols

    def window_size(self) -> int:
        return max(self.fastlength, self.slowlength, self.signal_smoothing)

    def warmup_size(self) -> int:
        return self.window_size() * 3
