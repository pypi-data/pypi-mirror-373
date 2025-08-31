import polars as pl
import polars_talib as pta

from typing import List, Optional

from proalgotrader_core.indicators.indicator import Indicator


class RSI_TV(Indicator):
    """
    TradingView-style RSI wrapper.

    Parameters
    - length (int, default: 14): RSI lookback length
    - source (str, default: "close"): input column name
    - output_columns (list[str] | None): optional; must contain exactly 1 name.
      If omitted, default is `rsi_tv_{length}_{source}`.
    """

    def __init__(
        self,
        length: int = 14,
        source: str = "close",
        output_columns: Optional[List[str]] = None,
    ) -> None:
        super().__init__()
        self.length = length
        self.source = source
        self.rsi_col = f"rsi_tv_{length}_{source}"
        self._requested_output_columns = output_columns

    def build(self) -> pl.Expr:
        return pta.rsi(real=pl.col(self.source), timeperiod=self.length)

    def _exprs(self) -> List[pl.Expr]:
        return [self.build().alias(self.rsi_col)]

    def output_columns(self) -> List[str]:
        return [self.rsi_col]

    def required_columns(self) -> List[str]:
        return [self.source]

    def validate_output_columns(self) -> None:
        if self._requested_output_columns is not None:
            if len(self._requested_output_columns) != 1:
                raise ValueError(
                    "RSI_TV expects exactly 1 output column name in 'output_columns'"
                )
            requested = self._requested_output_columns[0]
            if not isinstance(requested, str) or not requested:
                raise ValueError(
                    "RSI_TV requires a non-empty single output column name"
                )
            self.rsi_col = requested

    def window_size(self) -> int:
        return self.length

    def warmup_size(self) -> int:
        return self.length * 3
