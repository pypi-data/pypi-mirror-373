"""
Webhook handling for Laneful API events.
"""

import hashlib
import hmac
import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, Optional, Union


class WebhookEventType(Enum):
    """Webhook event types."""

    EMAIL_SENT = "email.sent"
    EMAIL_DELIVERED = "email.delivered"
    EMAIL_OPENED = "email.opened"
    EMAIL_CLICKED = "email.clicked"
    EMAIL_BOUNCED = "email.bounced"
    EMAIL_COMPLAINED = "email.complained"
    EMAIL_UNSUBSCRIBED = "email.unsubscribed"
    EMAIL_FAILED = "email.failed"


@dataclass
class WebhookEvent:
    """Webhook event data."""

    event_type: str
    message_id: str
    email: str
    timestamp: int
    data: Dict[str, Any]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WebhookEvent":
        """Create WebhookEvent from webhook payload."""
        return cls(
            event_type=data.get("event_type", ""),
            message_id=data.get("message_id", ""),
            email=data.get("email", ""),
            timestamp=data.get("timestamp", 0),
            data=data.get("data", {}),
        )


class WebhookHandler:
    """
    Handler for processing Laneful webhook events.

    Example:
        handler = WebhookHandler("your-webhook-secret")

        @handler.on("email.delivered")
        def handle_delivered(event: WebhookEvent):
            print(f"Email {event.message_id} was delivered to {event.email}")

        # In your web framework handler:
        if handler.verify_signature(request_body, signature_header):
            handler.process_webhook(request_body)
    """

    def __init__(self, webhook_secret: Optional[str] = None) -> None:
        """
        Initialize webhook handler.

        Args:
            webhook_secret: Secret key for verifying webhook signatures
        """
        self.webhook_secret = webhook_secret
        self._handlers: Dict[str, Callable[[WebhookEvent], None]] = {}

    def verify_signature(self, payload: Union[str, bytes], signature: str) -> bool:
        """
        Verify webhook signature to ensure authenticity.

        Args:
            payload: The raw webhook payload
            signature: The signature header from the webhook request

        Returns:
            True if signature is valid, False otherwise
        """
        if not self.webhook_secret:
            return True  # Skip verification if no secret is configured

        if isinstance(payload, str):
            payload = payload.encode("utf-8")

        # Extract signature from header (format: "sha256=signature")
        if signature.startswith("sha256="):
            signature = signature[7:]

        # Calculate expected signature
        expected_signature = hmac.new(
            self.webhook_secret.encode("utf-8"), payload, hashlib.sha256
        ).hexdigest()

        # Use constant-time comparison to prevent timing attacks
        return hmac.compare_digest(expected_signature, signature)

    def on(
        self, event_type: str
    ) -> Callable[[Callable[[WebhookEvent], None]], Callable[[WebhookEvent], None]]:
        """
        Decorator to register event handlers.

        Args:
            event_type: The event type to handle (e.g., "email.delivered")

        Returns:
            Decorator function
        """

        def decorator(
            func: Callable[[WebhookEvent], None],
        ) -> Callable[[WebhookEvent], None]:
            self._handlers[event_type] = func
            return func

        return decorator

    def register_handler(
        self, event_type: str, handler: Callable[[WebhookEvent], None]
    ) -> None:
        """
        Register an event handler function.

        Args:
            event_type: The event type to handle
            handler: The handler function
        """
        self._handlers[event_type] = handler

    def process_webhook(self, payload: Union[str, Dict[str, Any]]) -> None:
        """
        Process a webhook payload and call appropriate handlers.

        Args:
            payload: The webhook payload (JSON string or dict)

        Raises:
            ValueError: If payload is invalid
            KeyError: If required fields are missing
        """
        if isinstance(payload, str):
            try:
                data = json.loads(payload)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON payload: {e}")
        else:
            data = payload

        event = WebhookEvent.from_dict(data)

        # Call the appropriate handler if one is registered
        if event.event_type in self._handlers:
            self._handlers[event.event_type](event)

    def handle_event(self, event_type: str, event: WebhookEvent) -> None:
        """
        Manually trigger an event handler.

        Args:
            event_type: The event type
            event: The webhook event data
        """
        if event_type in self._handlers:
            self._handlers[event_type](event)
