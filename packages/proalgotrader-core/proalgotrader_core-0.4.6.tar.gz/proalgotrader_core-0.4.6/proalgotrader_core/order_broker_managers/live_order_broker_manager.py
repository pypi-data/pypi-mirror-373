from proalgotrader_core.algo_session import AlgoSession
from proalgotrader_core.api import Api
from proalgotrader_core.notification_manager import NotificationManager
from proalgotrader_core.order_broker_managers.base_order_broker_manager import (
    BaseOrderBrokerManager,
)
from proalgotrader_core.protocols.algorithm import AlgorithmProtocol


class LiveOrderBrokerManager(BaseOrderBrokerManager):
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
