import polars as pl
import polars_talib as pta

from typing import List, Optional

from proalgotrader_core.indicators.indicator import Indicator


class ATR(Indicator):
    """
    Average True Range (ATR).

    Parameters
    - timeperiod (int, default: 14)
    - output_columns (list[str] | None): optional; must contain exactly 1 name.
      If omitted, the default name is `atr_{timeperiod}` (e.g. `atr_14`).

    Output/Response
    - `data` contains `current_candle` plus 1 ATR column.
    - Output column names: `[<atr>]`. Default: `atr_{timeperiod}`.
    """

    def __init__(
        self,
        timeperiod: int = 14,
        output_columns: Optional[List[str]] = None,
    ) -> None:
        super().__init__()
        self.timeperiod = timeperiod
        self.atr_col = f"atr_{timeperiod}"
        self._requested_output_columns = output_columns

    def build(self) -> pl.Expr:
        return pta.atr(
            high=pl.col("high"),
            low=pl.col("low"),
            close=pl.col("close"),
            timeperiod=self.timeperiod,
        )

    def _exprs(self) -> List[pl.Expr]:
        return [self.build().alias(self.atr_col)]

    def output_columns(self) -> List[str]:
        return [self.atr_col]

    def required_columns(self) -> List[str]:
        return ["high", "low", "close"]

    def validate_output_columns(self) -> None:
        if self._requested_output_columns is not None:
            if len(self._requested_output_columns) != 1:
                raise ValueError(
                    "ATR expects exactly 1 output column name in 'output_columns'"
                )
            requested = self._requested_output_columns[0]
            if not isinstance(requested, str) or not requested:
                raise ValueError("ATR requires a non-empty single output column name")
            self.atr_col = requested

    def window_size(self) -> int:
        return self.timeperiod

    def warmup_size(self) -> int:
        return self.timeperiod * 3
