import asyncio
import os
import polars as pl

from asyncio import AbstractEventLoop, sleep
from datetime import datetime, timedelta
from typing import Any, Dict, List
from logzero import logger

from proalgotrader_core._helpers.get_data_path import get_data_path
from proalgotrader_core.api import Api
from proalgotrader_core.args_manager import ArgsManager
from proalgotrader_core.base_symbol import BaseSymbol
from proalgotrader_core.broker_symbol import BrokerSymbol
from proalgotrader_core.protocols.algorithm import AlgorithmProtocol
from proalgotrader_core.protocols.enums.account_type import AccountType
from proalgotrader_core.protocols.enums.order_type import OrderType
from proalgotrader_core.protocols.enums.position_type import PositionType
from proalgotrader_core.protocols.position_manager import PositionManagerProtocol
from proalgotrader_core.protocols.signal_manager import SignalManagerProtocol
from proalgotrader_core.protocols.algorithm_factory import AlgorithmFactoryProtocol


class BaseAlgorithm(AlgorithmProtocol):
    def __init__(
        self,
        algorithm_factory: AlgorithmFactoryProtocol,
        event_loop: AbstractEventLoop,
        args_manager: ArgsManager,
        api: Api,
        algo_session_info: Dict[str, Any],
    ) -> None:
        self.algorithm_factory = algorithm_factory
        self.event_loop = event_loop
        self.args_manager = args_manager
        self.api = api
        self.algo_session_info = algo_session_info

        self.algo_session = self.algorithm_factory.get_algo_session(
            algo_session_info=self.algo_session_info,
        )

        self.notification_manager = self.algorithm_factory.get_notification_manager(
            algo_session=self.algo_session,
        )

        self.order_broker_manager = self.algorithm_factory.get_order_broker_manager(
            algorithm=self,
            api=self.api,
            algo_session=self.algo_session,
            notification_manager=self.notification_manager,
        )

        self.chart_manager = self.algorithm_factory.get_chart_manager(
            algorithm=self,
        )

        self.account_type: AccountType = AccountType.CASH_POSITIONAL

        self.__signals: List[SignalManagerProtocol] = []

        self.position_manager: PositionManagerProtocol | None = None

        self.interval = timedelta(seconds=1)

        self.__trading_days: pl.DataFrame | None = None

        self.__booted = False

    async def get_trading_days(self) -> pl.DataFrame:
        if self.__trading_days is None:
            self.__trading_days = await self.__fetch_trading_days()

        return self.__trading_days

    async def get_market_status(self) -> str:
        try:
            trading_days = await self.get_trading_days()

            if os.getenv("24_7_MARKET") == "true":
                return "market_opened"

            if self.current_datetime.date() not in trading_days["date"].to_list():
                return "trading_closed"

            if self.current_datetime < self.pre_market_time:
                return "before_market_opened"

            if (self.current_datetime >= self.pre_market_time) and (
                self.current_datetime < self.market_start_datetime
            ):
                return "pre_market_opened"

            if self.current_datetime > self.market_end_datetime:
                return "after_market_closed"

            return "market_opened"
        except Exception as e:
            logger.debug(e)
            raise Exception(e)

    async def __validate_market_status(self) -> None:
        try:
            while True:
                market_status = await self.get_market_status()

                if market_status == "trading_closed":
                    raise Exception("trading is closed")
                elif market_status == "after_market_closed":
                    raise Exception("market is closed")
                elif market_status == "before_market_opened":
                    raise Exception("market is not opened yet")
                elif market_status == "pre_market_opened":
                    logger.info("market will be opened soon")
                    await sleep(1)
                elif market_status == "market_opened":
                    break
                else:
                    raise Exception("Invalid market status")
        except Exception as e:
            logger.debug(e)
            raise Exception(e)

    async def __fetch_trading_days(self) -> pl.DataFrame:
        data_path = await get_data_path(self.current_datetime)

        file = f"{data_path}/trading_days.csv"

        try:
            return pl.read_csv(file, try_parse_dates=True)
        except FileNotFoundError:
            trading_days = await self.api.get_trading_days()

            def get_json(date: str) -> Dict[str, Any]:
                dt = datetime.strptime(date, "%Y-%m-%d")

                return {
                    "date": dt.strftime("%Y-%m-%d"),
                    "day": dt.strftime("%A"),
                    "year": dt.year,
                }

            df = pl.DataFrame(
                data=[get_json(trading_day["date"]) for trading_day in trading_days],
            )

            df.write_csv(file)

        return pl.read_csv(file, try_parse_dates=True)

    async def _get_fno_expiry(
        self,
        expiry_type,
        expiry_input,
        base_symbol: BaseSymbol,
        market_type: str,
        segment_type: str,
    ) -> str:
        try:
            if not expiry_input:
                raise Exception("Expiry input is required")

            if not isinstance(expiry_input, tuple):
                raise Exception("Expiry input must be a tuple")

            expiry_period, expiry_number = expiry_input

            if expiry_type == "future" and expiry_period != "Monthly":
                raise Exception("Future expiry must be Monthly")

            if expiry_period not in ["Weekly", "Monthly"]:
                raise Exception("Expiry period must be Weekly or Monthly")

            if expiry_number < 0:
                raise Exception("Expiry number must be 0 or greater")

            payload = {
                "base_symbol_id": base_symbol.id,
                "market_type": market_type,
                "segment_type": segment_type,
                "expiry_input": expiry_input,
            }

            expiry_date = await self.api.get_fno_expiry(payload)

            if not expiry_date:
                raise Exception("There was some error fetching expiry date")

            return expiry_date
        except Exception as e:
            logger.debug(e)
            raise Exception(e)

    async def _place_order(
        self,
        broker_symbol: BrokerSymbol | None,
        quantities: int,
        position_type: PositionType,
        order_type: OrderType,
    ) -> None:
        market_type, product_type = self.account_type.value

        try:
            if not isinstance(broker_symbol, BrokerSymbol):
                raise Exception("Symbol must be instance of BrokerSymbol")

            if not quantities:
                raise Exception("Quantities is required")

            if broker_symbol.market_type != market_type.value:
                raise Exception("Invalid market type")

            if not broker_symbol.can_trade:
                raise Exception("Can not trade in this symbol")

            if (
                self.account_type == AccountType.CASH_POSITIONAL
                and position_type == PositionType.SELL
            ):
                raise Exception("Equity can't be sold")

            if order_type not in OrderType:
                raise Exception("Invalid order type")

            if quantities % broker_symbol.base_symbol.lot_size != 0:
                raise Exception("Invalid quantities")

            logger.debug(
                f"Placing order, Symbol: {broker_symbol.symbol_name} @ {broker_symbol.ltp} - Qty: {quantities}"
            )

            await self.order_broker_manager.enter_position(
                broker_symbol=broker_symbol,
                quantities=quantities,
                product_type=product_type.value,
                order_type=order_type.value,
                position_type=position_type.value,
            )

            await self.order_broker_manager.set_current_capital()
        except Exception as e:
            raise Exception(e)

    async def boot(self) -> None:
        try:
            if self.__booted:
                raise Exception("Algorithm already booted")

            logger.debug("booting algo")

            await self.notification_manager.connect()

            if self.args_manager.environment == "production":
                await self.algo_session.project.clone_repository(api=self.api)

            await self.__validate_market_status()

            await self.order_broker_manager.initialize()

            await self.order_broker_manager.start_connection()
        except Exception as e:
            logger.debug(e)
            raise Exception(e)

    async def run(self) -> None:
        try:
            if self.__booted:
                raise Exception("Algorithm already booted")

            logger.debug("market is opened")

            await self.__initialize()

            await self.__next()
        except Exception as e:
            logger.debug(e)
            raise Exception(e)

    async def __initialize(self) -> None:
        try:
            logger.debug("running initialize")

            await self.order_broker_manager.set_initial_capital()

            await self.order_broker_manager.set_portfolio()

            await self.order_broker_manager.set_current_capital()

            await self.initialize()
        except Exception as e:
            logger.debug(e)
            raise Exception(e)

    async def __next(self) -> None:
        try:
            self.__booted = True

            logger.debug("running Algorithm@next")

            market_status = await self.get_market_status()

            while market_status == "market_opened":
                if self.chart_manager.charts:
                    await self.__chart_next()

                if not self.order_broker_manager.is_processing():
                    if self.__signals:
                        await self.__signal_next()

                    await self.next()

                    await self.order_broker_manager.next()

                await sleep(self.interval.seconds)

            if market_status == "after_market_closed":
                await self.order_broker_manager.on_after_market_closed()

                logger.debug("market is closed")
        except Exception as e:
            logger.debug(e)
            raise Exception(e)

    async def __signal_next(self) -> None:
        try:
            tasks = []

            for signal in self.__signals:
                task = asyncio.create_task(signal.next())
                tasks.append(task)

            await asyncio.gather(*tasks)
        except Exception as e:
            logger.debug(e)
            raise Exception(e)

    async def __chart_next(self) -> None:
        try:
            tasks = []

            for chart in self.chart_manager.charts:
                task = asyncio.create_task(chart.next())
                tasks.append(task)

            await asyncio.gather(*tasks)
        except Exception as e:
            logger.debug(e)
            raise Exception(e)
