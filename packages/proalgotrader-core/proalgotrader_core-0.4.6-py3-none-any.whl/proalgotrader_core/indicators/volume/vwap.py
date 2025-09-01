import polars as pl

from typing import List, Optional

from proalgotrader_core.indicators.indicator import Indicator


class VWAP(Indicator):
    """
    Volume Weighted Average Price (VWAP).

    VWAP is a trading benchmark that gives the average price a security has traded at
    throughout the day, based on both volume and price. It provides insight into both
    the trend and value of a security.

    Note: VWAP is not available in polars_talib, so this is a custom implementation
    using native Polars expressions. This was explicitly requested and approved.

    For broker-accurate VWAP calculation:
    - Uses typical price (HLC3) when price_column="typical_price"
    - Resets calculation at the beginning of each trading session (daily)
    - Matches standard broker VWAP implementations

    Parameters
    - window (int, default: None): lookback window for rolling VWAP. If None, calculates session-based cumulative VWAP.
    - price_column (str, default: "close"): price column to use. Use "typical_price" for broker-standard calculation.
    - volume_column (str, default: "volume"): volume column
    - output_columns (list[str] | None): optional; must contain exactly 1 name.
      If omitted, the default name is `vwap_{window}_{price_column}` or `vwap_cumulative_{price_column}`.

    Output/Response
    - `data` contains `current_candle` plus 1 VWAP column.
    - Output column names: `[<vwap>]`. Default: `vwap_{window}_{price_column}` or `vwap_cumulative_{price_column}`.

    Examples:
        # Session-based VWAP using typical price (broker standard)
        vwap = VWAP(price_column="typical_price")

        # Rolling 20-period VWAP
        vwap = VWAP(window=20)

        # VWAP using close price
        vwap = VWAP()

        # Custom output name
        vwap = VWAP(window=14, output_columns=["my_vwap"])
    """

    def __init__(
        self,
        window: Optional[int] = None,
        price_column: str = "close",
        volume_column: str = "volume",
        output_columns: Optional[List[str]] = None,
        prefix: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.window = window
        self.price_column = price_column
        self.volume_column = volume_column

        if window is None:
            base = prefix or f"vwap_cumulative_{price_column}"
        else:
            base = prefix or f"vwap_{window}_{price_column}"

        self.vwap_col = base
        self._requested_output_columns = output_columns

    def build(self) -> pl.Expr:
        # Note: VWAP is not available in polars_talib (pta), so we implement it
        # using native Polars expressions as per explicit request.
        # Formula: VWAP = Σ(Price × Volume) / Σ(Volume)

        # Handle typical price calculation if requested
        if self.price_column == "typical_price":
            # Typical price = (high + low + close) / 3
            price_col = (pl.col("high") + pl.col("low") + pl.col("close")) / 3
        else:
            price_col = pl.col(self.price_column)

        volume_col = pl.col(self.volume_column)

        # Calculate price * volume
        pv = price_col * volume_col

        if self.window is None:
            # Session-based cumulative VWAP (resets each trading day)
            # Group by date to reset VWAP calculation for each trading session
            vwap_expr = pv.cum_sum().over(
                pl.col("current_candle").dt.date()
            ) / volume_col.cum_sum().over(pl.col("current_candle").dt.date())
        else:
            # Rolling VWAP
            vwap_expr = pv.rolling_sum(
                window_size=self.window
            ) / volume_col.rolling_sum(window_size=self.window)

        return vwap_expr

    def _exprs(self) -> List[pl.Expr]:
        return [self.build().alias(self.vwap_col)]

    def output_columns(self) -> List[str]:
        return [self.vwap_col]

    def required_columns(self) -> List[str]:
        if self.price_column == "typical_price":
            # For typical price, we need high, low, close, and volume
            return ["high", "low", "close", self.volume_column]
        else:
            return [self.price_column, self.volume_column]

    def validate_output_columns(self) -> None:
        if self._requested_output_columns is not None:
            if len(self._requested_output_columns) != 1:
                raise ValueError(
                    "VWAP expects exactly 1 output column name in 'output_columns'"
                )
            requested = self._requested_output_columns[0]
            if not isinstance(requested, str) or not requested:
                raise ValueError("VWAP requires a non-empty single output column name")
            self.vwap_col = requested

    def window_size(self) -> int:
        # For cumulative VWAP, we need all the data
        if self.window is None:
            return 0
        return self.window

    def warmup_size(self) -> int:
        # VWAP doesn't need much warmup since it's a simple calculation
        return 0
