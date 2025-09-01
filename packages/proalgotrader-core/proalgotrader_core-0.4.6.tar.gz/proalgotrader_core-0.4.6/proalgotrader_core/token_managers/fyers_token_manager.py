import os
import time
from fyers_apiv3.FyersWebsocket.data_ws import FyersDataSocket
from fyers_apiv3.fyersModel import FyersModel

from logzero import logger

from proalgotrader_core._helpers.logging_config import (
    setup_broker_logging,
    BROKER_NAMES,
)
from proalgotrader_core.token_managers.base_token_manager import BaseTokenManager


class FyersTokenManager(BaseTokenManager):
    def __init__(
        self,
        username: str,
        totp_key: str,
        pin: str,
        api_key: str,
        secret_key: str,
        redirect_url: str,
    ) -> None:
        super().__init__()

        self.username = username
        self.totp_key = totp_key
        self.pin = pin
        self.api_key = api_key
        self.secret_key = secret_key
        self.redirect_url = redirect_url

        self.ws_client: FyersDataSocket | None = None
        self.http_client: FyersModel | None = None
        self.token: str | None = None

        # Set up standardized logging path for Fyers
        self.log_path = setup_broker_logging(BROKER_NAMES["fyers"])

        # Create the broker-specific logs directory structure
        # This ensures Fyers logs go to logs/fyers/logs/ for consistency
        broker_logs_dir = os.path.join(self.log_path, "logs")
        os.makedirs(broker_logs_dir, exist_ok=True)

        # Configure Fyers logging to use our standardized path with date-based structure
        self._setup_fyers_logging()

    def _setup_fyers_logging(self) -> None:
        """Configure Fyers logging to use our standardized path with date-based structure."""
        try:
            # Ensure log_path is set
            if self.log_path is None:
                logger.warning("Log path not set, using default")
                return

            # Create the broker-specific logs directory structure
            # Fyers will create logs in logs/fyers/logs/ instead of logs/fyers/
            broker_logs_dir = os.path.join(self.log_path, "logs")
            os.makedirs(broker_logs_dir, exist_ok=True)

            # Create date-based subdirectory for today
            today = time.strftime("%Y-%m-%d", time.localtime())
            date_logs_dir = os.path.join(broker_logs_dir, today)
            os.makedirs(date_logs_dir, exist_ok=True)

            # Store the original working directory
            self.original_cwd = os.getcwd()

            # Change to the date-specific logs directory
            # This makes Fyers create logs in logs/fyers/logs/{date}/ instead of logs/fyers/logs/
            os.chdir(date_logs_dir)

            logger.info(f"Fyers logging redirected to: {date_logs_dir}")
        except Exception as e:
            logger.debug(f"Failed to configure Fyers logging: {e}")

    def _restore_working_directory(self) -> None:
        """Restore the original working directory."""
        try:
            if hasattr(self, "original_cwd"):
                os.chdir(self.original_cwd)
                logger.debug("Working directory restored")
        except Exception as e:
            logger.debug(f"Failed to restore working directory: {e}")

    async def initialize(self, token: str, feed_token: str | None) -> None:
        self.token = token
        self.feed_token = feed_token

        self.http_client = FyersModel(
            client_id=self.api_key,
            token=self.token,
            log_path="",  # Use empty string since we're changing working directory
        )

        self.ws_client = FyersDataSocket(
            access_token=f"{self.api_key}:{self.token}",
            litemode=False,
            reconnect=True,
            log_path="",  # Use empty string since we're changing working directory
        )

    def __del__(self):
        """Cleanup: restore working directory when token manager is destroyed."""
        self._restore_working_directory()
