"""Tests for webhook handling functionality."""

import hashlib
import hmac
import json
from unittest.mock import Mock

import pytest

from laneful.webhooks import (
    WebhookEvent,
    WebhookEventType,
    WebhookHandler,
)


class TestWebhookEvent:
    """Test cases for WebhookEvent model."""
    
    def test_webhook_event_creation(self):
        """Test creating webhook event."""
        event = WebhookEvent(
            event_type="email.delivered",
            message_id="msg_123",
            email="user@example.com",
            timestamp=1640995200,
            data={"delivery_time": "2022-01-01T00:00:00Z"}
        )
        
        assert event.event_type == "email.delivered"
        assert event.message_id == "msg_123"
        assert event.email == "user@example.com"
        assert event.timestamp == 1640995200
        assert event.data == {"delivery_time": "2022-01-01T00:00:00Z"}
    
    def test_webhook_event_from_dict(self):
        """Test creating webhook event from dictionary."""
        data = {
            "event_type": "email.opened",
            "message_id": "msg_456",
            "email": "user@example.com",
            "timestamp": 1640995260,
            "data": {"user_agent": "Mozilla/5.0"}
        }
        
        event = WebhookEvent.from_dict(data)
        assert event.event_type == "email.opened"
        assert event.message_id == "msg_456"
        assert event.email == "user@example.com"
        assert event.timestamp == 1640995260
        assert event.data == {"user_agent": "Mozilla/5.0"}
    
    def test_webhook_event_from_dict_missing_fields(self):
        """Test creating webhook event from dictionary with missing fields."""
        data = {}
        event = WebhookEvent.from_dict(data)
        
        assert event.event_type == ""
        assert event.message_id == ""
        assert event.email == ""
        assert event.timestamp == 0
        assert event.data == {}


class TestWebhookHandler:
    """Test cases for WebhookHandler."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.handler = WebhookHandler(webhook_secret="test-secret")
        self.sample_payload = {
            "event_type": "email.delivered",
            "message_id": "msg_123",
            "email": "user@example.com",
            "timestamp": 1640995200,
            "data": {}
        }
    
    def test_handler_initialization(self):
        """Test webhook handler initialization."""
        handler = WebhookHandler("secret")
        assert handler.webhook_secret == "secret"
        assert handler._handlers == {}
    
    def test_handler_initialization_no_secret(self):
        """Test webhook handler initialization without secret."""
        handler = WebhookHandler()
        assert handler.webhook_secret is None
    
    def test_register_handler_decorator(self):
        """Test registering handler using decorator."""
        handler_func = Mock()
        
        @self.handler.on("email.delivered")
        def test_handler(event):
            handler_func(event)
        
        assert "email.delivered" in self.handler._handlers
        assert self.handler._handlers["email.delivered"] == test_handler
    
    def test_register_handler_method(self):
        """Test registering handler using method."""
        handler_func = Mock()
        
        self.handler.register_handler("email.opened", handler_func)
        
        assert "email.opened" in self.handler._handlers
        assert self.handler._handlers["email.opened"] == handler_func
    
    def test_process_webhook_string_payload(self):
        """Test processing webhook with string payload."""
        handler_func = Mock()
        self.handler.register_handler("email.delivered", handler_func)
        
        payload_str = json.dumps(self.sample_payload)
        self.handler.process_webhook(payload_str)
        
        handler_func.assert_called_once()
        event = handler_func.call_args[0][0]
        assert isinstance(event, WebhookEvent)
        assert event.event_type == "email.delivered"
    
    def test_process_webhook_dict_payload(self):
        """Test processing webhook with dict payload."""
        handler_func = Mock()
        self.handler.register_handler("email.delivered", handler_func)
        
        self.handler.process_webhook(self.sample_payload)
        
        handler_func.assert_called_once()
        event = handler_func.call_args[0][0]
        assert isinstance(event, WebhookEvent)
        assert event.event_type == "email.delivered"
    
    def test_process_webhook_no_handler(self):
        """Test processing webhook with no registered handler."""
        # Should not raise an exception
        self.handler.process_webhook(self.sample_payload)
    
    def test_process_webhook_invalid_json(self):
        """Test processing webhook with invalid JSON."""
        with pytest.raises(ValueError) as exc_info:
            self.handler.process_webhook("invalid json")
        
        assert "Invalid JSON payload" in str(exc_info.value)
    
    def test_verify_signature_valid(self):
        """Test signature verification with valid signature."""
        payload = json.dumps(self.sample_payload)
        signature = hmac.new(
            "test-secret".encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        assert self.handler.verify_signature(payload, f"sha256={signature}")
        assert self.handler.verify_signature(payload, signature)  # without prefix
    
    def test_verify_signature_invalid(self):
        """Test signature verification with invalid signature."""
        payload = json.dumps(self.sample_payload)
        
        assert not self.handler.verify_signature(payload, "sha256=invalid")
        assert not self.handler.verify_signature(payload, "invalid")
    
    def test_verify_signature_no_secret(self):
        """Test signature verification without secret (should always pass)."""
        handler = WebhookHandler()  # No secret
        payload = json.dumps(self.sample_payload)
        
        assert handler.verify_signature(payload, "any-signature")
    
    def test_verify_signature_bytes_payload(self):
        """Test signature verification with bytes payload."""
        payload_bytes = json.dumps(self.sample_payload).encode()
        signature = hmac.new(
            "test-secret".encode(),
            payload_bytes,
            hashlib.sha256
        ).hexdigest()
        
        assert self.handler.verify_signature(payload_bytes, f"sha256={signature}")
    
    def test_handle_event_manual(self):
        """Test manually handling an event."""
        handler_func = Mock()
        self.handler.register_handler("email.opened", handler_func)
        
        event = WebhookEvent.from_dict({
            "event_type": "email.opened",
            "message_id": "msg_123",
            "email": "user@example.com",
            "timestamp": 1640995200,
            "data": {}
        })
        
        self.handler.handle_event("email.opened", event)
        handler_func.assert_called_once_with(event)


class TestWebhookIntegrations:
    """Test webhook framework integrations."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.handler = WebhookHandler("test-secret")
        self.sample_payload = {
            "event_type": "email.delivered",
            "message_id": "msg_123",
            "email": "user@example.com",
            "timestamp": 1640995200,
            "data": {}
        }


class TestWebhookEventType:
    """Test webhook event type enum."""
    
    def test_event_types(self):
        """Test all event types are defined."""
        assert WebhookEventType.EMAIL_SENT.value == "email.sent"
        assert WebhookEventType.EMAIL_DELIVERED.value == "email.delivered"
        assert WebhookEventType.EMAIL_OPENED.value == "email.opened"
        assert WebhookEventType.EMAIL_CLICKED.value == "email.clicked"
        assert WebhookEventType.EMAIL_BOUNCED.value == "email.bounced"
        assert WebhookEventType.EMAIL_COMPLAINED.value == "email.complained"
        assert WebhookEventType.EMAIL_UNSUBSCRIBED.value == "email.unsubscribed"
        assert WebhookEventType.EMAIL_FAILED.value == "email.failed"
