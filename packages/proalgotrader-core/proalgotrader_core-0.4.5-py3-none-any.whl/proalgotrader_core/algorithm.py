import asyncio

from datetime import date, datetime, time, timedelta
from typing import List, Literal, Optional, Tuple, Type, Dict
from logzero import logger

from proalgotrader_core.base_algorithm import BaseAlgorithm
from proalgotrader_core.broker_symbol import BrokerSymbol
from proalgotrader_core.chart import Chart
from proalgotrader_core._helpers.get_strike_price import get_strike_price
from proalgotrader_core.order import Order
from proalgotrader_core.position import Position
from proalgotrader_core.protocols.enums.account_type import AccountType
from proalgotrader_core.protocols.enums.candle_type import CandleType
from proalgotrader_core.protocols.enums.market_type import MarketType
from proalgotrader_core.protocols.enums.order_type import OrderType
from proalgotrader_core.protocols.enums.position_type import PositionType
from proalgotrader_core.protocols.enums.segment_type import SegmentType
from proalgotrader_core.protocols.position_manager import PositionManagerProtocol
from proalgotrader_core.protocols.signal_manager import SignalManagerProtocol


class Algorithm(BaseAlgorithm):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @property
    def market_start_time(self) -> time:
        return self.algo_session.market_start_time

    @property
    def market_end_time(self) -> time:
        return self.algo_session.market_end_time

    @property
    def market_start_datetime(self) -> datetime:
        return self.algo_session.market_start_datetime

    @property
    def market_end_datetime(self) -> datetime:
        return self.algo_session.market_end_datetime

    @property
    def pre_market_time(self) -> datetime:
        return self.algo_session.pre_market_time

    @property
    def current_datetime(self) -> datetime:
        return self.algo_session.current_datetime

    @property
    def current_timestamp(self) -> int:
        return self.algo_session.current_timestamp

    @property
    def current_date(self) -> date:
        return self.algo_session.current_date

    @property
    def current_time(self) -> time:
        return self.algo_session.current_time

    @property
    def orders(self) -> List[Order]:
        return self.order_broker_manager.orders.copy()

    @property
    def positions(self) -> List[Position]:
        return self.order_broker_manager.positions.copy()

    @property
    def open_positions(self) -> List[Position]:
        return self.order_broker_manager.open_positions.copy()

    @property
    def position_pnl(self) -> Dict[str, float]:
        pnl = sum(
            [
                position.pnl
                for position in self.order_broker_manager.positions
                if position.status == "open"
            ]
        )

        if pnl > 0:
            return {"pnl": pnl, "profit": pnl, "loss": 0}
        else:
            return {"pnl": pnl, "profit": 0, "loss": abs(pnl)}

    @property
    def total_pnl(self) -> Dict[str, float]:
        pnl = sum([position.pnl for position in self.order_broker_manager.positions])

        if pnl > 0:
            return {"pnl": pnl, "profit": pnl, "loss": 0}
        else:
            return {"pnl": pnl, "profit": 0, "loss": abs(pnl)}

    def set_interval(self, interval: timedelta) -> None:
        self.interval = interval

    def between_time(self, first: time, second: time) -> bool:
        return first < self.current_time < second

    async def add_signals(
        self,
        *,
        signal_manager: Optional[Type[SignalManagerProtocol]],
        symbol_names: List[str],
    ) -> None:
        if not signal_manager or not issubclass(signal_manager, SignalManagerProtocol):
            raise Exception("SignalManager is required.")

        signals = [
            signal_manager(symbol_name=symbol_name, algorithm=self)
            for symbol_name in symbol_names
        ]

        await asyncio.gather(*[signal.initialize() for signal in signals])

        self.__signals.extend(signals)

    def set_position_manager(
        self, *, position_manager: Optional[Type[PositionManagerProtocol]]
    ) -> None:
        if not position_manager or not issubclass(
            position_manager, PositionManagerProtocol
        ):
            raise Exception("PositionManager is required.")

        self.position_manager = position_manager(algorithm=self)

    def set_account_type(self, *, account_type: AccountType | None) -> None:
        if not isinstance(account_type, AccountType):
            logger.error("Invalid account type")

        self.account_type = account_type

    async def add_chart(
        self,
        *,
        broker_symbol: BrokerSymbol,
        timeframe: timedelta,
        candle_type: CandleType = CandleType.REGULAR,
        **kwargs,
    ) -> Chart:
        try:
            chart = await self.chart_manager.register_chart(
                broker_symbol, timeframe, candle_type=candle_type, **kwargs
            )

            return chart
        except Exception as e:
            logger.debug(e)
            raise Exception(e)

    async def add_equity(
        self,
        *,
        symbol_name: str,
    ) -> BrokerSymbol:
        try:
            base_symbol = self.order_broker_manager.base_symbols[symbol_name]

            equity_symbol = await self.order_broker_manager.add_equity(
                base_symbol=base_symbol,
                market_type=MarketType.Cash.value,
                segment_type=SegmentType.Equity.value,
            )

            return equity_symbol
        except Exception as e:
            logger.debug(e)
            raise Exception(e)

    async def add_future(
        self,
        *,
        symbol_name: str,
        expiry_input: Tuple[Literal["Weekly", "Monthly"], int] | None = None,
    ) -> BrokerSymbol:
        try:
            equity_symbol = await self.add_equity(symbol_name=symbol_name)

            expiry_date = await self._get_fno_expiry(
                expiry_type="future",
                expiry_input=expiry_input,
                base_symbol=equity_symbol.base_symbol,
                market_type=MarketType.Derivative.value,
                segment_type=SegmentType.Option.value,
            )

            future_symbol = await self.order_broker_manager.add_future(
                base_symbol=equity_symbol.base_symbol,
                market_type=MarketType.Derivative.value,
                segment_type=SegmentType.Future.value,
                expiry_date=expiry_date,
            )

            return future_symbol
        except Exception as e:
            logger.debug(e)
            raise Exception(e)

    async def add_option(
        self,
        *,
        symbol_name: str,
        expiry_input: Tuple[Literal["Weekly", "Monthly"], int] | None = None,
        strike_price_input: int | None = None,
        option_type: Literal["CE", "PE"] | None = None,
    ) -> BrokerSymbol:
        try:
            equity_symbol = await self.add_equity(symbol_name=symbol_name)

            expiry_date = await self._get_fno_expiry(
                expiry_type="option",
                expiry_input=expiry_input,
                base_symbol=equity_symbol.base_symbol,
                market_type=MarketType.Derivative.value,
                segment_type=SegmentType.Option.value,
            )

            if not isinstance(strike_price_input, int):
                raise Exception(
                    "Invalid strike price input, must be integer like -1, 0, 1"
                )

            if option_type not in ["CE", "PE"]:
                raise Exception("Invalid option type, must be CE or PE")

            strike_price = await get_strike_price(equity_symbol, strike_price_input)

            option_symbol = await self.order_broker_manager.add_option(
                base_symbol=equity_symbol.base_symbol,
                market_type=MarketType.Derivative.value,
                segment_type=SegmentType.Option.value,
                expiry_date=expiry_date,
                strike_price=strike_price,
                option_type=option_type,
            )

            return option_symbol
        except Exception as e:
            logger.debug(e)
            raise Exception(e)

    async def buy(self, *, broker_symbol: BrokerSymbol, quantities: int) -> None:
        try:
            await self._place_order(
                broker_symbol, quantities, PositionType.BUY, OrderType.MARKET_ORDER
            )
        except Exception as e:
            logger.debug(e)
            raise Exception(e)

    async def sell(self, *, broker_symbol: BrokerSymbol, quantities: int) -> None:
        try:
            await self._place_order(
                broker_symbol, quantities, PositionType.SELL, OrderType.MARKET_ORDER
            )
        except Exception as e:
            logger.debug(e)
            raise Exception(e)

    async def exit_all_positions(self) -> None:
        try:
            return await self.order_broker_manager.exit_all_positions()
        except Exception as e:
            raise Exception(e)
