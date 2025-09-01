import polars as pl
import polars_talib as pta

from typing import List, Optional

from proalgotrader_core.indicators.indicator import Indicator


class STOCH(Indicator):
    """
    Stochastic Oscillator (STOCH).

    Parameters
    - fastk_period (int, default: 14): lookback for %K
    - slowk_period (int, default: 3): smoothing for %K
    - slowd_period (int, default: 3): smoothing for %D
    - output_columns (list[str] | None): optional; must contain exactly 2 names
      in this order: [k, d]. If omitted, defaults are derived as
      `stoch_{fastk}_{slowk}_{slowd}` plus `_k`, `_d` suffixes.
    - prefix (str | None): optional base for default names when `output_columns`
      is not provided.

    Output/Response
    - `data` contains `current_candle` plus 2 columns in order: [k, d].
    - Default names example: `stoch_14_3_3_k`, `stoch_14_3_3_d`.
    """

    def __init__(
        self,
        fastk_period: int = 14,
        slowk_period: int = 3,
        slowd_period: int = 3,
        output_columns: Optional[List[str]] = None,
        prefix: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.fastk_period = fastk_period
        self.slowk_period = slowk_period
        self.slowd_period = slowd_period

        base = prefix or f"stoch_{fastk_period}_{slowk_period}_{slowd_period}"
        self.k_col = f"{base}_k"
        self.d_col = f"{base}_d"

        self._requested_output_columns = output_columns

    def build(self) -> pl.Expr:
        return pta.stoch(
            high=pl.col("high"),
            low=pl.col("low"),
            close=pl.col("close"),
            fastk_period=self.fastk_period,
            slowk_period=self.slowk_period,
            slowd_period=self.slowd_period,
        )

    def _exprs(self) -> List[pl.Expr]:
        stoch_result = self.build()
        return [
            stoch_result.struct.field("slowk").alias(self.k_col),
            stoch_result.struct.field("slowd").alias(self.d_col),
        ]

    def output_columns(self) -> List[str]:
        return [self.k_col, self.d_col]

    def required_columns(self) -> List[str]:
        return ["high", "low", "close"]

    def validate_output_columns(self) -> None:
        if self._requested_output_columns is not None:
            if len(self._requested_output_columns) != 2:
                raise ValueError(
                    "STOCH expects exactly 2 output column names in 'output_columns'"
                )
            k_col, d_col = self._requested_output_columns
            cols = [k_col, d_col]
            if any(not isinstance(c, str) or not c for c in cols):
                raise ValueError("STOCH requires two non-empty output column names")
            self.k_col, self.d_col = cols

    def window_size(self) -> int:
        return max(self.fastk_period, self.slowk_period, self.slowd_period)

    def warmup_size(self) -> int:
        return self.window_size() * 3
