"""
Laneful API exceptions.
"""

from typing import Any, Dict, Optional


class LanefulError(Exception):
    """Base exception for all Laneful client errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class LanefulAPIError(LanefulError):
    """Exception raised for API errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data or {}


class LanefulAuthError(LanefulError):
    """Exception raised for authentication errors."""

    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(message)
