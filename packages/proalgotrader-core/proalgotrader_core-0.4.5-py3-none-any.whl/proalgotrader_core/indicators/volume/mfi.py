import polars as pl
import polars_talib as pta

from typing import List, Optional

from proalgotrader_core.indicators.indicator import Indicator


class MFI(Indicator):
    """
    Money Flow Index (MFI).

    Parameters
    - timeperiod (int, default: 14)
    - output_columns (list[str] | None): optional; must contain exactly 1 name.
      If omitted, the default name is `mfi_{timeperiod}` (e.g. `mfi_14`).

    Output/Response
    - `data` contains `current_candle` plus 1 MFI column.
    - Output column names: `[<mfi>]`. Default: `mfi_{timeperiod}`.
    """

    def __init__(
        self,
        timeperiod: int = 14,
        output_columns: Optional[List[str]] = None,
    ) -> None:
        super().__init__()
        self.timeperiod = timeperiod
        self.mfi_col = f"mfi_{timeperiod}"
        self._requested_output_columns = output_columns

    def build(self) -> pl.Expr:
        return pta.mfi(
            high=pl.col("high"),
            low=pl.col("low"),
            close=pl.col("close"),
            volume=pl.col("volume"),
            timeperiod=self.timeperiod,
        )

    def _exprs(self) -> List[pl.Expr]:
        return [self.build().alias(self.mfi_col)]

    def output_columns(self) -> List[str]:
        return [self.mfi_col]

    def required_columns(self) -> List[str]:
        return ["high", "low", "close", "volume"]

    def validate_output_columns(self) -> None:
        if self._requested_output_columns is not None:
            if len(self._requested_output_columns) != 1:
                raise ValueError(
                    "MFI expects exactly 1 output column name in 'output_columns'"
                )
            requested = self._requested_output_columns[0]
            if not isinstance(requested, str) or not requested:
                raise ValueError("MFI requires a non-empty single output column name")
            self.mfi_col = requested

    def window_size(self) -> int:
        return self.timeperiod

    def warmup_size(self) -> int:
        return self.timeperiod * 3
