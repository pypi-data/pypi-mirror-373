from typing import Any, Dict, Type

from proalgotrader_core.algo_session import AlgoSession
from proalgotrader_core.api import Api
from proalgotrader_core.notification_manager import NotificationManager
from proalgotrader_core.order_broker_managers.angel_one_order_broker_manager import (
    AngelOneOrderBrokerManager,
)
from proalgotrader_core.order_broker_managers.base_order_broker_manager import (
    BaseOrderBrokerManager,
)
from proalgotrader_core.order_broker_managers.fyers_order_broker_manager import (
    FyersOrderBrokerManager,
)
from proalgotrader_core.order_broker_managers.live_order_broker_manager import (
    LiveOrderBrokerManager,
)
from proalgotrader_core.order_broker_managers.paper_order_broker_manager import (
    PaperOrderBrokerManager,
)
from proalgotrader_core.order_broker_managers.shoonya_order_broker_manager import (
    ShoonyaOrderBrokerManager,
)

modes: Dict[str, Any] = {
    "paper": PaperOrderBrokerManager,
    "live": LiveOrderBrokerManager,
}

brokers: Dict[str, Any] = {
    "paper": PaperOrderBrokerManager,
    "fyers": FyersOrderBrokerManager,
    "angel-one": AngelOneOrderBrokerManager,
    "shoonya": ShoonyaOrderBrokerManager,
}


class OrderBrokerManager:
    @staticmethod
    def get_instance(
        api: Api,
        algo_session: AlgoSession,
        notification_manager: NotificationManager,
        algorithm,
    ) -> BaseOrderBrokerManager:
        broker_mode = algo_session.mode.lower()

        mode_class: Type[BaseOrderBrokerManager] = modes[broker_mode]

        broker_title = algo_session.project.order_broker_info.broker_title.lower()

        broker_class: Type[BaseOrderBrokerManager] = brokers[broker_title]

        mode_class.__bases__ = (broker_class,)

        broker: BaseOrderBrokerManager = mode_class(
            api=api,
            algo_session=algo_session,
            notification_manager=notification_manager,
            algorithm=algorithm,
        )

        return broker
