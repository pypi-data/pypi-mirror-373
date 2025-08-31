import polars as pl
import polars_talib as pta

from typing import List, Optional

from proalgotrader_core.indicators.indicator import Indicator


class EMA(Indicator):
    """
    Exponential Moving Average (EMA).

    Parameters
    - timeperiod (int, default: 9): lookback window length
    - column (str, default: "close"): input column name
    - output_columns (list[str] | None): optional; must contain exactly 1 name.
      If omitted, the default name is `ema_{timeperiod}_{column}` (e.g. `ema_9_close`).

    Output/Response
    - `data` contains `current_candle` plus 1 EMA column.
    - Output column names: `[<ema_column>]`. Default: `ema_{timeperiod}_{column}`.
    """

    def __init__(
        self,
        timeperiod: int = 9,
        column: str = "close",
        output_columns: Optional[List[str]] = None,
    ) -> None:
        super().__init__()
        self.timeperiod = timeperiod
        self.column = column
        self.ema_col = f"ema_{timeperiod}_{column}"
        self._requested_output_columns = output_columns

    def build(self) -> pl.Expr:
        return pta.ema(real=pl.col(self.column), timeperiod=self.timeperiod)

    def expr(self) -> pl.Expr:
        return self.build().alias(self.ema_col)

    def _exprs(self) -> List[pl.Expr]:
        return [self.expr()]

    def output_columns(self) -> List[str]:
        return [self.ema_col]

    def required_columns(self) -> List[str]:
        return [self.column]

    def validate_output_columns(self) -> None:
        if self._requested_output_columns is not None:
            if len(self._requested_output_columns) != 1:
                raise ValueError(
                    "EMA expects exactly 1 output column name in 'output_columns'"
                )
            requested = self._requested_output_columns[0]
            if not isinstance(requested, str) or not requested:
                raise ValueError("EMA requires a non-empty single output column name")
            self.ema_col = requested

    def window_size(self) -> int:
        return self.timeperiod

    def warmup_size(self) -> int:
        # use extra history to stabilize EMA
        return self.timeperiod * 3
