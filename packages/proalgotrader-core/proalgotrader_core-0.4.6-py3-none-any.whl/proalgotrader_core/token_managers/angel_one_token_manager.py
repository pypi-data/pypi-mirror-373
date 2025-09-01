import os
from SmartApi import SmartConnect
from SmartApi.smartWebSocketV2 import SmartWebSocketV2

from logzero import logger

from proalgotrader_core._helpers.logging_config import (
    setup_broker_logging,
    BROKER_NAMES,
)
from proalgotrader_core.token_managers.base_token_manager import BaseTokenManager


class AngelOneTokenManager(BaseTokenManager):
    def __init__(
        self,
        username: str,
        totp_key: str,
        mpin: str,
        api_key: str,
        api_secret: str,
        redirect_url: str,
    ) -> None:
        super().__init__()

        self.username = username
        self.totp_key = totp_key
        self.mpin = mpin
        self.api_key = api_key
        self.api_secret = api_secret
        self.redirect_url = redirect_url

        self.token: str | None = None
        self.session = None
        self.http_client = None
        self.ws_client = None

        # Set up standardized logging path for Angel One
        self.log_path = setup_broker_logging(BROKER_NAMES["angel_one"])

        # Configure SmartApi logging to use our standardized path
        self._setup_smartapi_logging()

    def _setup_smartapi_logging(self) -> None:
        """Configure SmartApi logging to use our standardized path."""
        try:
            # Ensure log_path is set
            if self.log_path is None:
                logger.warning("Log path not set, using default")
                return

            # Create the broker-specific logs directory structure
            # We want logs/angel_one/{date}/ not logs/angel_one/logs/{date}/
            broker_logs_dir = self.log_path  # This is logs/angel_one/
            os.makedirs(broker_logs_dir, exist_ok=True)

            # Store the original working directory
            self.original_cwd = os.getcwd()

            # Change to the broker-specific directory (logs/angel_one/)
            # This makes SmartApi create logs in logs/angel_one/logs/{date}/
            os.chdir(broker_logs_dir)

            logger.info(f"SmartApi logging redirected to: {broker_logs_dir}")
            logger.info("SmartApi will create logs in logs/angel_one/logs/{date}/")
        except Exception as e:
            logger.debug(f"Failed to configure SmartApi logging: {e}")

    def _move_logs_to_desired_structure(self) -> None:
        """Move logs from logs/angel_one/logs/{date}/ to logs/angel_one/{date}/"""
        try:
            if self.log_path is None:
                return

            # Check if logs were created in logs/angel_one/logs/{date}/
            logs_subdir = os.path.join(self.log_path, "logs")
            if os.path.exists(logs_subdir):
                # Find date directories
                for item in os.listdir(logs_subdir):
                    date_path = os.path.join(logs_subdir, item)
                    if (
                        os.path.isdir(date_path)
                        and len(item) == 10
                        and item.count("-") == 2
                    ):  # Date format YYYY-MM-DD
                        # Move the entire date directory to logs/angel_one/{date}/
                        target_path = os.path.join(self.log_path, item)
                        if not os.path.exists(target_path):
                            os.rename(date_path, target_path)
                            logger.info(f"Moved logs from {date_path} to {target_path}")
                        else:
                            # If target exists, merge contents
                            import shutil

                            for log_file in os.listdir(date_path):
                                src_file = os.path.join(date_path, log_file)
                                dst_file = os.path.join(target_path, log_file)
                                if os.path.isfile(src_file):
                                    shutil.move(src_file, dst_file)
                            # Remove empty date directory
                            os.rmdir(date_path)
                            logger.info(
                                f"Merged logs from {date_path} to {target_path}"
                            )

                # Remove empty logs subdirectory if it's empty
                if os.path.exists(logs_subdir) and not os.listdir(logs_subdir):
                    os.rmdir(logs_subdir)

        except Exception as e:
            logger.debug(f"Failed to move logs to desired structure: {e}")

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

        self.http_client = await self.get_http_client()
        self.ws_client = await self.get_ws_client()

        # Move logs to desired structure after SmartApi initialization
        # This ensures logs go from logs/angel_one/logs/{date}/ to logs/angel_one/{date}/
        self._move_logs_to_desired_structure()

    async def get_http_client(self) -> SmartConnect:
        try:
            http_client = SmartConnect(
                api_key=self.api_key,
                access_token=self.token,
                timeout=5,
            )

            return http_client
        except Exception as e:
            logger.debug(e)
            raise Exception(e)

    async def get_ws_client(self) -> SmartWebSocketV2:
        try:
            ws_client = SmartWebSocketV2(
                self.token,
                self.api_key,
                self.username,
                self.feed_token,
            )

            return ws_client
        except Exception as e:
            logger.debug(e)
            raise Exception(e)

    def __del__(self):
        """Cleanup: restore working directory when token manager is destroyed."""
        self._restore_working_directory()
