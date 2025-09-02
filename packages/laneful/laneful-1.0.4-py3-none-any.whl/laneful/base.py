"""
Base client functionality shared between sync and async clients.
"""

import json
from abc import ABC, abstractmethod
from typing import Any, Dict
from urllib.parse import urljoin

from .exceptions import LanefulAPIError, LanefulAuthError
from .models import Email, EmailList, EmailResponse, EmailResponseList


class BaseLanefulClient(ABC):
    """
    Base class for Laneful API clients.

    This abstract base class provides common functionality for both sync and async clients.
    """

    def __init__(
        self,
        base_url: str,
        auth_token: str,
        timeout: float = 30.0,
        verify_ssl: bool = True,
    ) -> None:
        """
        Initialize the base client.

        Args:
            base_url: The base URL for the Laneful API endpoint
            auth_token: Your authentication token
            timeout: Request timeout in seconds (default: 30.0)
            verify_ssl: Whether to verify SSL certificates (default: True)
        """
        self.base_url = base_url.rstrip("/")
        self.auth_token = auth_token
        self.timeout = timeout
        self.verify_ssl = verify_ssl

        self.headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
            "User-Agent": "laneful-python/1.0.0",
        }

    def _build_url(self, endpoint: str) -> str:
        """Build the full URL for an API endpoint."""
        return urljoin(self.base_url + "/v1/", endpoint.lstrip("/"))

    def _process_response_data(
        self, response_data: Dict[str, Any], status_code: int
    ) -> Dict[str, Any]:
        """
        Process response data and handle errors.

        Args:
            response_data: The parsed response data
            status_code: HTTP status code

        Returns:
            Processed response data

        Raises:
            LanefulAuthError: If authentication fails
            LanefulAPIError: If the API returns an error
        """
        # Handle authentication errors
        if status_code == 401:
            raise LanefulAuthError("Invalid authentication token")

        # Handle API errors
        if status_code >= 400:
            error_message = response_data.get("message", f"HTTP {status_code}")
            raise LanefulAPIError(
                message=error_message,
                status_code=status_code,
                response_data=response_data,
            )

        return response_data

    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON response text, handling decode errors."""
        try:
            result = json.loads(response_text)
            # Ensure we return a dict, even if the JSON is valid but not a dict
            if isinstance(result, dict):
                return result
            return {"data": result}
        except json.JSONDecodeError:
            return {"message": response_text}

    def _process_email_response(self, response_data: Dict[str, Any]) -> EmailResponse:
        """Process a single email response."""
        return EmailResponse.from_dict(response_data)

    def _process_emails_response(
        self, response_data: Dict[str, Any], email_count: int
    ) -> EmailResponseList:
        """Process bulk email response."""
        # Handle both single response and list of responses
        # Check if the API returned a list wrapped in "data" field
        if "data" in response_data and isinstance(response_data["data"], list):
            return [EmailResponse.from_dict(item) for item in response_data["data"]]
        elif "responses" in response_data:
            return [
                EmailResponse.from_dict(item) for item in response_data["responses"]
            ]
        else:
            # Fallback: create responses for each email
            return [EmailResponse.from_dict(response_data) for _ in range(email_count)]

    def _validate_emails_list(self, emails: EmailList) -> None:
        """Validate that emails list is not empty."""
        if not emails:
            raise ValueError("Email list cannot be empty")

    @abstractmethod
    def send_email(self, email: Email) -> EmailResponse:
        """Send a single email. Must be implemented by subclasses."""
        pass

    @abstractmethod
    def send_emails(self, emails: EmailList) -> EmailResponseList:
        """Send multiple emails. Must be implemented by subclasses."""
        pass

    @abstractmethod
    def get_email_status(self, message_id: str) -> Dict[str, Any]:
        """Get email status. Must be implemented by subclasses."""
        pass
