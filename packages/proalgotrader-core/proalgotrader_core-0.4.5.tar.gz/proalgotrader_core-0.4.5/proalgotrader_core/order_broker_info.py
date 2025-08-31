from typing import Any, Dict


class OrderBrokerInfo:
    def __init__(self, broker_info: Dict[str, Any]) -> None:
        self.id: int = broker_info["id"]
        self.broker_uid: str = broker_info["broker_uid"]
        self.broker_title: str = broker_info["broker_title"]
        self.broker_name: str = broker_info["broker_name"]
        self.broker_config: Dict[str, Any] = broker_info["broker_config"]
