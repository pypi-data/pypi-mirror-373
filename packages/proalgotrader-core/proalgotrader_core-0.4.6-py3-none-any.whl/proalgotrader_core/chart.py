from __future__ import annotations

import asyncio
import polars as pl

from logzero import logger

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, cast

from proalgotrader_core.broker_symbol import BrokerSymbol
from proalgotrader_core.indicators.indicator import Indicator
from proalgotrader_core.order_broker_managers.base_order_broker_manager import (
    BaseOrderBrokerManager,
)
from proalgotrader_core.protocols.enums.candle_type import CandleType
from proalgotrader_core.candle_processors import CandleProcessorFactory, BaseCandleProcessor

# Use lightweight typing protocols to avoid circular imports at runtime
from proalgotrader_core.protocols.chart_manager import ChartManagerProtocol
from proalgotrader_core.protocols.algo_session import AlgoSessionProtocol
from proalgotrader_core.protocols.tick import TickProtocol


class Chart:
    def __init__(
        self,
        *,
        chart_manager: ChartManagerProtocol,
        algo_session: AlgoSessionProtocol,
        order_broker_manager: BaseOrderBrokerManager,
        broker_symbol: BrokerSymbol,
        timeframe: timedelta,
        candle_type: CandleType = CandleType.REGULAR,
        **kwargs,
    ) -> None:
        self.chart_manager = chart_manager
        self.algo_session = algo_session
        self.order_broker_manager = order_broker_manager
        self.broker_symbol = broker_symbol
        self.timeframe = timeframe
        self.candle_type = candle_type

        self.__columns = [
            "current_candle",
            "current_timestamp",
            "current_datetime",
            "symbol",
            "open",
            "high",
            "low",
            "close",
            "volume",
        ]

        self.__df: pl.DataFrame = pl.DataFrame()

        self.current_candle_datetime = self.chart_manager.get_current_candle(
            self.timeframe
        )

        self.__indicators: Dict[str, Indicator] = {}

        # Initialize candle processor
        self.__candle_processor: Optional[BaseCandleProcessor] = None
        self.__candle_processor_kwargs = kwargs

    @property
    def next_candle_datetime(self) -> datetime:
        return self.current_candle_datetime + self.timeframe

    @property
    def ltp(self) -> float:
        return self.broker_symbol.ltp

    @property
    def df(self) -> pl.DataFrame:
        return self.__df

    @property
    def data(self) -> pl.DataFrame:
        return self.__df.filter(
            [pl.col("current_candle") <= self.algo_session.current_datetime]
        )

    async def get_data(
        self, row_number: int = 0, column_name: Optional[str] = None
    ) -> Any:
        if row_number > 0:
            raise Exception("Invalid row number")

        actual_row_number = row_number - 1

        data = self.data[actual_row_number]

        if column_name:
            if column_name not in data.columns:
                raise Exception(
                    f"Column '{column_name}' not found. Available: {data.columns}"
                )
            # Return scalar value instead of Series
            return data[column_name].item()

        return data

    async def initialize(self) -> None:
        # Initialize candle processor
        self.__candle_processor = await CandleProcessorFactory.create_processor(
            self.candle_type, **self.__candle_processor_kwargs
        )

        self.fetch_from, self.fetch_to = await self.chart_manager.fetch_ranges(
            self.timeframe
        )

        bars = await self.__fetch_bars()

        self.__df = pl.DataFrame(data=bars, schema=self.__columns, orient="row")

        await self.order_broker_manager.subscribe_tick(self.broker_symbol, self.on_tick)

    async def next(self) -> None:
        logger.info("running chart@next")

    async def __fetch_bars(self) -> List[Any]:
        try:
            return await self.order_broker_manager.fetch_bars(
                broker_symbol=self.broker_symbol,
                timeframe=self.timeframe,
                fetch_from=self.fetch_from,
                fetch_to=self.fetch_to,
            )
        except Exception as e:
            logger.debug(e)
            raise Exception(e)

    def is_new_candle(self) -> bool:
        new_candle = self.algo_session.current_datetime > self.next_candle_datetime

        if new_candle:
            self.current_candle_datetime = self.chart_manager.get_current_candle(
                self.timeframe
            )

        return new_candle

    async def on_tick(self, tick: TickProtocol):
        try:
            logger.info("running Chart@on_tick")

            await self.update_chart(tick)

            await self.update_chart_indicators()
        except Exception as e:
            logger.debug(e)
            raise Exception(e)

    async def update_existing_candle(self, tick: TickProtocol):
        last_open_literal = self.__df.get_column("open").last()
        last_high_literal = self.__df.get_column("high").last()
        last_low_literal = self.__df.get_column("low").last()
        last_close_literal = self.__df.get_column("close").last()

        last_open = last_open_literal if isinstance(last_open_literal, float) else 0
        last_high = last_high_literal if isinstance(last_high_literal, float) else 0
        last_low = last_low_literal if isinstance(last_low_literal, float) else 0
        last_close = last_close_literal if isinstance(last_close_literal, float) else 0

        # Process candle data using the appropriate processor
        cp = self.__candle_processor
        if cp is None:
            raise RuntimeError("Candle processor not initialized")

        processed_data = await cp.process_existing_candle(
            current_open=last_open,
            current_high=last_high,
            current_low=last_low,
            current_close=last_close,
            ltp=tick.ltp,
            volume=self.__get_bar_volume(tick.total_volume),
        )

        tick_item: List[Any] = [
            self.current_candle_datetime,
            tick.current_timestamp,
            tick.current_datetime,
            tick.broker_symbol,
            processed_data["open"],
            processed_data["high"],
            processed_data["low"],
            processed_data["close"],
            processed_data["volume"],
        ]

        updated_row = pl.DataFrame(
            data=[tick_item],
            schema=self.__columns,
            orient="row",
        )

        self.__df = pl.concat([self.__df[:-1], updated_row])

    async def add_new_candle(self, tick: TickProtocol):
        # Process new candle data using the appropriate processor
        cp = self.__candle_processor
        if cp is None:
            raise RuntimeError("Candle processor not initialized")

        processed_data = await cp.process_new_candle(
            ltp=tick.ltp, volume=self.__get_bar_volume(tick.total_volume)
        )

        tick_item: List[Any] = [
            self.current_candle_datetime,
            tick.current_timestamp,
            tick.current_datetime,
            tick.broker_symbol,
            processed_data["open"],
            processed_data["high"],
            processed_data["low"],
            processed_data["close"],
            processed_data["volume"],
        ]

        new_row = pl.DataFrame(
            data=[tick_item],
            schema=self.__columns,
            orient="row",
        )

        self.__df = pl.concat([self.__df, new_row])

    async def update_chart(self, tick: TickProtocol):
        try:
            new_candle = self.is_new_candle()

            last_candle = self.__df.get_column("current_candle").last()

            if not new_candle and self.current_candle_datetime == last_candle:
                await self.update_existing_candle(tick)
            else:
                await self.add_new_candle(tick)
        except Exception as e:
            logger.debug(e)
            raise Exception(e)

    def __get_bar_volume(self, total_volume: int) -> int:
        try:
            prev_volume_sum = (
                self.__df.filter(
                    pl.col("current_candle") < self.current_candle_datetime
                )
                .filter(
                    pl.col("current_candle").dt.date() == self.algo_session.current_date
                )
                .select(pl.col("volume").sum().fill_null(0))
                .item()
            )

            return total_volume - prev_volume_sum
        except Exception as e:
            logger.debug(e)
            raise Exception(e)

    async def update_chart_indicators(self):
        try:
            if not self.__indicators:
                return False

            tasks: List[asyncio.Task[None]] = []

            for indicator in self.__indicators.values():
                task = asyncio.create_task(indicator.next(self.__df))
                tasks.append(task)

            await asyncio.gather(*tasks)
        except Exception as e:
            logger.debug(e)
            raise Exception(e)

    async def add_indicator(self, *, key: str, indicator: Indicator | Any) -> Indicator:
        if not isinstance(indicator, Indicator):
            raise Exception("Invalid Indicator")

        if key in self.__indicators:
            return self.__indicators[key]

        # Cast algo_session to Any to avoid importing concrete AlgoSession type for typing-only purposes
        await indicator.initialize(self.__df, cast(Any, self.algo_session))

        self.__indicators[key] = indicator

        return indicator
