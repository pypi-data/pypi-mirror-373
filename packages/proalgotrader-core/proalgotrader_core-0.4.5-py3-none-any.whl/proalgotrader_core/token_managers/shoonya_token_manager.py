import os
import logging
from NorenRestApiPy.NorenApi import NorenApi

from logzero import logger

from proalgotrader_core._helpers.logging_config import (
    setup_broker_logging,
    BROKER_NAMES,
)
from proalgotrader_core.token_managers.base_token_manager import BaseTokenManager


class ShoonyaTokenManager(BaseTokenManager):
    def __init__(
        self,
        user_id: str,
        password: str,
        totp_key: str,
        vendor_code: str,
        api_secret: str,
        imei: str,
    ) -> None:
        super().__init__()

        self.token: str | None = None

        self.user_id = user_id
        self.password = password
        self.totp_key = totp_key
        self.vendor_code = vendor_code
        self.api_secret = api_secret
        self.imei = imei

        # Set up standardized logging path for Shoonya
        self.log_path = setup_broker_logging(BROKER_NAMES["shoonya"])

        # Create the broker-specific logs directory structure
        # This ensures Shoonya logs go to logs/shoonya/logs/ for consistency
        broker_logs_dir = os.path.join(self.log_path, "logs")
        os.makedirs(broker_logs_dir, exist_ok=True)

        # Configure NorenRestApiPy logging to use our standardized path
        self._setup_noren_logging()

        self.api = NorenApi(
            host="https://api.shoonya.com/NorenWClientTP/",
            websocket="wss://api.shoonya.com/NorenWSTP/",
        )

    def _setup_noren_logging(self) -> None:
        """Configure NorenRestApiPy logging to use our standardized path."""
        try:
            # Ensure log_path is set
            if self.log_path is None:
                logger.warning("Log path not set, using default")
                return

            # Create log file path in the broker-specific logs directory
            log_file = os.path.join(self.log_path, "logs", "shoonya.log")

            # Ensure log directory exists
            os.makedirs(os.path.dirname(log_file), exist_ok=True)

            # Configure file handler for NorenRestApiPy logging
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.INFO)

            # Create formatter
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            file_handler.setFormatter(formatter)

            # Get the NorenRestApiPy logger and add our file handler
            noren_logger = logging.getLogger("NorenRestApiPy")
            noren_logger.addHandler(file_handler)
            noren_logger.setLevel(logging.INFO)

            logger.info(f"Shoonya logging configured to: {log_file}")
        except Exception as e:
            logger.debug(f"Failed to configure NorenRestApiPy logging: {e}")

    async def initialize(self, token: str, feed_token: str | None) -> None:
        self.token = token
        self.feed_token = feed_token

        self.api.set_session(
            userid=self.user_id,
            password=self.password,
            usertoken=self.token,
        )
