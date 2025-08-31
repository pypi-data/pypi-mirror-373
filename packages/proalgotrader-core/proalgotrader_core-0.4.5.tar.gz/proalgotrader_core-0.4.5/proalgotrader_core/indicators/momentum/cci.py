import polars as pl
import polars_talib as pta

from typing import List, Optional

from proalgotrader_core.indicators.indicator import Indicator


class CCI(Indicator):
    """
    Commodity Channel Index (CCI).

    Parameters
    - timeperiod (int, default: 14)
    - column (str, default: "close"): input column name
    - output_columns (list[str] | None): optional; must contain exactly 1 name.
      If omitted, the default name is `cci_{timeperiod}_{column}` (e.g. `cci_14_close`).

    Output/Response
    - `data` contains `current_candle` plus 1 CCI column.
    - Output column names: `[<cci>]`. Default: `cci_{timeperiod}_{column}`.
    """

    def __init__(
        self,
        timeperiod: int = 14,
        column: str = "close",
        output_columns: Optional[List[str]] = None,
    ) -> None:
        super().__init__()
        self.timeperiod = timeperiod
        self.column = column
        self.cci_col = f"cci_{timeperiod}_{column}"
        self._requested_output_columns = output_columns

    def build(self) -> pl.Expr:
        return pta.cci(
            high=pl.col("high"),
            low=pl.col("low"),
            close=pl.col("close"),
            timeperiod=self.timeperiod,
        )

    def _exprs(self) -> List[pl.Expr]:
        return [self.build().alias(self.cci_col)]

    def output_columns(self) -> List[str]:
        return [self.cci_col]

    def required_columns(self) -> List[str]:
        return ["high", "low", self.column]

    def validate_output_columns(self) -> None:
        if self._requested_output_columns is not None:
            if len(self._requested_output_columns) != 1:
                raise ValueError(
                    "CCI expects exactly 1 output column name in 'output_columns'"
                )
            requested = self._requested_output_columns[0]
            if not isinstance(requested, str) or not requested:
                raise ValueError("CCI requires a non-empty single output column name")
            self.cci_col = requested

    def window_size(self) -> int:
        return self.timeperiod

    def warmup_size(self) -> int:
        return self.timeperiod * 3
