from abc import ABC, abstractmethod
from typing import Optional


class BaseTokenManager(ABC):
    """Base class for all token managers with standardized logging support."""

    def __init__(self):
        self.log_path: Optional[str] = None

    @property
    def broker_log_path(self) -> Optional[str]:
        """Get the broker-specific log path."""
        return self.log_path

    @abstractmethod
    async def initialize(self, token: str, feed_token: Optional[str]) -> None:
        """Initialize the token manager with authentication tokens."""
        pass
