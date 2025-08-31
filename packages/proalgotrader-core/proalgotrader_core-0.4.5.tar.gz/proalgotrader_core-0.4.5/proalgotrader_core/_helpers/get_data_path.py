import os

from datetime import datetime
from pathlib import Path


async def get_data_path(current_datetime: datetime) -> Path:
    home_directory = os.path.expanduser("~")

    path = Path(f"{home_directory}/proalgotrader/trading_info/{current_datetime.year}")

    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    return path
