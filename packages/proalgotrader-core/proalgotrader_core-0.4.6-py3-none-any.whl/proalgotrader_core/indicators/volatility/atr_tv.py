import polars as pl
import polars_talib as pta

from typing import List, Optional

from proalgotrader_core.indicators.indicator import Indicator


class ATR_TV(Indicator):
    """
    TradingView-style ATR wrapper (Wilder's smoothing).

    Parameters
    - length (int, default: 14)
    - output_columns (list[str] | None): optional; must contain exactly 1 name.
    """

    def __init__(
        self,
        length: int = 14,
        output_columns: Optional[List[str]] = None,
    ) -> None:
        super().__init__()
        self.length = length
        self.atr_col = f"atr_tv_{length}"
        self._requested_output_columns = output_columns

    def build(self) -> pl.Expr:
        return pta.atr(
            high=pl.col("high"),
            low=pl.col("low"),
            close=pl.col("close"),
            timeperiod=self.length,
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
                    "ATR_TV expects exactly 1 output column name in 'output_columns'"
                )
            requested = self._requested_output_columns[0]
            if not isinstance(requested, str) or not requested:
                raise ValueError(
                    "ATR_TV requires a non-empty single output column name"
                )
            self.atr_col = requested

    def window_size(self) -> int:
        return self.length

    def warmup_size(self) -> int:
        return self.length * 3
