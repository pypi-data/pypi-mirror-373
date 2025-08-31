import polars as pl
import polars_talib as pta

from typing import List, Optional

from proalgotrader_core.indicators.indicator import Indicator


class STOCH_TV(Indicator):
    """
    TradingView-style Stochastic Oscillator.

    Parameters
    - k (int, default: 14): %K length
    - k_smoothing (int, default: 3): %K smoothing
    - d_smoothing (int, default: 3): %D smoothing
    - output_columns (list[str] | None): optional; must contain exactly 2 names [k, d].
    """

    def __init__(
        self,
        k: int = 14,
        k_smoothing: int = 3,
        d_smoothing: int = 3,
        output_columns: Optional[List[str]] = None,
        prefix: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.k = k
        self.k_smoothing = k_smoothing
        self.d_smoothing = d_smoothing

        base = prefix or f"stoch_tv_{k}_{k_smoothing}_{d_smoothing}"
        self.k_col = f"{base}_k"
        self.d_col = f"{base}_d"

        self._requested_output_columns = output_columns

    def build(self) -> pl.Expr:
        return pta.stoch(
            high=pl.col("high"),
            low=pl.col("low"),
            close=pl.col("close"),
            fastk_period=self.k,
            slowk_period=self.k_smoothing,
            slowd_period=self.d_smoothing,
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
                    "STOCH_TV expects exactly 2 output column names in 'output_columns'"
                )
            k_col, d_col = self._requested_output_columns
            cols = [k_col, d_col]
            if any(not isinstance(c, str) or not c for c in cols):
                raise ValueError("STOCH_TV requires two non-empty output column names")
            self.k_col, self.d_col = cols

    def window_size(self) -> int:
        return max(self.k, self.k_smoothing, self.d_smoothing)

    def warmup_size(self) -> int:
        return self.window_size() * 3
