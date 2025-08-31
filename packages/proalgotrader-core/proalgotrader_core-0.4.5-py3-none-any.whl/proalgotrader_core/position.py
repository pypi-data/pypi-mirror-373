from logzero import logger
from datetime import datetime
from typing import Callable, Literal, Any, Dict, Optional

from proalgotrader_core.protocols.algorithm import AlgorithmProtocol
from proalgotrader_core.broker_symbol import BrokerSymbol
from proalgotrader_core.protocols.enums.position_type import PositionType
from proalgotrader_core.protocols.enums.product_type import ProductType
from proalgotrader_core.risk_reward import RiskReward


class Position:
    def __init__(
        self,
        position_info: Dict[str, Any],
        broker_symbol: BrokerSymbol,
        algorithm: AlgorithmProtocol,
    ) -> None:
        self.position_info = position_info
        self.broker_symbol: BrokerSymbol = broker_symbol
        self.algorithm: AlgorithmProtocol = algorithm

        self.id: int = position_info["id"]
        self.position_id: str = position_info["position_id"]
        self.position_type: str = position_info["position_type"]
        self.order_type: str = position_info["order_type"]
        self.product_type: str = position_info["product_type"]
        self.net_quantities: int = position_info["net_quantities"]
        self.buy_price: float | None = position_info["buy_price"]
        self.sell_price: float | None = position_info["sell_price"]
        self.buy_quantities: float | None = position_info["buy_quantities"]
        self.sell_quantities: float | None = position_info["sell_quantities"]
        self.status: Literal["open", "closed"] = position_info["status"]
        self.created_at: datetime = position_info["created_at"]
        self.updated_at: datetime = position_info["updated_at"]

        self.risk_reward_info: Optional[Dict[str, Any]] = position_info["risk_reward"]
        self.__risk_reward: RiskReward | None = None

    @property
    def is_buy(self) -> bool:
        return self.position_type == PositionType.BUY.value

    @property
    def is_sell(self) -> bool:
        return self.position_type == PositionType.SELL.value

    @property
    def pnl(self) -> float:
        net_pnl = 0

        if self.is_buy and self.status == "closed":
            net_pnl = (self.sell_price * self.sell_quantities) - (
                self.buy_price * self.buy_quantities
            )

        if self.is_buy and self.status == "open":
            net_pnl = (self.broker_symbol.ltp * self.buy_quantities) - (
                self.buy_price * self.buy_quantities
            )

        if self.is_sell and self.status == "closed":
            net_pnl = (self.buy_price * self.buy_quantities) - (
                self.sell_price * self.sell_quantities
            )

        if self.is_sell and self.status == "open":
            net_pnl = (self.broker_symbol.ltp * self.sell_quantities) - (
                self.sell_price * self.sell_quantities
            )

        return round(net_pnl, 2)

    @property
    def profit(self) -> float:
        if self.pnl >= 0:
            return self.pnl

        return 0

    @property
    def loss(self) -> float:
        if self.pnl <= 0:
            return self.pnl

        return 0

    @property
    def pnl_percent(self) -> float:
        total_volume = (
            self.buy_price * self.buy_quantities
            if self.position_type == "BUY"
            else self.sell_price * self.sell_quantities
        )

        return round((self.pnl * 100) / total_volume, 2)

    @property
    def should_square_off(self) -> bool:
        if self.product_type == ProductType.NRML.value:
            expiry_date = self.algorithm.current_datetime.strftime("%Y-%m-%d")

            return self.broker_symbol.expiry_date == expiry_date
        else:
            return self.product_type == ProductType.MIS.value

    async def initialize(self) -> None:
        if self.algorithm.position_manager and self.status == "open":
            await self.algorithm.position_manager.initialize()

    async def next(self) -> None:
        if self.__risk_reward and self.status == "open":
            await self.__risk_reward.next()

        if self.algorithm.position_manager and self.status == "open":
            await self.algorithm.position_manager.next()

    async def on_after_market_closed(self) -> None:
        if self.should_square_off:
            print(f"closing {self.broker_symbol.symbol_name}, market is closing")

            await self.exit()

    async def exit(self, quantities: int = None) -> None:
        try:
            logger.debug("exiting position")

            exit_position_type: PositionType = (
                PositionType.SELL if self.is_buy else PositionType.BUY
            )

            exit_quantities = quantities if quantities else self.net_quantities

            await self.algorithm.order_broker_manager.exit_position(
                position_id=self.id,
                broker_symbol=self.broker_symbol,
                quantities=exit_quantities,
                product_type=self.product_type,
                order_type=self.order_type,
                position_type=exit_position_type.value,
            )
        except Exception as e:
            logger.debug(e)
            raise Exception(e)

    async def set_risk_reward(
        self,
        *,
        sl: float,
        tgt: float | None = None,
        tsl: float | None = None,
        on_exit: Optional[Callable[..., Any]] = None,
        unit: Literal["points", "percentage"] = "points",
    ) -> None:
        if self.__risk_reward:
            raise Exception("Risk reward already exists")

        base_symbol = await self.algorithm.add_equity(
            symbol_name=self.broker_symbol.base_symbol.value
        )

        if not self.risk_reward_info:
            payload = {
                "broker_symbol_id": self.broker_symbol.id,
                "symbol_price": self.broker_symbol.ltp,
                "base_symbol_price": base_symbol.ltp,
                "sl": round(sl, 2),
                "tgt": round(tgt, 2) if tgt else None,
                "tsl": round(tsl, 2) if tsl else None,
            }

            self.risk_reward_info = await self.algorithm.api.create_risk_reward(
                self.position_id, payload
            )

        self.__risk_reward = RiskReward(
            position=self,
            symbol=self.broker_symbol,
            base_symbol=base_symbol,
            symbol_price=self.risk_reward_info["symbol_price"],
            base_symbol_price=self.risk_reward_info["base_symbol_price"],
            sl=sl,
            tgt=tgt,
            tsl=tsl,
            on_exit=on_exit if on_exit else self.exit,
            unit=unit,
        )
