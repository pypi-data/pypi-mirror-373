import polars as pl
import re
from typing import List, Optional, Set

from proalgotrader_core.indicators.indicator import Indicator


class CustomIndicator(Indicator):
    """
    Base class for custom indicators using polars_talib.

    Users extend this class and implement the `build()` method to create
    their own indicators using polars_talib functions.

    The `build()` method should return polars expressions that work on any DataFrame size
    (full historical data or trailing window for incremental updates).

        Example:
        # Simple usage - just return the polars_talib function call
        class MyRSI(CustomIndicator):
            def __init__(self, timeperiod: int = 14):
                super().__init__()
                self.timeperiod = timeperiod

            def build(self) -> pl.Expr:
                return pta.rsi(pl.col("close"), timeperiod=self.timeperiod).alias("my_rsi")

            def window_size(self) -> int:
                return self.timeperiod

        # Even simpler - MACD with auto field extraction
        class MyMACD(CustomIndicator):
            def __init__(self, fastperiod: int = 12, slowperiod: int = 26, signalperiod: int = 9):
                super().__init__()
                self.fastperiod = fastperiod
                self.slowperiod = slowperiod
                self.signalperiod = signalperiod

            def build(self) -> pl.Expr:
                return pta.macd(pl.col("close"), fastperiod=self.fastperiod,
                               slowperiod=self.slowperiod, signalperiod=self.signalperiod)
                # Auto-extracts: macd, macdsignal, macdhist

            def window_size(self) -> int:
                return self.slowperiod

        # With custom prefix for column names
        class MyPrefixedMACD(CustomIndicator):
            def __init__(self, fastperiod: int = 12, slowperiod: int = 26, signalperiod: int = 9):
                super().__init__(output_prefix="my_macd")
                self.fastperiod = fastperiod
                self.slowperiod = slowperiod
                self.signalperiod = signalperiod

            def build(self) -> pl.Expr:
                return pta.macd(pl.col("close"), fastperiod=self.fastperiod,
                               slowperiod=self.slowperiod, signalperiod=self.signalperiod)
                # Auto-extracts: my_macd_macd, my_macd_macdsignal, my_macd_macdhist

        # Single function with custom alias
        class MySMA(CustomIndicator):
            def __init__(self, period: int = 20):
                super().__init__()
                self.period = period

            def build(self) -> pl.Expr:
                return pta.sma(pl.col("close"), timeperiod=self.period).alias("my_sma")
    """

    def __init__(
        self,
        output_columns: Optional[List[str]] = None,
        required_columns: Optional[List[str]] = None,
        output_prefix: Optional[str] = None,
    ) -> None:
        super().__init__()
        self._user_output_columns = output_columns
        self._user_required_columns = required_columns
        self._output_prefix = output_prefix
        self._cached_expressions: Optional[List[pl.Expr]] = None
        self._cached_output_columns: Optional[List[str]] = None
        self._cached_required_columns: Optional[List[str]] = None

    def _exprs(self) -> List[pl.Expr]:
        """Return the polars expressions from the build method."""
        if self._cached_expressions is None:
            raw_expression = self.build()
            self._cached_expressions = self._process_expressions([raw_expression])
        return self._cached_expressions

    def build(self) -> pl.Expr:
        """
        Build the indicator expression using polars_talib.

        This method must be implemented by subclasses. It should return
        a single polars expression that uses a polars_talib function.

        You can return raw polars_talib function calls (like pta.macd()) and the system
        will automatically extract all fields from struct results.

        Returns:
            A single polars expression for the indicator
        """
        raise NotImplementedError(
            f"Subclass {self.__class__.__name__} must implement build() method"
        )

    def output_columns(self) -> List[str]:
        """
        Return the output column names.

        If user provided output_columns in __init__, use those.
        Otherwise, extract column names from the build() expressions.
        """
        if self._user_output_columns is not None:
            return self._user_output_columns

        if self._cached_output_columns is None:
            expressions = self._exprs()
            self._cached_output_columns = self._extract_column_names(expressions)

        return self._cached_output_columns

    def required_columns(self) -> List[str]:
        """
        Return the required input columns.

        If user provided required_columns in __init__, use those.
        Otherwise, extract column names from the build() expressions.
        """
        if self._user_required_columns is not None:
            return self._user_required_columns

        if self._cached_required_columns is None:
            expressions = self._exprs()
            self._cached_required_columns = self._extract_required_columns(expressions)

        return self._cached_required_columns

    def validate_output_columns(self) -> None:
        """Validate output columns - not needed for CustomIndicator."""
        # CustomIndicator doesn't use _requested_output_columns
        pass

    def window_size(self) -> int:
        """
        Return the minimum lookback required for exact last-value computation.

        Default implementation tries to auto-calculate from indicator parameters.
        Override if needed for custom logic.
        """
        return self._auto_calculate_window_size()

    def warmup_size(self) -> int:
        """
        Return extra lookback to stabilize recursive indicators.

        Default implementation tries to auto-calculate from indicator parameters.
        Override if needed for custom logic.
        """
        return self._auto_calculate_warmup_size()

    def _auto_calculate_window_size(self) -> int:
        """
        Automatically calculate window size from indicator parameters.

        Analyzes the indicator's parameters to determine the minimum lookback period.
        """
        # Get all numeric parameters from the indicator instance
        numeric_params = self._get_numeric_parameters()

        if not numeric_params:
            return 0

        # Return the maximum parameter value as the window size
        return max(numeric_params)

    def _auto_calculate_warmup_size(self) -> int:
        """
        Automatically calculate warmup size from indicator parameters.

        Uses a multiplier on the window size for stabilization.
        """
        window_size = self._auto_calculate_window_size()
        if window_size == 0:
            return 0

        # Use 3x the window size for warmup (common practice)
        return window_size * 3

    def _get_numeric_parameters(self) -> List[int]:
        """
        Extract numeric parameters from the indicator instance.

        Looks for common parameter names and returns their values.
        """
        numeric_params = []

        # Common parameter names that indicate lookback periods
        param_names = [
            "timeperiod",
            "period",
            "fastperiod",
            "slowperiod",
            "signalperiod",
            "fastlength",
            "slowlength",
            "signal_smoothing",
            "length",
            "fastk_period",
            "slowk_period",
            "slowd_period",
            "fastd_period",
            "fastk_matype",
            "slowk_matype",
            "slowd_matype",
            "fastd_matype",
            "fastlimit",
            "slowlimit",
            "acceleration",
            "maximum",
            "nbdevup",
            "nbdevdn",
            "matype",
            "minperiod",
            "maxperiod",
            "startvalue",
            "offsetonreverse",
            "accelerationinitlong",
            "accelerationlong",
            "accelerationmaxlong",
            "accelerationinit",
            "accelerationmax",
            "accelerationinitshort",
            "accelerationshort",
            "accelerationmaxshort",
        ]

        for param_name in param_names:
            if hasattr(self, param_name):
                value = getattr(self, param_name)
                if isinstance(value, (int, float)) and value > 0:
                    numeric_params.append(int(value))

        return numeric_params

    def _extract_column_names(self, expressions: List[pl.Expr]) -> List[str]:
        """
        Extract column names from polars expressions.

        Looks for .alias() calls in the expressions to get the output column names.
        """
        column_names = []
        for expr in expressions:
            # Convert expression to string to analyze
            expr_str = str(expr)

            # Look for .alias("column_name") pattern
            alias_match = re.search(r'\.alias\(["\']([^"\']+)["\']\)', expr_str)
            if alias_match:
                column_names.append(alias_match.group(1))
            else:
                # If no alias found, generate a default name
                column_names.append(f"custom_indicator_{len(column_names)}")

        return column_names

    def _extract_required_columns(self, expressions: List[pl.Expr]) -> List[str]:
        """
        Extract required input columns from polars expressions.

        Looks for col("column_name") calls in the expressions.
        """
        required_columns: Set[str] = set()

        for expr in expressions:
            # Convert expression to string to analyze
            expr_str = str(expr)

            # Look for col("column_name") pattern - handle both single and double quotes
            col_matches = re.findall(r'col\(["\']([^"\']+)["\']\)', expr_str)
            for match in col_matches:
                required_columns.add(match)

            # Also look for col(column_name) without quotes (though this is less common)
            col_matches_no_quotes = re.findall(
                r"col\(([a-zA-Z_][a-zA-Z0-9_]*)\)", expr_str
            )
            for match in col_matches_no_quotes:
                required_columns.add(match)

        return list(required_columns)

    def _process_expressions(self, raw_expressions: List[pl.Expr]) -> List[pl.Expr]:
        """
        Process raw expressions to automatically extract struct fields.

        If an expression is a struct result (like from pta.macd()), automatically
        extract all fields and create separate expressions for each field.
        """
        processed_expressions = []

        for expr in raw_expressions:
            # Convert expression to string to check if it's a struct
            expr_str = str(expr)

            # Check if this looks like a struct result (contains .struct.field)
            if ".struct.field(" in expr_str:
                # This is already a struct field extraction, keep as is
                processed_expressions.append(expr)
            else:
                # Check if this might be a struct result by looking for polars_talib function calls
                # Look for patterns like "lib/python3.x/site-packages/polars_talib/_polars_talib.abi3.so:function_name"
                if "polars_talib" in expr_str and ".abi3.so:" in expr_str:
                    # Extract the function name from the expression string
                    function_name = self._extract_function_name(expr_str)

                    # Get the known field names for this function
                    field_names = self._get_known_struct_fields(function_name)

                    if field_names:
                        # Extract all fields for this function
                        for field in field_names:
                            alias = (
                                f"{self._output_prefix}_{field}"
                                if self._output_prefix
                                else field
                            )
                            processed_expressions.append(
                                expr.struct.field(field).alias(alias)
                            )
                    else:
                        # Unknown function, keep as is
                        processed_expressions.append(expr)
                else:
                    # Not a polars_talib struct function, keep as is
                    processed_expressions.append(expr)

        return processed_expressions

    def _extract_function_name(self, expr_str: str) -> str:
        """
        Extract the function name from a polars_talib expression string.
        """
        # Look for pattern: "abi3.so:function_name"
        match = re.search(r"abi3\.so:([a-zA-Z_][a-zA-Z0-9_]*)", expr_str)
        if match:
            return match.group(1)
        return ""

    def _get_known_struct_fields(self, function_name: str) -> List[str]:
        """
        Get known field names for polars_talib functions that return structs.
        This is based on the official polars_talib get_functions_output_struct() function.
        """
        # Dictionary mapping function names to their struct field names
        # This matches exactly with polars_talib's get_functions_output_struct()
        struct_fields = {
            # Hilbert Transform functions
            "ht_phasor": ["inphase", "quadrature"],
            "ht_sine": ["sine", "leadsine"],
            # Math Operators
            "minmax": ["min", "max"],
            "minmaxindex": ["minidx", "maxidx"],
            # Momentum Indicators
            "aroon": ["aroondown", "aroonup"],
            "macd": ["macd", "macdsignal", "macdhist"],
            "macdext": ["macd", "macdsignal", "macdhist"],
            "macdfix": ["macd", "macdsignal", "macdhist"],
            "stoch": ["slowk", "slowd"],
            "stochf": ["fastk", "fastd"],
            "stochrsi": ["fastk", "fastd"],
            # Overlap Studies
            "bbands": ["upperband", "middleband", "lowerband"],
            "mama": ["mama", "fama"],
        }

        return struct_fields.get(function_name, [])
