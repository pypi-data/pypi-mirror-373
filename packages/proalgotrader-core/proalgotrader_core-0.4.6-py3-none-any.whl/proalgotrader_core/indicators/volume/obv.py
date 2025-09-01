import polars as pl
import polars_talib as pta

from typing import List, Optional

from proalgotrader_core.indicators.indicator import Indicator


class OBV(Indicator):
    """
    On Balance Volume (OBV).

    Parameters
    - close_column (str, default: "close"): price column used for direction
    - volume_column (str, default: "volume"): volume column
    - output_columns (list[str] | None): optional; must contain exactly 1 name.
      If omitted, the default name is `obv_{close_column}_{volume_column}`.

    Output/Response
    - `data` contains `current_candle` plus 1 OBV column.
    - Output column names: `[<obv>]`. Default: `obv_{close_column}_{volume_column}`.
    """

    def __init__(
        self,
        close_column: str = "close",
        volume_column: str = "volume",
        output_columns: Optional[List[str]] = None,
        prefix: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.close_column = close_column
        self.volume_column = volume_column

        base = prefix or f"obv_{close_column}_{volume_column}"
        self.obv_col = base
        self._requested_output_columns = output_columns

    def build(self) -> pl.Expr:
        return pta.obv(close=pl.col("close"), volume=pl.col("volume"))

    def _exprs(self) -> List[pl.Expr]:
        return [self.build().alias(self.obv_col)]

    def output_columns(self) -> List[str]:
        return [self.obv_col]

    def required_columns(self) -> List[str]:
        return [self.close_column, self.volume_column]

    def validate_output_columns(self) -> None:
        if self._requested_output_columns is not None:
            if len(self._requested_output_columns) != 1:
                raise ValueError(
                    "OBV expects exactly 1 output column name in 'output_columns'"
                )
            requested = self._requested_output_columns[0]
            if not isinstance(requested, str) or not requested:
                raise ValueError("OBV requires a non-empty single output column name")
            self.obv_col = requested

    def window_size(self) -> int:
        # OBV is cumulative but only requires previous bar state to update
        return 1

    def warmup_size(self) -> int:
        return 50
