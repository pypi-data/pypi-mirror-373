from enum import Enum

from proalgotrader_core.protocols.enums.market_type import MarketType
from proalgotrader_core.protocols.enums.product_type import ProductType


class AccountType(Enum):
    CASH_INTRADAY = (MarketType.Cash, ProductType.MIS)
    CASH_POSITIONAL = (MarketType.Cash, ProductType.CNC)
    DERIVATIVE_INTRADAY = (MarketType.Derivative, ProductType.MIS)
    DERIVATIVE_POSITIONAL = (MarketType.Derivative, ProductType.NRML)
