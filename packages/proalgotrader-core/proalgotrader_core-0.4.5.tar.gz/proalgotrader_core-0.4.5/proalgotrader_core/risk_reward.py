from logzero import logger
from typing import Callable, List, Any, Literal

from proalgotrader_core.protocols.enums.position_type import PositionType
from proalgotrader_core.protocols.enums.segment_type import SegmentType
from proalgotrader_core.broker_symbol import BrokerSymbol

from proalgotrader_core.protocols.position import PositionProtocol


class RiskReward:
    def __init__(
        self,
        *,
        position: PositionProtocol,
        symbol: BrokerSymbol,
        base_symbol: BrokerSymbol,
        symbol_price: float,
        base_symbol_price: float,
        sl: float,
        tgt: float | None = None,
        tsl: float | None = None,
        on_exit: Callable[..., Any],
        unit: Literal["points", "percentage"],
    ) -> None:
        self.position = position
        self.symbol = symbol
        self.base_symbol = base_symbol
        self.symbol_price = symbol_price
        self.base_symbol_price = base_symbol_price
        self.sl = sl
        self.tgt = tgt
        self.tsl = tsl
        self.on_exit = on_exit
        self.unit = unit

        if not self.position:
            logger.error("Position is required")

        if not self.sl:
            logger.error("Stoploss is required")

        self.direction: str = self.__get_direction()
        self.stoploss: float = self.__get_stoploss()
        self.target: float = self.__get_target()
        self.trailed_stoplosses: List[float] = self.__get_trailed_stoplosses()

    @property
    def price(self) -> float:
        return self.base_symbol_price if self.unit == "points" else self.symbol_price

    @property
    def ltp(self):
        return self.base_symbol.ltp if self.unit == "points" else self.symbol.ltp

    @property
    def trailed_stoploss(self) -> float:
        return self.trailed_stoplosses[-1]

    def __get_direction(self) -> str:
        segment_type = self.position.broker_symbol.segment_type
        position_type = self.position.position_type
        option_type = self.position.broker_symbol.option_type

        if segment_type == SegmentType.Equity.value:
            return self.__get_equity_direction(position_type)

        elif segment_type == SegmentType.Future.value:
            return self.__get_future_direction(position_type)

        elif segment_type == SegmentType.Option.value:
            return self.__get_option_direction(position_type, option_type)

        else:
            raise Exception("Invalid direction")

    def __get_equity_direction(self, position_type: str) -> str:
        if position_type == PositionType.BUY.value:
            return "long"
        elif position_type == PositionType.SELL.value:
            return "short"
        else:
            raise Exception("Invalid equity direction")

    def __get_future_direction(self, position_type: str) -> str:
        if position_type == PositionType.BUY.value:
            return "long"
        elif position_type == PositionType.SELL.value:
            return "short"
        else:
            raise Exception("Invalid future direction")

    def __get_option_direction(self, position_type: str, option_type: str) -> str:
        option_direction = {
            (SegmentType.Equity.value, PositionType.BUY.value, "CE"): "long",
            (SegmentType.Future.value, PositionType.BUY.value, "CE"): "long",
            (SegmentType.Option.value, PositionType.BUY.value, "CE"): "long",
            (SegmentType.Equity.value, PositionType.BUY.value, "PE"): "short",
            (SegmentType.Future.value, PositionType.BUY.value, "PE"): "short",
            (SegmentType.Option.value, PositionType.BUY.value, "PE"): "long",
            (SegmentType.Equity.value, PositionType.SELL.value, "CE"): "short",
            (SegmentType.Future.value, PositionType.SELL.value, "CE"): "short",
            (SegmentType.Option.value, PositionType.SELL.value, "CE"): "short",
            (SegmentType.Equity.value, PositionType.SELL.value, "PE"): "long",
            (SegmentType.Future.value, PositionType.SELL.value, "PE"): "long",
            (SegmentType.Option.value, PositionType.SELL.value, "PE"): "short",
        }

        direction = option_direction.get(
            (self.symbol.segment_type, position_type, option_type), None
        )

        if direction:
            return direction
        else:
            raise Exception("Invalid option direction")

    def __get_stoploss(self) -> float:
        if self.direction == "long":
            return round(self.price - self.sl, 2)

        elif self.direction == "short":
            return round(self.price + self.sl, 2)

        else:
            raise Exception("error")

    def __get_target(self) -> float | None:
        if not self.tgt:
            return None

        if self.direction == "long":
            return round(self.price + self.tgt, 2)

        elif self.direction == "short":
            return round(self.price - self.tgt, 2)

        else:
            raise Exception("error")

    def __get_trailed_stoplosses(self) -> List[float]:
        """Initialize trailed stoplosses based on current market position"""
        current_stoploss = self.stoploss
        trailed_stoploss_list: List[float] = [self.stoploss]

        if self.tsl:
            if self.direction == "long":
                # Only trail if market has moved in favor (LTP > entry price)
                # and we haven't hit stoploss yet
                if self.ltp > self.price and self.ltp > current_stoploss:
                    while (current_stoploss + (self.sl + self.tsl)) < self.ltp:
                        current_stoploss = round(current_stoploss + self.tsl, 2)
                        trailed_stoploss_list.append(current_stoploss)

            elif self.direction == "short":
                # Only trail if market has moved in favor (LTP < entry price)
                # and we haven't hit stoploss yet
                if self.ltp < self.price and self.ltp < current_stoploss:
                    while (current_stoploss - (self.sl + self.tsl)) > self.ltp:
                        current_stoploss = round(current_stoploss - self.tsl, 2)
                        trailed_stoploss_list.append(current_stoploss)

        return trailed_stoploss_list

    async def next(self) -> None:
        # print("direction", self.direction)
        # print("stoploss", self.stoploss)
        # print("target", self.target)
        # print("trailed_stoploss", self.trailed_stoploss)
        # print("trailed_stoplosses", self.trailed_stoplosses)
        # print("unit", self.unit)
        # print("price", self.price)
        # print("symbol_price", self.symbol_price)
        # print("base_symbol_price", self.base_symbol_price)
        # print("ltp", self.ltp)
        # print("sl", self.sl)
        # print("tgt", self.tgt)
        # print("tsl", self.tsl)
        # print("\n")

        if self.direction == "long":
            await self.__monitor_long_position()

        if self.direction == "short":
            await self.__monitor_short_position()

    async def __monitor_long_position(self) -> None:
        if self.sl and self.trailed_stoploss:
            if self.ltp <= self.trailed_stoploss:
                await self.on_exit()

        if self.tgt and self.target:
            if self.ltp >= self.target:
                await self.on_exit()

        if self.tsl and self.trailed_stoploss:
            current_move_ctc = (self.trailed_stoploss) >= self.price
            next_move_ctc = (self.trailed_stoploss + self.tsl) >= self.price

            await self.__trail_stoploss("long", current_move_ctc, next_move_ctc)

    async def __monitor_short_position(self) -> None:
        if self.sl and self.trailed_stoploss:
            if self.ltp >= self.trailed_stoploss:
                await self.on_exit()

        if self.tgt and self.target:
            if self.ltp <= self.target:
                await self.on_exit()

        if self.tsl and self.trailed_stoploss:
            current_move_ctc = (self.trailed_stoploss) <= self.price
            next_move_ctc = (self.trailed_stoploss - self.tsl) <= self.price

            await self.__trail_stoploss("short", current_move_ctc, next_move_ctc)

    async def __trail_stoploss(
        self, direction: str, current_move_ctc: bool, next_move_ctc: bool
    ) -> None:
        if next_move_ctc:
            await self.__trail_stoploss_ctc(direction, current_move_ctc, next_move_ctc)
        else:
            await self.__trail_stoploss_normal(
                direction, current_move_ctc, next_move_ctc
            )

    async def __trail_stoploss_ctc(
        self, direction: str, current_move_ctc: bool, next_move_ctc: bool
    ) -> None:
        should_move = not current_move_ctc and next_move_ctc

        trail_by = self.sl + self.tsl if should_move else self.tsl
        move_by = self.sl if should_move else self.tsl

        if direction == "long":
            if self.ltp >= (self.trailed_stoploss + trail_by):
                trailed_stoploss = self.trailed_stoploss + move_by
                self.trailed_stoplosses.append(trailed_stoploss)

        if direction == "short":
            if self.ltp <= (self.trailed_stoploss - trail_by):
                trailed_stoploss = self.trailed_stoploss - move_by
                self.trailed_stoplosses.append(trailed_stoploss)

    async def __trail_stoploss_normal(
        self, direction: str, current_move_ctc: bool, next_move_ctc: bool
    ) -> None:
        if direction == "long":
            if self.ltp >= (self.trailed_stoploss + (self.sl + self.tsl)):
                trailed_stoploss = self.trailed_stoploss + self.tsl
                self.trailed_stoplosses.append(trailed_stoploss)

        if direction == "short":
            if self.ltp <= (self.trailed_stoploss - (self.sl + self.tsl)):
                trailed_stoploss = self.trailed_stoploss - self.tsl
                self.trailed_stoplosses.append(trailed_stoploss)
