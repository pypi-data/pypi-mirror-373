import polars as pl

from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from logzero import logger

from proalgotrader_core.broker_symbol import BrokerSymbol
from proalgotrader_core.protocols.chart_protocol import ChartProtocol
from proalgotrader_core.protocols.algorithm import AlgorithmProtocol
from proalgotrader_core.protocols.enums.candle_type import CandleType


class ChartManager:
    def __init__(self, algorithm: AlgorithmProtocol) -> None:
        self.algorithm = algorithm
        self.algo_session = algorithm.algo_session
        self.order_broker_manager = algorithm.order_broker_manager

        # store protocol-typed charts to avoid importing concrete Chart at module import time
        self.__charts: Dict[Tuple[int, timedelta, CandleType], ChartProtocol] = {}

        self.warmup_days = {
            timedelta(minutes=1): 2,
            timedelta(minutes=3): 4,
            timedelta(minutes=5): 6,
            timedelta(minutes=15): 16,
            timedelta(minutes=30): 32,
            timedelta(hours=1): 60,
            timedelta(hours=2): 100,
            timedelta(hours=3): 150,
            timedelta(hours=4): 200,
            timedelta(days=1): 400,
        }

    @property
    def charts(self) -> List[ChartProtocol]:
        return [chart for chart in self.__charts.values()]

    async def get_chart(self, key: Tuple[int, timedelta, CandleType]) -> ChartProtocol | None:
        try:
            return self.__charts[key]
        except KeyError:
            return None

    async def register_chart(
        self,
        broker_symbol: BrokerSymbol,
        timeframe: timedelta,
        candle_type: CandleType = CandleType.REGULAR,
        **kwargs,
    ) -> ChartProtocol:
        try:
            key = (broker_symbol.exchange_token, timeframe, candle_type)

            exists = await self.get_chart(key)

            if exists:
                return exists
            else:
                # Import concrete Chart at runtime to avoid circular import during module import
                from proalgotrader_core.chart import Chart

                chart = Chart(
                    chart_manager=self,
                    algo_session=self.algo_session,
                    order_broker_manager=self.order_broker_manager,
                    broker_symbol=broker_symbol,
                    timeframe=timeframe,
                    candle_type=candle_type,
                    **kwargs,
                )

                self.__charts[key] = chart

                await chart.initialize()

                return chart
        except Exception as e:
            logger.debug(e)
            raise Exception(e)

    async def __get_warmups_days(self, timeframe: timedelta) -> int:
        try:
            return self.warmup_days[timeframe]
        except KeyError:
            raise Exception("Invalid timeframe")

    async def fetch_ranges(self, timeframe: timedelta) -> Tuple[datetime, datetime]:
        trading_days = await self.algorithm.get_trading_days()
        warmups_days = await self.__get_warmups_days(timeframe)

        past_days = trading_days.filter(
            pl.col("date") < self.algo_session.current_datetime.date()
        ).sort("date")

        warmups_from = past_days.tail(warmups_days).head(1).select("date").item()

        fetch_from_epoch = datetime.fromisoformat(str(warmups_from)).replace(
            hour=self.algo_session.market_start_time.hour,
            minute=self.algo_session.market_start_time.minute,
            second=self.algo_session.market_start_time.second,
            microsecond=0,
        )

        return fetch_from_epoch, self.algo_session.current_datetime

    def get_current_candle(self, timeframe: timedelta) -> datetime:
        try:
            if timeframe == timedelta(days=1):
                return datetime.now(tz=self.algo_session.tz_info).replace(
                    hour=5,
                    minute=30,
                    second=0,
                    microsecond=0,
                    tzinfo=None,
                )

            current_candle_timedelta: timedelta = (
                self.algo_session.current_datetime
                - self.algo_session.market_start_datetime
            )

            seconds, _ = divmod(
                int(current_candle_timedelta.seconds), int(timeframe.total_seconds())
            )

            return self.algo_session.market_start_datetime + timedelta(
                seconds=seconds * timeframe.total_seconds()
            )
        except Exception as e:
            logger.debug(e)
            raise Exception(e)
