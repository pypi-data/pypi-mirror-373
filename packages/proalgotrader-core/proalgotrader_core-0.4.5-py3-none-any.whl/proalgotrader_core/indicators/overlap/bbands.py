import polars as pl
import polars_talib as pta

from typing import List, Optional

from proalgotrader_core.indicators.indicator import Indicator


class BBANDS(Indicator):
    """
    Bollinger Bands (BBANDS).

    Parameters
    - timeperiod (int, default: 20)
    - nbdevup (float, default: 2.0)
    - nbdevdn (float, default: 2.0)
    - column (str, default: "close"): input column name
    - output_columns (list[str] | None): optional; must contain exactly 3 names
      in this order: [upper, middle, lower]. If omitted, defaults are derived as
      `bbands_{timeperiod}_{column}` plus `_middle`, `_lower` suffixes.

    Output/Response
    - `data` contains `current_candle` plus 3 columns in order: [upper, middle, lower].
    - Default names example: `bbands_20_close`, `bbands_20_close_middle`, `bbands_20_close_lower`.
    """

    def __init__(
        self,
        timeperiod: int = 20,
        nbdevup: float = 2.0,
        nbdevdn: float = 2.0,
        column: str = "close",
        output_columns: Optional[List[str]] = None,
    ) -> None:
        super().__init__()
        self.timeperiod = timeperiod
        self.nbdevup = nbdevup
        self.nbdevdn = nbdevdn
        self.column = column

        base = f"bbands_{timeperiod}_{column}"
        self.upper_col = base
        self.middle_col = f"{base}_middle"
        self.lower_col = f"{base}_lower"

        self._requested_output_columns = output_columns

    def build(self) -> pl.Expr:
        return pta.bbands(
            real=pl.col(self.column),
            timeperiod=self.timeperiod,
            nbdevup=self.nbdevup,
            nbdevdn=self.nbdevdn,
        )

    def _bbands_struct_expr(self) -> pl.Expr:
        return self.build()

    def _exprs(self) -> List[pl.Expr]:
        bb = self._bbands_struct_expr().alias("__bbands_struct__")
        return [
            bb.struct.field("upperband").alias(self.upper_col),
            bb.struct.field("middleband").alias(self.middle_col),
            bb.struct.field("lowerband").alias(self.lower_col),
        ]

    def output_columns(self) -> List[str]:
        return [self.upper_col, self.middle_col, self.lower_col]

    def required_columns(self) -> List[str]:
        return [self.column]

    def validate_output_columns(self) -> None:
        if self._requested_output_columns is not None:
            if len(self._requested_output_columns) != 3:
                raise ValueError(
                    "BBANDS expects exactly 3 output column names in 'output_columns'"
                )
            upper, middle, lower = self._requested_output_columns
            cols = [upper, middle, lower]
            if any(not isinstance(c, str) or not c for c in cols):
                raise ValueError("BBANDS requires three non-empty output column names")
            self.upper_col, self.middle_col, self.lower_col = cols

    def window_size(self) -> int:
        return self.timeperiod

    def warmup_size(self) -> int:
        return 0
