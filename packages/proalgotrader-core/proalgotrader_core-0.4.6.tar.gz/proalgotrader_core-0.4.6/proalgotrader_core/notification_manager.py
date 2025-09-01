import pusher

from typing import Dict, Any

from proalgotrader_core.algo_session import AlgoSession


class NotificationManager:
    def __init__(self, algo_session: AlgoSession) -> None:
        self.algo_session = algo_session

    async def connect(self):
        self.algo_session_key = self.algo_session.key
        self.reverb_info = self.algo_session.reverb_info

        self.pusher_client = pusher.Pusher(
            app_id=self.reverb_info["app_id"],
            key=self.reverb_info["app_key"],
            secret=self.reverb_info["app_secret"],
            host=self.reverb_info["host"],
            port=self.reverb_info["port"],
            ssl=self.reverb_info["secure"],
        )

    async def send_message(self, data: Dict[str, Any]) -> None:
        channel_name = f"algo-session-{self.algo_session_key}"

        self.pusher_client.trigger(
            channels=[channel_name], event_name="ltp.update", data=data
        )
