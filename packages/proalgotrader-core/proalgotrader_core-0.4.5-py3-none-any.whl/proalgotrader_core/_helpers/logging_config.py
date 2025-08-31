import os
from pathlib import Path


def get_broker_log_path(broker_name: str) -> str:
    """
    Get the standardized log path for a specific broker.

    Args:
        broker_name: Name of the broker (e.g., 'fyers', 'angel_one', 'shoonya')

    Returns:
        Path to the broker's log directory
    """
    # Get the project root directory (assuming this is called from proalgotrader_core)
    project_root = Path(__file__).parent.parent.parent

    # Create logs directory if it doesn't exist
    logs_dir = project_root / "logs"
    logs_dir.mkdir(exist_ok=True)

    # Create broker-specific log directory
    broker_log_dir = logs_dir / broker_name
    broker_log_dir.mkdir(exist_ok=True)

    return str(broker_log_dir)


def setup_broker_logging(broker_name: str) -> str:
    """
    Set up logging for a specific broker and return the log path.

    Args:
        broker_name: Name of the broker (e.g., 'fyers', 'angel_one', 'shoonya')

    Returns:
        Path to the broker's log directory
    """
    log_path = get_broker_log_path(broker_name)

    # Ensure the log directory exists
    os.makedirs(log_path, exist_ok=True)

    return log_path


# Predefined broker names for consistency
BROKER_NAMES = {"fyers": "fyers", "angel_one": "angel_one", "shoonya": "shoonya"}
