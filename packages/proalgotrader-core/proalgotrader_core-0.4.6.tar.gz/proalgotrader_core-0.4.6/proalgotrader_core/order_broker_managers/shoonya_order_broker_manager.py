from datetime import datetime, timedelta
from typing import Any, Dict, List

from logzero import logger
from tenacity import retry, stop_after_attempt, wait_fixed

from proalgotrader_core.algo_session import AlgoSession
from proalgotrader_core.api import Api
from proalgotrader_core.broker_symbol import BrokerSymbol
from proalgotrader_core.notification_manager import NotificationManager
from proalgotrader_core.order_broker_managers.base_order_broker_manager import (
    BaseOrderBrokerManager,
)
from proalgotrader_core.protocols.algorithm import AlgorithmProtocol
from proalgotrader_core.protocols.enums.order_type import OrderType
from proalgotrader_core.protocols.enums.position_type import PositionType
from proalgotrader_core.protocols.enums.product_type import ProductType
from proalgotrader_core.token_managers.shoonya_token_manager import ShoonyaTokenManager


class ShoonyaOrderBrokerManager(BaseOrderBrokerManager):
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

        logger.info("ShoonyaDataManager: getting token manager")

        # Map expected config to token manager signature
        self.token_manager = ShoonyaTokenManager(
            user_id=self.broker_config["user_id"],
            password=self.broker_config["password"],
            totp_key=self.broker_config["totp_key"],
            vendor_code=self.broker_config["vendor_code"],
            api_secret=self.broker_config["api_secret"],
            imei=self.broker_config["imei"],
        )

        self.http_client = None
        self.ws_client = None
        self.ws_connected = False

        self.resolutions = {
            timedelta(minutes=1): "1",
            timedelta(minutes=3): "3",
            timedelta(minutes=5): "5",
            timedelta(minutes=15): "15",
            timedelta(minutes=30): "30",
            timedelta(hours=1): "60",
            timedelta(days=1): "D",
        }

    async def set_initial_capital(self) -> None:
        self.initial_capital = self.algo_session.initial_capital

    async def set_current_capital(self) -> None:
        self.current_capital = self.algo_session.current_capital

    async def initialize(self):
        await super().initialize()
        print("shoonya order broker initializing")

        await self.token_manager.initialize(
            token=self.algo_session.broker_token_info["token"],
            feed_token=self.algo_session.broker_token_info["feed_token"],
        )

        self.http_client = self.token_manager.http_client
        self.ws_client = self.token_manager.ws_client

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

    async def start_connection(self):
        try:
            pass
        except Exception as e:
            logger.info(f"Error starting Shoonya connection: {e}")
            raise Exception(e)

    async def stop_connection(self):
        try:
            pass
        except Exception as e:
            logger.info(f"Error stopping Shoonya WebSocket: {e}")
            raise Exception(e)

    async def on_open(self, wsapp):
        logger.info("✅ Shoonya WebSocket connection opened successfully")
        self.ws_connected = True

    async def on_close(self, wsapp):
        logger.info("❌ Shoonya WebSocket connection closed")
        self.ws_connected = False

    async def on_error(self, wsapp, error):
        logger.info(f"❌ Shoonya WebSocket error: {error}")
        self.ws_connected = False

    async def on_data(self, wsapp, message: Dict[str, Any]):
        try:
            pass
        except Exception as e:
            logger.debug(e)
            raise Exception(e)

    async def subscribe(self, broker_symbol: BrokerSymbol) -> None:
        try:
            pass
        except Exception as e:
            logger.info(f"Shoonya subscribe error: {e}")
            raise Exception(e)

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(3))
    async def fetch_quotes(self, broker_symbol: BrokerSymbol) -> None:
        try:
            pass
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
            return []
        except Exception as e:
            logger.debug(e)
            raise Exception(e)
