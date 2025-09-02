"""
RD Station API Helper
"""
import logging
from typing import Optional

from .client import RDStationAPI
from .utils import (
    load_from_json_file,
    save_to_json_file,
    append_to_json_file,
    get_webhook_events,
)
from .exceptions import (
    APIError,
    AuthenticationError,
    ConfigurationError,
    DataProcessingError,
    ValidationError,
)

# Main exports
__all__ = [
    "RDStationAPI",
    # Utils
    "load_from_json_file",
    "save_to_json_file",
    "append_to_json_file",
    "get_webhook_events",
    # Exceptions
    "AuthenticationError",
    "ValidationError",
    "APIError",
    "DataProcessingError",
    "ConfigurationError",
    # __init__
    "setup_logging",
]


def setup_logging(level: int = logging.INFO,
                  format_string: Optional[str] = None) -> None:
    """
    Setup logging configuration.

    Args:
        level (int): Logging level (default: INFO)
        format_string (Optional[str]): Custom format string
    """
    if format_string is None:
        format_string = '%(levelname)s - %(message)s'

    logging.basicConfig(
        level=level,
        format=format_string,
        handlers=[
            logging.StreamHandler(),
        ]
    )
