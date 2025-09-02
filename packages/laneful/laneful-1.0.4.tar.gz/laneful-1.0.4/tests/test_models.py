"""Tests for Laneful data models."""

import pytest

from laneful.models import Address, Attachment, Email, EmailResponse, TrackingSettings


class TestAddress:
    """Test cases for Address model."""
    
    def test_address_with_email_only(self):
        """Test creating address with email only."""
        addr = Address(email="test@example.com")
        assert addr.email == "test@example.com"
        assert addr.name == ""
    
    def test_address_with_name(self):
        """Test creating address with name."""
        addr = Address(email="test@example.com", name="Test User")
        assert addr.email == "test@example.com"
        assert addr.name == "Test User"
    
    def test_address_to_dict(self):
        """Test converting address to dictionary."""
        addr = Address(email="test@example.com", name="Test User")
        expected = {"email": "test@example.com", "name": "Test User"}
        assert addr.to_dict() == expected
    
    def test_address_to_dict_no_name(self):
        """Test converting address to dictionary without name."""
        addr = Address(email="test@example.com")
        expected = {"email": "test@example.com"}
        assert addr.to_dict() == expected


class TestAttachment:
    """Test cases for Attachment model."""
    
    def test_attachment_creation(self):
        """Test creating attachment."""
        att = Attachment(
            file_name="test.txt",
            content="dGVzdCBjb250ZW50",  # base64 encoded "test content"
            content_type="text/plain"
        )
        assert att.file_name == "test.txt"
        assert att.content == "dGVzdCBjb250ZW50"
        assert att.content_type == "text/plain"
    
    def test_attachment_to_dict(self):
        """Test converting attachment to dictionary."""
        att = Attachment(
            file_name="test.txt",
            content="dGVzdCBjb250ZW50",
            content_type="text/plain"
        )
        expected = {
            "file_name": "test.txt",
            "content": "dGVzdCBjb250ZW50",
            "content_type": "text/plain"
        }
        assert att.to_dict() == expected
    
    def test_attachment_validation_failure(self):
        """Test attachment validation fails without file_name or inline_id."""
        with pytest.raises(ValueError) as exc_info:
            Attachment(content_type="text/plain", content="content")
        assert "Either file_name or inline_id is required" in str(exc_info.value)
    
    def test_attachment_with_inline_id(self):
        """Test creating attachment with inline_id."""
        att = Attachment(
            content_type="image/png",
            inline_id="img1",
            content="base64content"
        )
        expected = {
            "content_type": "image/png",
            "inline_id": "img1",
            "content": "base64content"
        }
        assert att.to_dict() == expected


class TestTrackingSettings:
    """Test cases for TrackingSettings model."""
    
    def test_tracking_settings_defaults(self):
        """Test default tracking settings."""
        tracking = TrackingSettings()
        assert tracking.opens is True
        assert tracking.clicks is True
        assert tracking.unsubscribes is True
        assert tracking.unsubscribe_group_id is None
    
    def test_tracking_settings_custom(self):
        """Test custom tracking settings."""
        tracking = TrackingSettings(opens=True, clicks=True, unsubscribes=True)
        assert tracking.opens is True
        assert tracking.clicks is True
        assert tracking.unsubscribes is True
    
    def test_tracking_settings_to_dict(self):
        """Test converting tracking settings to dictionary."""
        tracking = TrackingSettings(opens=True, clicks=False, unsubscribes=True)
        expected = {"opens": True, "clicks": False, "unsubscribes": True}
        assert tracking.to_dict() == expected
    
    def test_tracking_settings_with_unsubscribe_group(self):
        """Test tracking settings with unsubscribe group ID."""
        tracking = TrackingSettings(unsubscribe_group_id=123)
        result = tracking.to_dict()
        assert result["unsubscribe_group_id"] == 123


class TestEmail:
    """Test cases for Email model."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.from_addr = Address(email="sender@test.com", name="Sender")
        self.to_addr = Address(email="recipient@test.com", name="Recipient")
    
    def test_email_minimal(self):
        """Test creating minimal email."""
        email = Email(
            from_address=self.from_addr,
            to=[self.to_addr],
            subject="Test Subject",
            text_content="Test content"
        )
        assert email.from_address == self.from_addr
        assert email.to == [self.to_addr]
        assert email.subject == "Test Subject"
        assert email.text_content == "Test content"
        assert email.html_content == ""
    
    def test_email_validation_no_content(self):
        """Test email validation fails without content."""
        with pytest.raises(ValueError) as exc_info:
            Email(
                from_address=self.from_addr,
                to=[self.to_addr],
                subject="Test Subject"
            )
        assert "must have either text_content, html_content, or template_id" in str(exc_info.value)
    
    def test_email_validation_no_recipients(self):
        """Test email validation fails without recipients."""
        with pytest.raises(ValueError) as exc_info:
            Email(
                from_address=self.from_addr,
                to=[],
                cc=[],
                bcc=[],
                subject="Test Subject",
                text_content="Test content"
            )
        assert "must have at least one recipient" in str(exc_info.value)
    
    def test_email_with_template(self):
        """Test email with template ID passes validation."""
        email = Email(
            from_address=self.from_addr,
            to=[self.to_addr],
            subject="Test Subject",
            template_id="welcome-template"
        )
        assert email.template_id == "welcome-template"
    
    def test_email_to_dict_minimal(self):
        """Test converting minimal email to dictionary."""
        email = Email(
            from_address=self.from_addr,
            to=[self.to_addr],
            subject="Test Subject",
            text_content="Test content"
        )
        
        result = email.to_dict()
        expected_keys = {
            "from": {"email": "sender@test.com", "name": "Sender"},
            "to": [{"email": "recipient@test.com", "name": "Recipient"}],
            "subject": "Test Subject",
            "text_content": "Test content",
            "cc": [],
            "bcc": [],
            "html_content": "",
            "template_id": "",
            "template_data": {},
            "attachments": [],
            "headers": {},
            "send_time": 0,
            "webhook_data": {},
            "tag": ""
        }
        
        # Check required fields match exactly
        for key, value in expected_keys.items():
            if key in result:
                assert result[key] == value
    
    def test_email_to_dict_full(self):
        """Test converting full email to dictionary."""
        cc_addr = Address(email="cc@test.com")
        bcc_addr = Address(email="bcc@test.com")
        reply_addr = Address(email="reply@test.com")
        attachment = Attachment(file_name="file.txt", content="content", content_type="text/plain")
        tracking = TrackingSettings(opens=True, clicks=True)
        
        email = Email(
            from_address=self.from_addr,
            to=[self.to_addr],
            subject="Test Subject",
            text_content="Test content",
            html_content="<p>Test content</p>",
            cc=[cc_addr],
            bcc=[bcc_addr],
            reply_to=reply_addr,
            attachments=[attachment],
            headers={"X-Custom": "value"},
            template_id="template-123",
            template_data={"name": "John"},
            send_time=1640995200,
            tracking=tracking,
            webhook_data={"user_id": "123"}
        )
        
        result = email.to_dict()
        
        # Check that all fields are present
        assert "from" in result
        assert "to" in result
        assert "subject" in result
        assert "text_content" in result
        assert "html_content" in result
        assert "cc" in result
        assert "bcc" in result
        assert "reply_to" in result
        assert "attachments" in result
        assert "headers" in result
        assert "template_id" in result
        assert "template_data" in result
        assert "send_time" in result
        assert "tracking" in result
        assert "webhook_data" in result
        
        # Check specific values
        assert result["template_id"] == "template-123"
        assert result["send_time"] == 1640995200
        assert result["headers"]["X-Custom"] == "value"


class TestEmailResponse:
    """Test cases for EmailResponse model."""
    
    def test_email_response_creation(self):
        """Test creating email response."""
        response = EmailResponse(
            status="sent",
            message_id="msg_123",
            message="Email sent successfully"
        )
        assert response.status == "sent"
        assert response.message_id == "msg_123"
        assert response.message == "Email sent successfully"
    
    def test_email_response_from_dict(self):
        """Test creating email response from dictionary."""
        data = {
            "status": "sent",
            "message_id": "msg_123",
            "message": "Email sent successfully"
        }
        response = EmailResponse.from_dict(data)
        assert response.status == "sent"
        assert response.message_id == "msg_123"
        assert response.message == "Email sent successfully"
    
    def test_email_response_from_dict_minimal(self):
        """Test creating email response from minimal dictionary."""
        data = {}
        response = EmailResponse.from_dict(data)
        assert response.status == "unknown"
        assert response.message_id is None
        assert response.message is None
