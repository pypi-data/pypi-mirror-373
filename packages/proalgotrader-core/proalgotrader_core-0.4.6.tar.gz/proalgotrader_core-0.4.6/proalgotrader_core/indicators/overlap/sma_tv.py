import polars as pl
import polars_talib as pta

from typing import List, Optional

from proalgotrader_core.indicators.indicator import Indicator


class SMA_TV(Indicator):
    """
    TradingView-style SMA wrapper.

    Parameters
    - length (int, default: 9)
    - source (str, default: "close")
    - output_columns (list[str] | None): optional; must contain exactly 1 name.
    """

    def __init__(
        self,
        length: int = 9,
        source: str = "close",
        output_columns: Optional[List[str]] = None,
    ) -> None:
        super().__init__()
        self.length = length
        self.source = source
        self.sma_col = f"sma_tv_{length}_{source}"
        self._requested_output_columns = output_columns

    def build(self) -> pl.Expr:
        return pta.sma(real=pl.col(self.source), timeperiod=self.length)

    def _exprs(self) -> List[pl.Expr]:
        return [self.build().alias(self.sma_col)]

    def output_columns(self) -> List[str]:
        return [self.sma_col]

    def required_columns(self) -> List[str]:
        return [self.source]

    def validate_output_columns(self) -> None:
        if self._requested_output_columns is not None:
            if len(self._requested_output_columns) != 1:
                raise ValueError(
                    "SMA_TV expects exactly 1 output column name in 'output_columns'"
                )
            requested = self._requested_output_columns[0]
            if not isinstance(requested, str) or not requested:
                raise ValueError(
                    "SMA_TV requires a non-empty single output column name"
                )
            self.sma_col = requested

    def window_size(self) -> int:
        return self.length

    def warmup_size(self) -> int:
        return 0
