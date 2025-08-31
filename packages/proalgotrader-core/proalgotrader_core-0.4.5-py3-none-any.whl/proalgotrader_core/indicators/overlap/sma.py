import polars as pl
import polars_talib as pta

from typing import Optional, List

from proalgotrader_core.indicators.indicator import Indicator


class SMA(Indicator):
    """
    Simple Moving Average (SMA).

    Parameters
    - period (int, default: 9): lookback window length
    - column (str, default: "close"): input column name
    - output_columns (list[str] | None): optional; must contain exactly 1 name.
      If omitted, the default name is `sma_{period}_{column}` (e.g. `sma_9_close`).

    Output/Response
    - When computed, results are exposed via `data` as a `pl.DataFrame` that
      contains `current_candle` plus 1 additional SMA column.
    - Output column names: `[<sma_column>]`. Default: `sma_{period}_{column}`.
    """

    def __init__(
        self,
        period: int = 9,
        column: str = "close",
        output_columns: Optional[List[str]] = None,
    ) -> None:
        super().__init__()
        self.period = period
        self.column = column
        self.output_column = f"sma_{period}_{column}"
        self._requested_output_columns = output_columns

    def build(self) -> pl.Expr:
        return pta.sma(real=pl.col(self.column), timeperiod=self.period)

    def expr(self) -> pl.Expr:
        return self.build().alias(self.output_column)

    def _exprs(self) -> List[pl.Expr]:
        return [self.expr()]

    def output_columns(self) -> List[str]:
        return [self.output_column]

    def required_columns(self) -> List[str]:
        return [self.column]

    def validate_output_columns(self) -> None:
        if self._requested_output_columns is not None:
            if len(self._requested_output_columns) != 1:
                raise ValueError(
                    "SMA expects exactly 1 output column name in 'output_columns'"
                )
            requested = self._requested_output_columns[0]
            if not isinstance(requested, str) or not requested:
                raise ValueError("SMA requires a non-empty single output column name")
            self.output_column = requested

    def window_size(self) -> int:
        return self.period

    def warmup_size(self) -> int:
        return 0
