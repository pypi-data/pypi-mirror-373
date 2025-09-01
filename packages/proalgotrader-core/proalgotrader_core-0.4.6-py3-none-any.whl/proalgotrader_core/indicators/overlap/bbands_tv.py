import polars as pl
import polars_talib as pta

from typing import List, Optional

from proalgotrader_core.indicators.indicator import Indicator


class BBANDS_TV(Indicator):
    """
    TradingView-style Bollinger Bands.

    Parameters
    - length (int, default: 20)
    - mult (float, default: 2.0)
    - source (str, default: "close")
    - output_columns (list[str] | None): optional; must contain exactly 3 names [upper, middle, lower].
    """

    def __init__(
        self,
        length: int = 20,
        mult: float = 2.0,
        source: str = "close",
        output_columns: Optional[List[str]] = None,
    ) -> None:
        super().__init__()
        self.length = length
        self.mult = mult
        self.source = source

        base = f"bbands_tv_{length}_{source}"
        self.upper_col = base
        self.middle_col = f"{base}_middle"
        self.lower_col = f"{base}_lower"

        self._requested_output_columns = output_columns

    def build(self) -> pl.Expr:
        return pta.bbands(
            real=pl.col(self.source),
            timeperiod=self.length,
            nbdevup=self.mult,
            nbdevdn=self.mult,
        )

    def _exprs(self) -> List[pl.Expr]:
        bb = self.build().alias("__bbands_tv_struct__")
        return [
            bb.struct.field("upperband").alias(self.upper_col),
            bb.struct.field("middleband").alias(self.middle_col),
            bb.struct.field("lowerband").alias(self.lower_col),
        ]

    def output_columns(self) -> List[str]:
        return [self.upper_col, self.middle_col, self.lower_col]

    def required_columns(self) -> List[str]:
        return [self.source]

    def validate_output_columns(self) -> None:
        if self._requested_output_columns is not None:
            if len(self._requested_output_columns) != 3:
                raise ValueError(
                    "BBANDS_TV expects exactly 3 output column names in 'output_columns'"
                )
            upper, middle, lower = self._requested_output_columns
            cols = [upper, middle, lower]
            if any(not isinstance(c, str) or not c for c in cols):
                raise ValueError(
                    "BBANDS_TV requires three non-empty output column names"
                )
            self.upper_col, self.middle_col, self.lower_col = cols

    def window_size(self) -> int:
        return self.length

    def warmup_size(self) -> int:
        return 0
