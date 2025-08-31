import polars as pl
import polars_talib as pta

from typing import List, Optional

from proalgotrader_core.indicators.indicator import Indicator


class AROON(Indicator):
    """
    Aroon.

    Parameters
    - timeperiod (int, default: 14)
    - output_columns (list[str] | None): optional; must contain exactly 2 names.
      If omitted, the default names are `aroon_down_{timeperiod}` and `aroon_up_{timeperiod}` (e.g. `aroon_down_14`, `aroon_up_14`).

    Output/Response
    - `data` contains `current_candle` plus 2 Aroon columns.
    - Output column names: `[<aroon_down>, <aroon_up>]`. Default: `aroon_down_{timeperiod}`, `aroon_up_{timeperiod}`.
    """

    def __init__(
        self,
        timeperiod: int = 14,
        output_columns: Optional[List[str]] = None,
    ) -> None:
        super().__init__()
        self.timeperiod = timeperiod
        self.aroon_down_col = f"aroon_down_{timeperiod}"
        self.aroon_up_col = f"aroon_up_{timeperiod}"
        self._requested_output_columns = output_columns

    def _exprs(self) -> List[pl.Expr]:
        aroon_result = self.build()

        return [
            aroon_result.struct.field("aroon_down").alias(self.aroon_down_col),
            aroon_result.struct.field("aroon_up").alias(self.aroon_up_col),
        ]

    def build(self) -> pl.Expr:
        return pta.aroon(
            high=pl.col("high"), low=pl.col("low"), timeperiod=self.timeperiod
        )

    def output_columns(self) -> List[str]:
        return [self.aroon_down_col, self.aroon_up_col]

    def required_columns(self) -> List[str]:
        return ["high", "low"]

    def validate_output_columns(self) -> None:
        if self._requested_output_columns is not None:
            if len(self._requested_output_columns) != 2:
                raise ValueError(
                    "AROON expects exactly 2 output column names in 'output_columns'"
                )
            requested_down, requested_up = self._requested_output_columns
            if not isinstance(requested_down, str) or not requested_down:
                raise ValueError("AROON requires non-empty output column names")
            if not isinstance(requested_up, str) or not requested_up:
                raise ValueError("AROON requires non-empty output column names")
            self.aroon_down_col = requested_down
            self.aroon_up_col = requested_up

    def window_size(self) -> int:
        return self.timeperiod

    def warmup_size(self) -> int:
        return self.timeperiod * 3
