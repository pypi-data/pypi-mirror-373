from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List

import asyncio
import threading

from logzero import logger
from tenacity import retry, stop_after_attempt, wait_fixed

from SmartApi import SmartConnect
from SmartApi.smartWebSocketV2 import SmartWebSocketV2

from proalgotrader_core.algo_session import AlgoSession
from proalgotrader_core.api import Api
from proalgotrader_core.bar import Bar
from proalgotrader_core.broker_symbol import BrokerSymbol
from proalgotrader_core.notification_manager import NotificationManager
from proalgotrader_core.order_broker_managers.base_order_broker_manager import (
    BaseOrderBrokerManager,
)
from proalgotrader_core.protocols.algorithm import AlgorithmProtocol
from proalgotrader_core.protocols.enums.order_type import OrderType
from proalgotrader_core.protocols.enums.position_type import PositionType
from proalgotrader_core.protocols.enums.product_type import ProductType
from proalgotrader_core.tick import Tick
from proalgotrader_core.token_managers.angel_one_token_manager import (
    AngelOneTokenManager,
)


class AngelOneOrderBrokerManager(BaseOrderBrokerManager):
    def __init__(
        self,
        api: Api,
        algo_session: AlgoSession,
        notification_manager: NotificationManager,
        algorithm: AlgorithmProtocol,
    ) -> None:
        super().__init__(
            api=api,
            algo_session=algo_session,
            notification_manager=notification_manager,
            algorithm=algorithm,
        )

        logger.info("AngelOneDataManager: getting token manager")

        self.token_manager = AngelOneTokenManager(
            username=self.broker_config["username"],
            totp_key=self.broker_config["totp_key"],
            mpin=self.broker_config["pin"],
            api_key=self.broker_config["api_key"],
            api_secret=self.broker_config["api_secret"],
            redirect_url=self.broker_config["redirect_url"],
        )

        self.http_client: SmartConnect | None = None
        self.ws_client: SmartWebSocketV2 | None = None
        self.ws_connected = False

        self.resolutions = {
            timedelta(minutes=1): "ONE_MINUTE",
            timedelta(minutes=3): "THREE_MINUTE",
            timedelta(minutes=5): "FIVE_MINUTE",
            timedelta(minutes=15): "FIFTEEN_MINUTE",
            timedelta(minutes=30): "THIRTY_MINUTE",
            timedelta(hours=1): "ONE_HOUR",
            timedelta(hours=2): "TWO_HOUR",
            timedelta(hours=3): "THREE_HOUR",
            timedelta(hours=4): "FOUR_HOUR",
            timedelta(days=1): "ONE_DAY",
        }

    async def set_initial_capital(self) -> None:
        self.initial_capital = self.algo_session.initial_capital

    async def set_current_capital(self) -> None:
        self.current_capital = self.algo_session.current_capital

    async def get_order_types(self) -> Dict[Any, Any]:
        return {
            OrderType.LIMIT_ORDER.value: 1,
            1: OrderType.LIMIT_ORDER.value,
            OrderType.MARKET_ORDER.value: 2,
            2: OrderType.MARKET_ORDER.value,
            OrderType.STOP_ORDER.value: 3,
            3: OrderType.STOP_ORDER.value,
            OrderType.STOP_LIMIT_ORDER.value: 4,
            4: OrderType.STOP_LIMIT_ORDER.value,
        }

    async def get_position_types(self) -> Dict[Any, Any]:
        return {
            PositionType.BUY.value: 1,
            1: PositionType.BUY.value,
            PositionType.SELL.value: -1,
            -1: PositionType.SELL.value,
        }

    async def get_product_types(self) -> Dict[Any, Any]:
        return {
            ProductType.MIS.value: "INTRADAY",
            "INTRADAY": ProductType.MIS.value,
            ProductType.NRML.value: "MARGIN",
            "MARGIN": ProductType.NRML.value,
            ProductType.CNC.value: "CNC",
            "CNC": ProductType.CNC.value,
        }

    async def initialize(self):
        await super().initialize()
        print("angel one order broker initializing")

        await self.token_manager.initialize(
            token=self.algo_session.broker_token_info["token"],
            feed_token=self.algo_session.broker_token_info["feed_token"],
        )

        self.http_client = self.token_manager.http_client
        self.ws_client = self.token_manager.ws_client

    async def stop_connection(self):
        if self.ws_client:
            self.ws_client.close_connection()

        self.ws_connected = False

    async def start_connection(self):
        try:
            print("AngelOne: starting connection")

            if not self.ws_client:
                logger.info("WebSocket client not initialized")
                return

            logger.info("Setting up WebSocket callbacks...")

            self.ws_client.on_open = self.on_open
            self.ws_client.on_close = self.on_close
            self.ws_client.on_error = self.on_error
            self.ws_client.on_data = self.on_data

            logger.info("Starting WebSocket connection in background thread...")

            connection_thread = threading.Thread(
                target=self.ws_client.connect, daemon=True
            )

            connection_thread.start()

        except Exception as e:
            logger.info(f"AngelOne: Error starting connection: {e}")
            raise Exception(e)

    def on_open(self, wsapp: Any):
        logger.info("✅ WebSocket connection opened successfully")
        self.ws_connected = True

    def on_close(self, wsapp: Any):
        logger.info("❌ WebSocket connection closed")
        self.ws_connected = False

    def on_error(self):
        logger.info("❌ WebSocket error")
        self.ws_connected = False

    def on_data(self, wsapp: Any, message: Any):
        try:
            for subscriber in self.subscribers:
                broker_symbol: BrokerSymbol = subscriber["broker_symbol"]

                on_tick: Callable[..., Any] = subscriber["on_tick"]

                if broker_symbol.exchange_token == int(message.get("token")):
                    ltp = message.get("last_traded_price", 0) / 100

                    total_volume = message.get("volume_trade_for_the_day", 0)

                    exchange_timestamp_ms = message.get(
                        "exchange_timestamp", self.algo_session.current_timestamp * 1000
                    )

                    exchange_timestamp = int(exchange_timestamp_ms / 1000)

                    tick = Tick(
                        broker_symbol=broker_symbol,
                        current_timestamp=exchange_timestamp,
                        ltp=ltp,
                        total_volume=total_volume,
                    )

                    asyncio.run_coroutine_threadsafe(
                        coro=on_tick(tick),
                        loop=self.algorithm.event_loop,
                    )
        except Exception as e:
            logger.debug(e)
            raise Exception(e)

    async def subscribe(self, broker_symbol: BrokerSymbol) -> None:
        if not self.ws_client:
            logger.info("WebSocket client not initialized; skipping live subscribe")
            return

        exchange_type = 1 if broker_symbol.segment_type == "Equity" else 2

        try:
            self.ws_client.subscribe(
                correlation_id="abc123",
                mode=2,
                token_list=[
                    {
                        "exchangeType": exchange_type,
                        "tokens": [broker_symbol.exchange_token],
                    }
                ],
            )

            await self.subscribe_tick(broker_symbol, broker_symbol.on_tick)

            broker_symbol.subscribed = True
        except Exception as e:
            logger.info(f"Subscribe failed: {e}")
            raise Exception(e)

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(3))
    async def fetch_quotes(self, broker_symbol: BrokerSymbol) -> None:
        try:
            logger.debug(f"fetching quotes {broker_symbol.symbol_name}")

            if not self.http_client:
                raise Exception("HTTP client not initialized; cannot fetch quotes")

            exchangeTokens = {
                "NSE" if broker_symbol.segment_type == "Equity" else "NFO": [
                    broker_symbol.exchange_token
                ]
            }

            response = self.http_client.getMarketData(
                mode="FULL",
                exchangeTokens=exchangeTokens,
            )

            if not isinstance(response, dict):
                raise Exception("Invalid response")

            data = response.get("data")

            if not data:
                raise Exception("Error fetching quotes", broker_symbol.symbol_name)

            data = data["fetched"][0]
            ltp = data.get("ltp")
            total_volume = data.get("tradeVolume")

            await broker_symbol.on_bar(ltp, total_volume)
        except Exception as e:
            logger.debug(e)
            raise Exception(e)

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(3))
    async def fetch_bars(
        self,
        broker_symbol: BrokerSymbol,
        timeframe: timedelta,
        fetch_from: datetime,
        fetch_to: datetime,
    ) -> List[List[Any]]:
        historicDataParams = {
            "exchange": "NSE" if broker_symbol.segment_type == "Equity" else "NFO",
            "symboltoken": broker_symbol.exchange_token,
            "interval": self.resolutions[timeframe],
            "fromdate": fetch_from.strftime("%Y-%m-%d %H:%M"),
            "todate": fetch_to.strftime("%Y-%m-%d %H:%M"),
        }

        response = self.http_client.getCandleData(historicDataParams=historicDataParams)

        if not isinstance(response, dict):
            raise Exception("Invalid response")

        if not response["status"]:
            raise Exception("Error fetching bars")

        def get_bar_item(bar: List[Any]) -> List[Any]:
            bar_item = Bar(
                broker_symbol=broker_symbol,
                current_timestamp=int(datetime.fromisoformat(bar[0]).timestamp()),
                open=bar[1],
                high=bar[2],
                low=bar[3],
                close=bar[4],
                volume=bar[5],
            )

            return bar_item.get_item()

        bars = [get_bar_item(bar) for bar in response["data"]]

        return bars
