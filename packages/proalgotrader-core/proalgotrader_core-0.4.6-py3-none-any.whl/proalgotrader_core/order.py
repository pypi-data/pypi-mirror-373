from datetime import datetime
from typing import Literal, Any, Dict


from proalgotrader_core.broker_symbol import BrokerSymbol


class Order:
    def __init__(
        self,
        order_info: Dict[str, Any],
        broker_symbol: BrokerSymbol,
    ):
        self.id: int = order_info["id"]
        self.order_id: str = order_info["order_id"]
        self.position_type: str = order_info["position_type"]
        self.order_type: str = order_info["order_type"]
        self.product_type: str = order_info["product_type"]
        self.quantities: int = order_info["quantities"]
        self.disclosed_quantities: int = order_info["disclosed_quantities"]
        self.price: float = order_info["price"]
        self.status: Literal["pending", "completed", "rejected", "failed"] = order_info[
            "status"
        ]
        self.created_at: datetime = order_info["created_at"]
        self.updated_at: datetime = order_info["updated_at"]

        self.broker_symbol: BrokerSymbol = broker_symbol

    async def initialize(self) -> None:
        pass

    @property
    def is_completed(self) -> bool:
        return self.status == "completed"

    @property
    def is_pending(self) -> bool:
        return self.status == "pending"
