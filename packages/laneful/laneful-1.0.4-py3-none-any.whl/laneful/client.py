"""
Synchronous Laneful API client implementation.

Requires: pip install laneful (included by default)
"""

from typing import Any, Dict, Optional

try:
    import requests
except ImportError:
    raise ImportError(
        "LanefulClient requires requests. "
        "Install with: pip install laneful[sync] or pip install laneful"
    )

from .base import BaseLanefulClient
from .exceptions import LanefulError
from .models import Email, EmailList, EmailResponse, EmailResponseList


class LanefulClient(BaseLanefulClient):
    """
    Laneful API client for sending emails.

    Example:
        client = LanefulClient("https://custom-endpoint.send.laneful.net", "your-auth-token")

        email = Email(
            from_address=Address(email="sender@example.com", name="Your Name"),
            to=[Address(email="recipient@example.com", name="Recipient Name")],
            subject="Hello from Laneful",
            text_content="This is a test email.",
            html_content="<h1>This is a test email.</h1>",
        )

        response = client.send_email(email)
        print(f"Email sent successfully: {response.status}")
    """

    def __init__(
        self,
        base_url: str,
        auth_token: str,
        timeout: float = 30.0,
        verify_ssl: bool = True,
    ) -> None:
        """
        Initialize the synchronous Laneful client.

        Args:
            base_url: The base URL for the Laneful API endpoint
            auth_token: Your authentication token
            timeout: Request timeout in seconds (default: 30.0)
            verify_ssl: Whether to verify SSL certificates (default: True)
        """
        super().__init__(base_url, auth_token, timeout, verify_ssl)

        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _make_request(
        self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: Request data to send as JSON

        Returns:
            Response data as dictionary

        Raises:
            LanefulAuthError: If authentication fails
            LanefulAPIError: If the API returns an error
            LanefulError: For other client errors
        """
        url = self._build_url(endpoint)

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                timeout=self.timeout,
                verify=self.verify_ssl,
                headers=self.headers,
            )

            # Parse JSON response
            response_data = self._parse_json_response(response.text)

            # Process response and handle errors
            return self._process_response_data(response_data, response.status_code)

        except requests.exceptions.Timeout:
            raise LanefulError("Request timed out")
        except requests.exceptions.ConnectionError:
            raise LanefulError("Failed to connect to Laneful API")
        except requests.exceptions.RequestException as e:
            raise LanefulError(f"Request failed: {str(e)}")

    def send_email(self, email: Email) -> EmailResponse:
        """
        Send a single email.

        Args:
            email: Email object to send

        Returns:
            EmailResponse with send status and message ID

        Raises:
            LanefulError: If sending fails
        """
        response_data = self._make_request(
            "POST", "/email/send", {"emails": [email.to_dict()]}
        )
        return self._process_email_response(response_data)

    def send_emails(self, emails: EmailList) -> EmailResponseList:
        """
        Send multiple emails.

        Args:
            emails: List of Email objects to send

        Returns:
            List of EmailResponse objects

        Raises:
            LanefulError: If sending fails
        """
        self._validate_emails_list(emails)

        email_data = [email.to_dict() for email in emails]
        response_data = self._make_request(
            "POST", "/email/send", {"emails": email_data}
        )

        return self._process_emails_response(response_data, len(emails))

    def get_email_status(self, message_id: str) -> Dict[str, Any]:
        """
        Get the status of a sent email.

        Args:
            message_id: The message ID returned when sending the email

        Returns:
            Dictionary with email status information

        Raises:
            LanefulError: If the request fails
        """
        return self._make_request("GET", f"/email/{message_id}/status")

    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()

    def __enter__(self) -> "LanefulClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()
