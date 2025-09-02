"""
Asynchronous Laneful API client implementation.

Requires: pip install laneful[async]
"""

import warnings

import asyncio
from typing import Any, Dict, Optional

try:
    import aiohttp
except ImportError:
    raise ImportError(
        "AsyncLanefulClient requires aiohttp. Install with: pip install laneful[async]"
    )

from .base import BaseLanefulClient
from .exceptions import LanefulError
from .models import Email, EmailList, EmailResponse, EmailResponseList


class AsyncLanefulClient(BaseLanefulClient):
    """
    Asynchronous Laneful API client for sending emails.

    Example:
        async with AsyncLanefulClient("https://api.laneful.net", "your-token") as client:
            email = Email(
                from_address=Address(email="sender@example.com", name="Your Name"),
                to=[Address(email="recipient@example.com", name="Recipient Name")],
                subject="Hello from Laneful",
                text_content="This is a test email.",
                html_content="<h1>This is a test email.</h1>",
            )

            response = await client.send_email(email)
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
        Initialize the asynchronous Laneful client.

        Args:
            base_url: The base URL for the Laneful API endpoint
            auth_token: Your authentication token
            timeout: Request timeout in seconds (default: 30.0)
            verify_ssl: Whether to verify SSL certificates (default: True)
        """
        super().__init__(base_url, auth_token, timeout, verify_ssl)

        # Create timeout object for aiohttp
        self.aiohttp_timeout = aiohttp.ClientTimeout(total=timeout)

        # Configure SSL context
        self.ssl_context = True if verify_ssl else False

        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create the aiohttp session."""
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(ssl=self.ssl_context)
            self._session = aiohttp.ClientSession(
                headers=self.headers, timeout=self.aiohttp_timeout, connector=connector
            )
        return self._session

    async def _make_request(
        self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make an async HTTP request to the API.

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
        session = await self._get_session()

        try:
            async with session.request(
                method=method,
                url=url,
                json=data,
            ) as response:
                # Get response text
                response_text = await response.text()

                # Parse JSON response
                response_data = self._parse_json_response(response_text)

                # Process response and handle errors
                return self._process_response_data(response_data, response.status)

        except asyncio.TimeoutError:
            raise LanefulError("Request timed out")
        except aiohttp.ClientConnectorError:
            raise LanefulError("Failed to connect to Laneful API")
        except aiohttp.ClientError as e:
            raise LanefulError(f"Request failed: {str(e)}")

    async def send_email(self, email: Email) -> EmailResponse:  # type: ignore[override]
        """
        Send a single email asynchronously.

        Args:
            email: Email object to send

        Returns:
            EmailResponse with send status and message ID

        Raises:
            LanefulError: If sending fails
        """
        response_data = await self._make_request(
            "POST", "/email/send", {"emails": [email.to_dict()]}
        )
        return self._process_email_response(response_data)

    async def send_emails(self, emails: EmailList) -> EmailResponseList:  # type: ignore[override]
        """
        Send multiple emails asynchronously.

        Args:
            emails: List of Email objects to send

        Returns:
            List of EmailResponse objects

        Raises:
            LanefulError: If sending fails
        """
        self._validate_emails_list(emails)

        email_data = [email.to_dict() for email in emails]
        response_data = await self._make_request(
            "POST", "/email/send", {"emails": email_data}
        )

        return self._process_emails_response(response_data, len(emails))

    async def get_email_status(self, message_id: str) -> Dict[str, Any]:  # type: ignore[override]
        """
        Get the status of a sent email asynchronously.

        Args:
            message_id: The message ID returned when sending the email

        Returns:
            Dictionary with email status information

        Raises:
            LanefulError: If the request fails
        """
        return await self._make_request("GET", f"/email/{message_id}/status")

    async def close(self) -> None:
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def __aenter__(self) -> "AsyncLanefulClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()
        return None

    def __del__(self) -> None:
        """Cleanup when object is garbage collected."""
        if self._session and not self._session.closed:
            # Don't await in __del__, just warn
            warnings.warn(
                "AsyncLanefulClient session was not closed properly. "
                "Use 'async with client:' or call 'await client.close()' explicitly.",
                ResourceWarning,
                stacklevel=2,
            )
