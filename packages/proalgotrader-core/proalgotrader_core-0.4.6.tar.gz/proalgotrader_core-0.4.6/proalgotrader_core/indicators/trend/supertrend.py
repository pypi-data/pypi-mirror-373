import polars as pl
from typing import List, Optional

from proalgotrader_core.indicators.indicator import Indicator


class Supertrend(Indicator):
    """
    Supertrend indicator (custom implementation).

    Parameters
    - length (int, default: 10): ATR lookback length
    - multiplier (float, default: 3.0): ATR multiplier
    - output_columns (list[str] | None): optional; must contain exactly 3 names
      in order: [supertrend, upper_band, lower_band]

    Output
    - Columns: supertrend (float), upper_band (float), lower_band (float)
    """

    def __init__(
        self,
        length: int = 10,
        multiplier: float = 3.0,
        output_columns: Optional[List[str]] = None,
    ) -> None:
        super().__init__()
        self.length = length
        self.multiplier = multiplier

        base = f"supertrend_{length}_{multiplier}"
        self.st_col = base
        self.upper_col = f"{base}_upper"
        self.lower_col = f"{base}_lower"

        self._requested_output_columns = output_columns

    def build(self) -> pl.Expr:
        # Supertrend calculation using ATR and basic upper/lower bands
        prev_close = pl.col("close").shift(1)

        tr = pl.max_horizontal(
            (pl.col("high") - pl.col("low")),
            (pl.col("high") - prev_close).abs(),
            (pl.col("low") - prev_close).abs(),
        )

        # Wilder's ATR via EMA with alpha=1/length
        atr = tr.ewm_mean(alpha=1.0 / self.length, adjust=False)

        hl2 = (pl.col("high") + pl.col("low")) / 2.0

        basic_upperband = hl2 + self.multiplier * atr
        basic_lowerband = hl2 - self.multiplier * atr

        # Final bands: prevent band from decreasing/increasing across candles
        final_upperband = (
            pl.when(
                (basic_upperband < basic_upperband.shift(1))
                | (pl.col("close").shift(1) > basic_upperband.shift(1))
            )
            .then(basic_upperband)
            .otherwise(basic_upperband.shift(1))
        )

        final_lowerband = (
            pl.when(
                (basic_lowerband > basic_lowerband.shift(1))
                | (pl.col("close").shift(1) < basic_lowerband.shift(1))
            )
            .then(basic_lowerband)
            .otherwise(basic_lowerband.shift(1))
        )

        # Supertrend direction and value
        # Direction: 1 for uptrend, -1 for downtrend
        direction = pl.lit(0).cast(pl.Int8)
        direction = (
            pl.when(
                (pl.col("close").shift(1) <= final_upperband.shift(1))
                & (pl.col("close") > final_upperband)
            )
            .then(1)
            .when(
                (pl.col("close").shift(1) >= final_lowerband.shift(1))
                & (pl.col("close") < final_lowerband)
            )
            .then(-1)
            .otherwise(pl.lit(None))
        )

        # Propagate direction forward filling initial nulls with -1
        direction = direction.fill_null(strategy="forward").fill_null(-1)

        st = pl.when(direction == 1).then(final_lowerband).otherwise(final_upperband)

        return pl.struct(
            [
                st.alias("supertrend"),
                final_upperband.alias("upper"),
                final_lowerband.alias("lower"),
            ]
        )

    def _exprs(self) -> List[pl.Expr]:
        supertrend_result = self.build()
        return [
            supertrend_result.struct.field("supertrend").alias(self.st_col),
            supertrend_result.struct.field("upper").alias(self.upper_col),
            supertrend_result.struct.field("lower").alias(self.lower_col),
        ]

    def output_columns(self) -> List[str]:
        return [self.st_col, self.upper_col, self.lower_col]

    def required_columns(self) -> List[str]:
        return ["high", "low", "close"]

    def validate_output_columns(self) -> None:
        if self._requested_output_columns is not None:
            if len(self._requested_output_columns) != 3:
                raise ValueError(
                    "Supertrend expects exactly 3 output column names in 'output_columns'"
                )
            st, up, low = self._requested_output_columns
            cols = [st, up, low]
            if any(not isinstance(c, str) or not c for c in cols):
                raise ValueError(
                    "Supertrend requires three non-empty output column names"
                )
            self.st_col, self.upper_col, self.lower_col = cols

    def window_size(self) -> int:
        return self.length

    def warmup_size(self) -> int:
        return self.length * 3
