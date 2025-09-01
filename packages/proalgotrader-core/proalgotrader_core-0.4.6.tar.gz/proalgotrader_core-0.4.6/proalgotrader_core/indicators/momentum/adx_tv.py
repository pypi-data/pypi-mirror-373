import polars as pl

from typing import List, Optional

from proalgotrader_core.indicators.indicator import Indicator


class ADX_TV(Indicator):
    """
    ADX with separate DI length and ADX smoothing (TradingView-style).

    Parameters
    - di_length (int, default: 14): lookback for +DI/-DI and ATR Wilder smoothing
    - adx_smoothing (int, default: 14): Wilder/RMA smoothing length for DX -> ADX
    - output_columns (list[str] | None): optional; must contain exactly 1 name.
      If omitted, default name is `adx_tv_{di_length}_{adx_smoothing}`.

    Output/Response
    - `data` contains `current_candle` plus 1 ADX column.
    - Output column name: `[<adx>]`.
    """

    def __init__(
        self,
        di_length: int = 14,
        adx_smoothing: int = 14,
        output_columns: Optional[List[str]] = None,
    ) -> None:
        super().__init__()
        self.di_length = di_length
        self.adx_smoothing = adx_smoothing
        self.adx_col = f"adx_tv_{di_length}_{adx_smoothing}"
        self._requested_output_columns = output_columns

    def build(self) -> pl.Expr:
        prev_close = pl.col("close").shift(1)

        tr = pl.max_horizontal(
            (pl.col("high") - pl.col("low")),
            (pl.col("high") - prev_close).abs(),
            (pl.col("low") - prev_close).abs(),
        )

        up_move = pl.col("high") - pl.col("high").shift(1)
        down_move = pl.col("low").shift(1) - pl.col("low")

        plus_dm = (
            pl.when((up_move > down_move) & (up_move > 0)).then(up_move).otherwise(0.0)
        )
        minus_dm = (
            pl.when((down_move > up_move) & (down_move > 0))
            .then(down_move)
            .otherwise(0.0)
        )

        alpha_di = 1.0 / float(self.di_length)
        alpha_adx = 1.0 / float(self.adx_smoothing)

        atr_rma = tr.ewm_mean(alpha=alpha_di, adjust=False)
        plus_dm_rma = plus_dm.ewm_mean(alpha=alpha_di, adjust=False)
        minus_dm_rma = minus_dm.ewm_mean(alpha=alpha_di, adjust=False)

        # Avoid division by zero; Polars will yield NaN which we replace with 0
        plus_di = plus_dm_rma / atr_rma * 100.0
        minus_di = minus_dm_rma / atr_rma * 100.0

        dx = (plus_di - minus_di).abs() / (plus_di + minus_di) * 100.0
        dx = dx.fill_nan(0.0)

        adx = dx.ewm_mean(alpha=alpha_adx, adjust=False)

        return adx

    def _exprs(self) -> List[pl.Expr]:
        return [self.build().alias(self.adx_col)]

    def output_columns(self) -> List[str]:
        return [self.adx_col]

    def required_columns(self) -> List[str]:
        return ["high", "low", "close"]

    def validate_output_columns(self) -> None:
        if self._requested_output_columns is not None:
            if len(self._requested_output_columns) != 1:
                raise ValueError(
                    "ADX_TV expects exactly 1 output column name in 'output_columns'"
                )
            requested = self._requested_output_columns[0]
            if not isinstance(requested, str) or not requested:
                raise ValueError(
                    "ADX_TV requires a non-empty single output column name"
                )
            self.adx_col = requested

    def window_size(self) -> int:
        return max(self.di_length, self.adx_smoothing)

    def warmup_size(self) -> int:
        return self.window_size() * 3
