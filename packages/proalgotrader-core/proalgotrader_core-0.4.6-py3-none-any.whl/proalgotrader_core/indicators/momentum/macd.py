import polars as pl
import polars_talib as pta

from typing import List, Optional

from proalgotrader_core.indicators.indicator import Indicator


class MACD(Indicator):
    """
    Moving Average Convergence/Divergence (MACD).

    Parameters
    - column (str, default: "close"): input column name
    - fastperiod (int, default: 12): fast EMA period
    - slowperiod (int, default: 26): slow EMA period
    - signalperiod (int, default: 9): signal EMA period
    - output_columns (list[str] | None): optional; must contain exactly 3 names
      in this order: [macd, signal, hist]. If omitted, defaults are derived as
      `macd_{fast}_{slow}_{signal}_{column}`, plus `_signal`, `_hist`.
    - prefix (str | None): optional base for default names when `output_columns`
      is not provided.

    Output/Response
    - When computed, results are exposed via `data` as a `pl.DataFrame` that
      contains `current_candle` plus 3 additional MACD columns.
    - Output column names: `[<macd>, <signal>, <hist>]`.
      Defaults example: `macd_12_26_9_close`, `macd_12_26_9_close_signal`,
      `macd_12_26_9_close_hist`.
    """

    def __init__(
        self,
        column: str = "close",
        fastperiod: int = 12,
        slowperiod: int = 26,
        signalperiod: int = 9,
        output_columns: Optional[List[str]] = None,
        prefix: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.column = column
        self.fastperiod = fastperiod
        self.slowperiod = slowperiod
        self.signalperiod = signalperiod

        base = prefix or f"macd_{fastperiod}_{slowperiod}_{signalperiod}_{column}"
        self.macd_col = f"{base}"
        self.signal_col = f"{base}_signal"
        self.hist_col = f"{base}_hist"

        self._requested_output_columns = output_columns

    def build(self) -> pl.Expr:
        return pta.macd(
            real=pl.col(self.column),
            fastperiod=self.fastperiod,
            slowperiod=self.slowperiod,
            signalperiod=self.signalperiod,
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
        return [self.column]

    def validate_output_columns(self) -> None:
        if self._requested_output_columns is not None:
            if len(self._requested_output_columns) != 3:
                raise ValueError(
                    "MACD expects exactly 3 output column names in 'output_columns'"
                )
            macd_col, signal_col, hist_col = self._requested_output_columns
            cols = [macd_col, signal_col, hist_col]
            if any(not isinstance(c, str) or not c for c in cols):
                raise ValueError("MACD requires three non-empty output column names")
            self.macd_col, self.signal_col, self.hist_col = cols

    def window_size(self) -> int:
        return max(self.fastperiod, self.slowperiod, self.signalperiod)

    def warmup_size(self) -> int:
        return self.window_size() * 3
