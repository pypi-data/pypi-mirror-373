"""Tests for the Laneful client."""

import json
from unittest.mock import Mock, patch

import pytest
from requests.exceptions import ConnectionError, Timeout

from laneful import Address, Email, EmailResponse, LanefulClient
from laneful.exceptions import LanefulAPIError, LanefulAuthError, LanefulError


class TestLanefulClient:
    """Test cases for LanefulClient."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = LanefulClient(
            base_url="https://test.laneful.net",
            auth_token="test-token"
        )
        
        self.sample_email = Email(
            from_address=Address(email="sender@test.com", name="Test Sender"),
            to=[Address(email="recipient@test.com", name="Test Recipient")],
            subject="Test Subject",
            text_content="Test content"
        )
    
    def test_client_initialization(self):
        """Test client initialization."""
        assert self.client.base_url == "https://test.laneful.net"
        assert self.client.auth_token == "test-token"
        assert "Bearer test-token" in self.client.session.headers["Authorization"]
    
    def test_client_initialization_strips_trailing_slash(self):
        """Test that trailing slashes are stripped from base URL."""
        client = LanefulClient("https://test.laneful.net/", "token")
        assert client.base_url == "https://test.laneful.net"
    
    @patch('requests.Session.request')
    def test_send_email_success(self, mock_request):
        """Test successful email sending."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.text = '{"status": "sent", "message_id": "msg_123"}'
        mock_response.json.return_value = {
            "status": "sent",
            "message_id": "msg_123"
        }
        mock_request.return_value = mock_response
        
        response = self.client.send_email(self.sample_email)
        
        assert isinstance(response, EmailResponse)
        assert response.status == "sent"
        assert response.message_id == "msg_123"
        
        # Verify the request was made correctly
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["method"] == "POST"
        assert "/email" in call_args[1]["url"]
        assert call_args[1]["json"] == {'emails': [self.sample_email.to_dict()]}
    
    @patch('requests.Session.request')
    def test_send_emails_success(self, mock_request):
        """Test successful bulk email sending."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.text = '{"responses": [{"status": "sent", "message_id": "msg_123"}, {"status": "sent", "message_id": "msg_124"}]}'
        mock_response.json.return_value = {
            "responses": [
                {"status": "sent", "message_id": "msg_123"},
                {"status": "sent", "message_id": "msg_124"}
            ]
        }
        mock_request.return_value = mock_response
        
        emails = [self.sample_email, self.sample_email]
        responses = self.client.send_emails(emails)
        
        assert len(responses) == 2
        assert all(isinstance(r, EmailResponse) for r in responses)
        assert responses[0].message_id == "msg_123"
        assert responses[1].message_id == "msg_124"
    
    @patch('requests.Session.request')
    def test_send_email_auth_error(self, mock_request):
        """Test authentication error handling."""
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 401
        mock_response.text = '{"message": "Unauthorized"}'
        mock_response.json.return_value = {"message": "Unauthorized"}
        mock_request.return_value = mock_response
        
        with pytest.raises(LanefulAuthError) as exc_info:
            self.client.send_email(self.sample_email)
        
        assert "Invalid authentication token" in str(exc_info.value)
    
    @patch('requests.Session.request')
    def test_send_email_api_error(self, mock_request):
        """Test API error handling."""
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 400
        mock_response.text = '{"message": "Invalid email format"}'
        mock_response.json.return_value = {"message": "Invalid email format"}
        mock_request.return_value = mock_response
        
        with pytest.raises(LanefulAPIError) as exc_info:
            self.client.send_email(self.sample_email)
        
        assert exc_info.value.status_code == 400
        assert "Invalid email format" in exc_info.value.message
    
    @patch('requests.Session.request')
    def test_send_email_connection_error(self, mock_request):
        """Test connection error handling."""
        mock_request.side_effect = ConnectionError("Connection failed")
        
        with pytest.raises(LanefulError) as exc_info:
            self.client.send_email(self.sample_email)
        
        assert "Failed to connect to Laneful API" in str(exc_info.value)
    
    @patch('requests.Session.request')
    def test_send_email_timeout(self, mock_request):
        """Test timeout error handling."""
        mock_request.side_effect = Timeout("Request timed out")
        
        with pytest.raises(LanefulError) as exc_info:
            self.client.send_email(self.sample_email)
        
        assert "Request timed out" in str(exc_info.value)
    
    @patch('requests.Session.request')
    def test_send_email_json_decode_error(self, mock_request):
        """Test handling of invalid JSON responses."""
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 500
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_response.text = "Internal Server Error"
        mock_request.return_value = mock_response
        
        with pytest.raises(LanefulAPIError) as exc_info:
            self.client.send_email(self.sample_email)
        
        assert exc_info.value.status_code == 500
        assert "Internal Server Error" in exc_info.value.message
    
    def test_send_emails_empty_list(self):
        """Test that sending empty email list raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            self.client.send_emails([])
        
        assert "Email list cannot be empty" in str(exc_info.value)
    
    @patch('requests.Session.request')
    def test_get_email_status(self, mock_request):
        """Test getting email status."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.text = '{"status": "delivered", "delivered_at": 1640995200}'
        mock_response.json.return_value = {
            "status": "delivered",
            "delivered_at": 1640995200
        }
        mock_request.return_value = mock_response
        
        status = self.client.get_email_status("msg_123")
        
        assert status["status"] == "delivered"
        assert status["delivered_at"] == 1640995200
        
        # Verify the request was made correctly
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["method"] == "GET"
        assert "/email/msg_123/status" in call_args[1]["url"]
    
    def test_context_manager(self):
        """Test client as context manager."""
        with patch.object(self.client, 'close') as mock_close:
            with self.client as client:
                assert client is self.client
            mock_close.assert_called_once()
    
    def test_close(self):
        """Test client close method."""
        with patch.object(self.client.session, 'close') as mock_close:
            self.client.close()
            mock_close.assert_called_once()
