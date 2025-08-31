import polars as pl
import polars_talib as pta

from typing import List, Optional

from proalgotrader_core.indicators.indicator import Indicator


class STOCHRSI(Indicator):
    """
    Stochastic RSI (STOCHRSI).

    Parameters
    - timeperiod (int, default: 14): RSI lookback length
    - fastk_period (int, default: 3): %K smoothing length applied to RSI
    - fastd_period (int, default: 3): %D smoothing length applied to %K
    - column (str, default: "close"): input column name
    - output_columns (list[str] | None): optional; must contain exactly 2 names
      in this order: [k, d]. If omitted, defaults are derived as
      `stochrsi_{timeperiod}_{fastk}_{fastd}_{column}` plus `_k`, `_d` suffixes.
    - prefix (str | None): optional base for default names when `output_columns`
      is not provided.

    Output/Response
    - `data` contains `current_candle` plus 2 columns in order: [k, d].
    - Default names example: `stochrsi_14_3_3_close_k`, `stochrsi_14_3_3_close_d`.
    """

    def __init__(
        self,
        timeperiod: int = 14,
        fastk_period: int = 3,
        fastd_period: int = 3,
        column: str = "close",
        output_columns: Optional[List[str]] = None,
        prefix: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.timeperiod = timeperiod
        self.fastk_period = fastk_period
        self.fastd_period = fastd_period
        self.column = column

        base = prefix or f"stochrsi_{timeperiod}_{fastk_period}_{fastd_period}_{column}"
        self.k_col = f"{base}_k"
        self.d_col = f"{base}_d"

        self._requested_output_columns = output_columns

    def build(self) -> pl.Expr:
        return pta.stochrsi(
            real=pl.col(self.column),
            timeperiod=self.timeperiod,
            fastk_period=self.fastk_period,
            fastd_period=self.fastd_period,
        )

    def _exprs(self) -> List[pl.Expr]:
        stochrsi_result = self.build()
        return [
            stochrsi_result.struct.field("fastk").alias(self.k_col),
            stochrsi_result.struct.field("fastd").alias(self.d_col),
        ]

    def output_columns(self) -> List[str]:
        return [self.k_col, self.d_col]

    def required_columns(self) -> List[str]:
        return [self.column]

    def validate_output_columns(self) -> None:
        if self._requested_output_columns is not None:
            if len(self._requested_output_columns) != 2:
                raise ValueError(
                    "STOCHRSI expects exactly 2 output column names in 'output_columns'"
                )
            k_col, d_col = self._requested_output_columns
            cols = [k_col, d_col]
            if any(not isinstance(c, str) or not c for c in cols):
                raise ValueError("STOCHRSI requires two non-empty output column names")
            self.k_col, self.d_col = cols

    def window_size(self) -> int:
        return max(self.timeperiod, self.fastk_period, self.fastd_period)

    def warmup_size(self) -> int:
        return self.window_size() * 3
