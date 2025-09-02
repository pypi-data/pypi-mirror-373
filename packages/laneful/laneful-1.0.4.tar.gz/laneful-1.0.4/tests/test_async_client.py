"""Tests for the async Laneful client."""

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest

try:
    import aiohttp
    from aiohttp import ClientConnectorError, ClientTimeout

    from laneful import AsyncLanefulClient
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    AsyncLanefulClient = None

from laneful import Address, Email, EmailResponse
from laneful.exceptions import LanefulAPIError, LanefulAuthError, LanefulError

# Skip all tests if aiohttp is not available
pytestmark = pytest.mark.skipif(not AIOHTTP_AVAILABLE, reason="aiohttp not available")


class TestAsyncLanefulClient:
    """Test cases for AsyncLanefulClient."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = AsyncLanefulClient(
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
        assert "Bearer test-token" in self.client.headers["Authorization"]
        assert isinstance(self.client.aiohttp_timeout, ClientTimeout)
    
    def test_client_initialization_strips_trailing_slash(self):
        """Test that trailing slashes are stripped from base URL."""
        client = AsyncLanefulClient("https://test.laneful.net/", "token")
        assert client.base_url == "https://test.laneful.net"
    
    @pytest.mark.asyncio
    async def test_session_creation(self):
        """Test that aiohttp session is created properly."""
        session = await self.client._get_session()
        assert isinstance(session, aiohttp.ClientSession)
        assert not session.closed
        
        # Test that same session is returned on subsequent calls
        session2 = await self.client._get_session()
        assert session is session2
        
        await self.client.close()
    
    @pytest.mark.asyncio
    async def test_send_email_success(self):
        """Test successful async email sending."""
        response_data = {
            "status": "sent",
            "message_id": "msg_123"
        }
        
        with patch.object(self.client, '_make_request', return_value=response_data) as mock_request:
            response = await self.client.send_email(self.sample_email)
            
            assert isinstance(response, EmailResponse)
            assert response.status == "sent"
            assert response.message_id == "msg_123"
            
            # Verify the request was made correctly
            mock_request.assert_called_once_with("POST", "/email/send", {'emails': [self.sample_email.to_dict()]})
    
    @pytest.mark.asyncio
    async def test_send_emails_success(self):
        """Test successful bulk async email sending."""
        response_data = {
            "responses": [
                {"status": "sent", "message_id": "msg_123"},
                {"status": "sent", "message_id": "msg_124"}
            ]
        }
        
        with patch.object(self.client, '_make_request', return_value=response_data) as mock_request:
            emails = [self.sample_email, self.sample_email]
            responses = await self.client.send_emails(emails)
            
            assert len(responses) == 2
            assert all(isinstance(r, EmailResponse) for r in responses)
            assert responses[0].message_id == "msg_123"
            assert responses[1].message_id == "msg_124"
    
    @pytest.mark.asyncio
    async def test_send_email_auth_error(self):
        """Test async authentication error handling."""
        with patch.object(self.client, '_make_request', side_effect=LanefulAuthError("Invalid authentication token")):
            with pytest.raises(LanefulAuthError) as exc_info:
                await self.client.send_email(self.sample_email)
            
            assert "Invalid authentication token" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_send_email_api_error(self):
        """Test async API error handling."""
        api_error = LanefulAPIError("Invalid email format", status_code=400)
        
        with patch.object(self.client, '_make_request', side_effect=api_error):
            with pytest.raises(LanefulAPIError) as exc_info:
                await self.client.send_email(self.sample_email)
            
            assert exc_info.value.status_code == 400
            assert "Invalid email format" in exc_info.value.message
    
    @pytest.mark.asyncio
    async def test_send_email_connection_error(self):
        """Test async connection error handling."""
        with patch.object(self.client, '_make_request', side_effect=LanefulError("Failed to connect to Laneful API")):
            with pytest.raises(LanefulError) as exc_info:
                await self.client.send_email(self.sample_email)
            
            assert "Failed to connect to Laneful API" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_send_email_timeout(self):
        """Test async timeout error handling."""
        with patch.object(self.client, '_make_request', side_effect=LanefulError("Request timed out")):
            with pytest.raises(LanefulError) as exc_info:
                await self.client.send_email(self.sample_email)
            
            assert "Request timed out" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_send_email_json_decode_error(self):
        """Test handling of invalid JSON responses in async client."""
        api_error = LanefulAPIError("Internal Server Error", status_code=500)
        
        with patch.object(self.client, '_make_request', side_effect=api_error):
            with pytest.raises(LanefulAPIError) as exc_info:
                await self.client.send_email(self.sample_email)
            
            assert exc_info.value.status_code == 500
            assert "Internal Server Error" in exc_info.value.message
    
    @pytest.mark.asyncio
    async def test_send_emails_empty_list(self):
        """Test that sending empty email list raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            await self.client.send_emails([])
        
        assert "Email list cannot be empty" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_email_status(self):
        """Test getting email status asynchronously."""
        response_data = {
            "status": "delivered",
            "delivered_at": 1640995200
        }
        
        with patch.object(self.client, '_make_request', return_value=response_data) as mock_request:
            status = await self.client.get_email_status("msg_123")
            
            assert status["status"] == "delivered"
            assert status["delivered_at"] == 1640995200
            
            # Verify the request was made correctly
            mock_request.assert_called_once_with("GET", "/email/msg_123/status")
    
    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Test client as async context manager."""
        with patch.object(self.client, 'close') as mock_close:
            async with self.client as client:
                assert client is self.client
            mock_close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_close(self):
        """Test async client close method."""
        # Create a mock session
        mock_session = AsyncMock()
        mock_session.closed = False
        self.client._session = mock_session
        
        await self.client.close()
        mock_session.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_close_already_closed_session(self):
        """Test closing when session is already closed."""
        # Create a mock session that's already closed
        mock_session = AsyncMock()
        mock_session.closed = True
        self.client._session = mock_session
        
        # Should not raise an exception
        await self.client.close()
        mock_session.close.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_close_no_session(self):
        """Test closing when no session exists."""
        # Should not raise an exception
        await self.client.close()
    
    def test_del_with_unclosed_session(self):
        """Test __del__ warning when session is not closed."""
        import warnings

        # Create a mock session that's not closed
        mock_session = Mock()
        mock_session.closed = False
        self.client._session = mock_session
        
        # Should issue a warning
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            self.client.__del__()
            
            assert len(w) == 1
            assert issubclass(w[0].category, ResourceWarning)
            assert "session was not closed properly" in str(w[0].message)
    
    def test_del_with_closed_session(self):
        """Test __del__ with closed session (no warning)."""
        import warnings

        # Create a mock session that's closed
        mock_session = Mock()
        mock_session.closed = True
        self.client._session = mock_session
        
        # Should not issue a warning
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            self.client.__del__()
            
            # Filter out any unrelated warnings
            relevant_warnings = [warning for warning in w 
                               if "session was not closed properly" in str(warning.message)]
            assert len(relevant_warnings) == 0
    
    def test_del_no_session(self):
        """Test __del__ when no session exists."""
        # Should not raise an exception or warning
        self.client.__del__()


@pytest.mark.asyncio
async def test_multiple_concurrent_requests():
    """Test that multiple concurrent requests work properly."""
    client = AsyncLanefulClient(
        base_url="https://test.laneful.net",
        auth_token="test-token"
    )
    
    sample_email = Email(
        from_address=Address(email="sender@test.com"),
        to=[Address(email="recipient@test.com")],
        subject="Test Subject",
        text_content="Test content"
    )
    
    response_data = {
        "status": "sent",
        "message_id": "msg_123"
    }
    
    with patch.object(client, '_make_request', return_value=response_data) as mock_request:
        # Send multiple emails concurrently
        tasks = [client.send_email(sample_email) for _ in range(5)]
        responses = await asyncio.gather(*tasks)
        
        # All should succeed
        assert len(responses) == 5
        assert all(response.status == "sent" for response in responses)
        
        # Request should have been called 5 times
        assert mock_request.call_count == 5
    
    await client.close()
