import asyncio

from datetime import datetime, timedelta

from logzero import logger
from contextlib import asynccontextmanager
from abc import abstractmethod
from typing import Any, Callable, Dict, List

from proalgotrader_core.algo_session import AlgoSession
from proalgotrader_core.api import Api
from proalgotrader_core.base_symbol import BaseSymbol
from proalgotrader_core.broker_symbol import BrokerSymbol
from proalgotrader_core.notification_manager import NotificationManager
from proalgotrader_core.order import Order
from proalgotrader_core.position import Position
from proalgotrader_core.protocols.algorithm import AlgorithmProtocol


class BaseOrderBrokerManager:
    def __init__(
        self,
        api: Api,
        algo_session: AlgoSession,
        notification_manager: NotificationManager,
        algorithm: AlgorithmProtocol,
    ) -> None:
        self.api = api
        self.algo_session = algo_session
        self.notification_manager = notification_manager

        self.algorithm = algorithm
        self.algo_session_broker = algo_session.project.order_broker_info

        self.id = self.algo_session_broker.id
        self.broker_uid = self.algo_session_broker.broker_uid
        self.broker_title = self.algo_session_broker.broker_title
        self.broker_name = self.algo_session_broker.broker_name
        self.broker_config = self.algo_session_broker.broker_config

        self.base_symbols: Dict[str, BaseSymbol] = {}
        self.broker_symbols: Dict[Any, BrokerSymbol] = {}

        self.initial_capital: float = 0
        self.current_capital: float = 0

        self.__orders: List[Order] = []
        self.__positions: List[Position] = []

        self.processing_request: bool = False

        self.__order_lock: asyncio.Lock = asyncio.Lock()

        self.__subscribers: List[Dict[str, Any]] = []

    @property
    def subscribers(self):
        return self.__subscribers

    async def subscribe_tick(
        self, broker_symbol: BrokerSymbol, on_tick: Callable[..., Any]
    ) -> None:
        logger.info(f"subscribed to {broker_symbol.symbol_name}")

        self.__subscribers.append({"broker_symbol": broker_symbol, "on_tick": on_tick})

    @property
    def orders(self) -> List[Order]:
        return self.__orders

    @property
    def positions(self) -> List[Position]:
        return self.__positions

    @property
    def open_positions(self) -> List[Position]:
        return [position for position in self.__positions if position.status == "open"]

    def is_processing(self) -> bool:
        return self.processing_request

    @asynccontextmanager
    async def processing(self):
        await self.__order_lock.acquire()

        self.processing_request = True

        try:
            yield
        finally:
            self.processing_request = False

            self.__order_lock.release()

    async def initialize(self) -> None:
        print("base order broker initializing")

        base_symbols = await self.api.get_base_symbols()

        self.base_symbols = {
            base_symbol["key"]: BaseSymbol(base_symbol) for base_symbol in base_symbols
        }

    async def get_order_info(self, data: Dict[str, Any]) -> Order:
        broker_symbol = await self.get_symbol(data["broker_symbol"])

        order = Order(data, broker_symbol=broker_symbol)

        await order.initialize()

        return order

    async def get_position_info(self, data: Dict[str, Any]) -> Position:
        broker_symbol = await self.get_symbol(data["broker_symbol"])

        position = Position(data, broker_symbol=broker_symbol, algorithm=self.algorithm)

        await position.initialize()

        return position

    async def set_portfolio(self) -> None:
        try:
            portfolio = await self.api.get_portfolio()

            await self.set_orders(portfolio["orders"])

            await self.set_positions(portfolio["positions"])
        except Exception as e:
            logger.info("set_orders: error happened", e)
            raise Exception(e)

    async def set_orders(self, orders: List) -> None:
        try:
            self.__orders = [await self.get_order_info(order) for order in orders]
        except Exception as e:
            logger.info("set_orders: error happened", e)
            raise Exception(e)

    async def set_positions(self, positions: List) -> None:
        try:
            self.__positions = [
                await self.get_position_info(position) for position in positions
            ]
        except Exception as e:
            logger.info("set_positions: error happened", e)
            raise Exception(e)

    async def on_after_market_closed(self) -> None:
        try:
            for position in self.positions:
                await position.on_after_market_closed()

            await self.stop_connection()
        except Exception as e:
            logger.debug(e)
            raise Exception(e)

    async def add_equity(
        self,
        *,
        base_symbol: BaseSymbol,
        market_type: str,
        segment_type: str,
    ) -> BrokerSymbol:
        try:
            data = {
                "base_symbol_id": base_symbol.id,
                "exchange": base_symbol.exchange,
                "market_type": market_type,
                "segment_type": segment_type,
                "expiry_input": None,
                "expiry_date": None,
                "strike_price": None,
                "option_type": None,
            }

            broker_symbol = await self.get_symbol(data)

            return broker_symbol
        except Exception as e:
            logger.debug(e)
            raise Exception(e)

    async def add_future(
        self,
        *,
        base_symbol: BaseSymbol,
        market_type: str,
        segment_type: str,
        expiry_date: str,
    ) -> BrokerSymbol:
        try:
            data = {
                "base_symbol_id": base_symbol.id,
                "exchange": base_symbol.exchange,
                "market_type": market_type,
                "segment_type": segment_type,
                "expiry_date": expiry_date,
                "strike_price": None,
                "option_type": None,
            }

            broker_symbol = await self.get_symbol(data)

            return broker_symbol
        except Exception as e:
            logger.debug(e)
            raise Exception(e)

    async def add_option(
        self,
        *,
        base_symbol: BaseSymbol,
        market_type: str,
        segment_type: str,
        expiry_date: str,
        strike_price: int,
        option_type: str,
    ) -> BrokerSymbol:
        try:
            data = {
                "base_symbol_id": base_symbol.id,
                "exchange": base_symbol.exchange,
                "market_type": market_type,
                "segment_type": segment_type,
                "expiry_date": expiry_date,
                "strike_price": strike_price,
                "option_type": option_type,
            }

            broker_symbol = await self.get_symbol(data)

            return broker_symbol
        except Exception as e:
            logger.debug(e)
            raise Exception(e)

    async def get_symbol(
        self,
        broker_symbol_info: Dict[str, Any],
    ) -> BrokerSymbol:
        base_symbol_id = broker_symbol_info["base_symbol_id"]
        exchange = broker_symbol_info["exchange"]
        market_type = broker_symbol_info["market_type"]
        segment_type = broker_symbol_info["segment_type"]
        expiry_date = broker_symbol_info["expiry_date"]
        strike_price = broker_symbol_info["strike_price"]
        option_type = broker_symbol_info["option_type"]

        key = (
            base_symbol_id,
            exchange,
            market_type,
            segment_type,
            expiry_date,
            strike_price,
            option_type,
        )

        try:
            return self.broker_symbols[key]
        except KeyError:
            if "id" not in broker_symbol_info:
                filtered_base_symbol = next(
                    base_symbol
                    for base_symbol in self.base_symbols.values()
                    if base_symbol.id == base_symbol_id
                )

                if not filtered_base_symbol:
                    raise Exception("Invalid Base Symbol")

                broker_symbol_info = await self.__get_broker_symbols(
                    broker_title=self.broker_title,
                    payload=broker_symbol_info,
                )

            broker_symbol = BrokerSymbol(
                order_broker_manager=self, broker_symbol_info=broker_symbol_info
            )

            await broker_symbol.initialize()

            self.broker_symbols[key] = broker_symbol

            return broker_symbol

    async def __get_broker_symbols(
        self, broker_title: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        try:
            broker_symbol: Dict[str, Any] = await self.api.get_broker_symbols(
                broker_title=broker_title,
                payload=payload,
            )

            return broker_symbol
        except Exception as e:
            logger.debug(e)
            raise Exception(e)

    async def get_positions(
        self,
        symbol_name: str,
        market_type: str,
        order_type: str,
        product_type: str,
        position_type: str,
    ) -> List[Position]:
        return [
            position
            for position in self.positions
            if (
                position.broker_symbol.symbol_name == symbol_name
                and position.broker_symbol.market_type == market_type
                and position.order_type == order_type
                and position.product_type == product_type
                and position.position_type == position_type
            )
        ]

    async def __upsert_position(self, position: Position) -> None:
        for idx, existing in enumerate(self.__positions):
            if existing.position_id == position.position_id:
                self.__positions[idx] = position
                return

        self.__positions.append(position)

    async def __manage_position(
        self,
        data: Dict[str, Any],
        broker_symbol: BrokerSymbol,
    ):
        order = Order(
            data["order"],
            broker_symbol=broker_symbol,
        )

        self.__orders.append(order)

        await order.initialize()

        position = Position(
            data["position"],
            broker_symbol=broker_symbol,
            algorithm=self.algorithm,
        )

        await self.__upsert_position(position)

        await position.initialize()

    async def enter_position(
        self,
        *,
        broker_symbol: BrokerSymbol,
        quantities: int,
        product_type: str,
        order_type: str,
        position_type: str,
    ) -> None:
        async with self.processing():
            print("entering position")

            payload: Dict[str, Any] = {
                "algo_session_id": self.algo_session.id,
                "broker_symbol_id": broker_symbol.id,
                "product_type": product_type,
                "order_type": order_type,
                "position_type": position_type,
                "quantities": quantities,
                "price": broker_symbol.ltp,
            }

            data = await self.api.enter_position(payload=payload)

            await self.__manage_position(data, broker_symbol)

    async def exit_position(
        self,
        position_id: str,
        broker_symbol: BrokerSymbol,
        quantities: int,
        product_type: str,
        order_type: str,
        position_type: str,
    ) -> None:
        async with self.processing():
            print("exiting position")

            payload: Dict[str, Any] = {
                "position_id": position_id,
                "algo_session_id": self.algo_session.id,
                "broker_symbol_id": broker_symbol.id,
                "product_type": product_type,
                "order_type": order_type,
                "position_type": position_type,
                "quantities": quantities,
                "price": broker_symbol.ltp,
            }

            data = await self.api.exit_position(payload)

            await self.__manage_position(data, broker_symbol)

    async def exit_all_positions(self) -> None:
        async with self.processing():
            print("exiting all positions")

            payload: List[Dict[str, Any]] = [
                {
                    "position_id": position.id,
                    "algo_session_id": self.algo_session.id,
                    "broker_symbol_id": position.broker_symbol.id,
                    "product_type": position.product_type,
                    "order_type": position.order_type,
                    "position_type": position.position_type,
                    "quantities": position.net_quantities,
                    "price": position.broker_symbol.ltp,
                }
                for position in self.open_positions
            ]

            data = await self.api.exit_all_positions({"items": payload})

            self.__orders = [
                await self.get_order_info(order) for order in data["orders"]
            ]

            self.__positions = [
                await self.get_position_info(position) for position in data["positions"]
            ]

    async def next(self) -> None:
        for position in self.open_positions:
            await position.next()

    @abstractmethod
    async def get_product_types(self) -> Dict[Any, Any]:
        raise NotImplementedError

    @abstractmethod
    async def get_order_types(self) -> Dict[Any, Any]:
        raise NotImplementedError

    @abstractmethod
    async def get_position_types(self) -> Dict[Any, Any]:
        raise NotImplementedError

    @abstractmethod
    async def set_initial_capital(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def set_current_capital(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def start_connection(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def stop_connection(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def subscribe(self, broker_symbol: BrokerSymbol) -> None:
        raise NotImplementedError

    @abstractmethod
    async def fetch_quotes(self, broker_symbol: BrokerSymbol) -> None:
        raise NotImplementedError

    @abstractmethod
    async def fetch_bars(
        self,
        broker_symbol: BrokerSymbol,
        timeframe: timedelta,
        fetch_from: datetime,
        fetch_to: datetime,
    ) -> List[List[Any]]:
        raise NotImplementedError
