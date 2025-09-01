import asyncio
import threading

from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List

from logzero import logger
from tenacity import retry, stop_after_attempt, wait_fixed

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

from fyers_apiv3.FyersWebsocket.data_ws import (
    FyersDataSocket,
)  # pyright: ignore[reportMissingStubs]

from fyers_apiv3.fyersModel import FyersModel

from proalgotrader_core.tick import Tick
from proalgotrader_core.token_managers.fyers_token_manager import FyersTokenManager


class FyersOrderBrokerManager(BaseOrderBrokerManager):
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

        logger.info("FyersDataManager: getting token manager")

        self.token_manager = FyersTokenManager(
            username=self.broker_config["username"],
            totp_key=self.broker_config["totp_key"],
            pin=self.broker_config["pin"],
            api_key=self.broker_config["api_key"],
            secret_key=self.broker_config["api_secret"],
            redirect_url=self.broker_config["redirect_url"],
        )

        self.http_client: FyersModel | None = None
        self.ws_client: FyersDataSocket | None = None
        self.ws_connected = False

        self.resolutions = {
            timedelta(minutes=1): "1",
            timedelta(minutes=3): "3",
            timedelta(minutes=5): "5",
            timedelta(minutes=15): "15",
            timedelta(minutes=30): "30",
            timedelta(hours=1): "60",
            timedelta(hours=2): "120",
            timedelta(hours=3): "180",
            timedelta(hours=4): "240",
            timedelta(days=1): "D",
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
        print("fyers order broker initializing")

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
            if not self.ws_client:
                logger.info("WebSocket client not initialized")
                return

            logger.info("Setting up WebSocket callbacks...")

            self.ws_client.on_open = self.on_open
            self.ws_client.on_close = self.on_close
            self.ws_client.On_error = self.on_error
            self.ws_client.On_message = self.on_data

            logger.info("Starting WebSocket connection in background thread...")

            connection_thread = threading.Thread(
                target=self.ws_client.connect, daemon=True
            )

            connection_thread.start()

        except Exception as e:
            logger.info(f"Fyers: Error starting connection: {e}")
            raise Exception(e)

    def on_open(self):
        logger.info("✅ WebSocket connection opened successfully")
        self.ws_connected = True

    def on_close(self, message: Any):
        logger.info("❌ WebSocket connection closed")
        self.ws_connected = False

    def on_error(self, error: Any):
        logger.info(f"❌ WebSocket error: {error}")
        self.ws_connected = False

    def on_data(self, message: Any):
        try:
            if message.get("type") not in ["if", "sf"]:
                return

            for subscriber in self.subscribers:
                broker_symbol: BrokerSymbol = subscriber["broker_symbol"]

                on_tick: Callable[..., Any] = subscriber["on_tick"]

                if broker_symbol.symbol_name == message.get("symbol"):
                    ltp = message.get("ltp", 0)

                    total_volume = message.get("vol_traded_today", 0)

                    last_traded_time = message.get(
                        "last_traded_time", self.algo_session.current_timestamp
                    )

                    tick = Tick(
                        broker_symbol=broker_symbol,
                        current_timestamp=last_traded_time,
                        ltp=ltp,
                        total_volume=total_volume,
                    )

                    # Schedule the on_tick coroutine in the main event loop
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

        try:
            self.ws_client.subscribe(
                symbols=[broker_symbol.symbol_name], data_type="SymbolUpdate"
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

            payload = {"symbols": broker_symbol.symbol_name}

            response = self.http_client.quotes(data=payload)

            if not isinstance(response, dict):
                raise Exception("Invalid response")

            data = response.get("d")

            if not data:
                raise Exception("Error fetching quotes", broker_symbol.symbol_name)

            quote_data = data[0]["v"]
            ltp = quote_data.get("lp")
            total_volume = quote_data.get("volume")

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
        try:
            payload = {
                "symbol": broker_symbol.symbol_name,
                "resolution": self.resolutions[timeframe],
                "date_format": "0",
                "range_from": int(fetch_from.timestamp()),
                "range_to": int(fetch_to.timestamp()),
                "cont_flag": "1",
            }

            if not self.http_client:
                logger.info("HTTP client not initialized; cannot fetch candles")
                return []

            response = self.http_client.history(data=payload)

            if not isinstance(response, dict):
                raise Exception("Invalid response")

            if not response["candles"]:
                raise Exception("Error fetching bars")

            def get_bar_item(bar: List[Any]) -> List[Any]:
                bar_item = Bar(
                    broker_symbol=broker_symbol,
                    current_timestamp=bar[0],
                    open=bar[1],
                    high=bar[2],
                    low=bar[3],
                    close=bar[4],
                    volume=bar[5],
                )

                return bar_item.get_item()

            bars = [get_bar_item(bar) for bar in response["candles"]]

            return bars
        except Exception as e:
            logger.debug(e)
            raise Exception(e)
