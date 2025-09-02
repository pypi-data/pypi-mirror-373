"""
Custom exceptions for the RD Station API helper module.
"""

from typing import Any, Optional


class RDStationException(Exception):
    """Base exception for all RD Station API errors."""

    def __init__(self, message: str, original_error: Optional[Exception] = None, **context: Any) -> None:
        self.message = message
        self.original_error = original_error
        self.context = context

        if original_error:
            super().__init__(f"{message} (caused by: {str(original_error)})")
        else:
            super().__init__(message)


class AuthenticationError(RDStationException):
    """Raised when authentication with RD Station API fails."""
    pass


class ValidationError(RDStationException):
    """Raised when input validation fails."""
    pass


class APIError(RDStationException):
    """Raised when RD Station API returns an error."""
    pass


class DataProcessingError(RDStationException):
    """Raised when data processing/transformation fails."""
    pass


class ConfigurationError(RDStationException):
    """Raised when configuration is invalid."""
    pass
