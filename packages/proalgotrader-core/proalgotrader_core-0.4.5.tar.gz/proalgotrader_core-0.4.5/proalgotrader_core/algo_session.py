import pytz

from datetime import date, datetime, time, timedelta
from typing import Literal, Dict, Any

from proalgotrader_core.project import Project


class AlgoSession:
    def __init__(self, algo_session_info: Dict[str, Any]):
        self.algo_session_info = algo_session_info["algo_session"]
        self.broker_token_info = algo_session_info["broker_token"]
        self.reverb_info = algo_session_info["reverb"]

        self.id: int = self.algo_session_info["id"]
        self.key: str = self.algo_session_info["key"]
        self.secret: str = self.algo_session_info["secret"]
        self.mode: Literal["Paper", "Live"] = self.algo_session_info["mode"]
        self.tz: str = self.algo_session_info["tz"]

        self.project_info = self.algo_session_info["project"]

        self.project: Project = Project(self.project_info)

        self.tz_info = pytz.timezone(self.tz)

        self.initial_capital: float = 10_00_000

        self.current_capital: float = 10_00_000

        self.market_start_time = time(9, 15)

        self.market_end_time = time(15, 30)

        self.market_start_datetime = datetime.now(tz=self.tz_info).replace(
            hour=self.market_start_time.hour,
            minute=self.market_start_time.minute,
            second=0,
            microsecond=0,
            tzinfo=None,
        )

        self.market_end_datetime = datetime.now(tz=self.tz_info).replace(
            hour=self.market_end_time.hour,
            minute=self.market_end_time.minute,
            second=0,
            microsecond=0,
            tzinfo=None,
        )

        self.pre_market_time = self.market_start_datetime - timedelta(minutes=15)

    @property
    def current_datetime(self) -> datetime:
        return datetime.now(tz=self.tz_info).replace(
            microsecond=0,
            tzinfo=None,
        )

    @property
    def current_timestamp(self) -> int:
        return int(self.current_datetime.timestamp())

    @property
    def current_date(self) -> date:
        return self.current_datetime.date()

    @property
    def current_time(self) -> time:
        return self.current_datetime.time()
