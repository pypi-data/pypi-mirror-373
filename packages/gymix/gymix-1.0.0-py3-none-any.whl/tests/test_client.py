"""Tests for the main Gymix client."""

import pytest
import requests_mock
from gymix import GymixClient
from gymix.exceptions import (
    GymixAuthenticationError,
    GymixNotFoundError,
    GymixForbiddenError
)


class TestGymixClient:
    """Test cases for GymixClient."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = GymixClient(api_token="test_token")
        self.base_url = "https://api.gymix.ir"

    def test_client_initialization(self):
        """Test client initialization with default and custom parameters."""
        # Test default initialization
        client = GymixClient(api_token="test_token")
        assert client.api_token == "test_token"
        assert client.base_url == "https://api.gymix.ir"
        assert client.timeout == 30
        
        # Test custom initialization
        client = GymixClient(
            api_token="custom_token",
            base_url="https://custom.api.com",
            timeout=60
        )
        assert client.api_token == "custom_token"
        assert client.base_url == "https://custom.api.com"
        assert client.timeout == 60

    @requests_mock.Mocker()
    def test_successful_request(self, m):
        """Test successful API request."""
        expected_response = {
            "return": {"status": 200, "message": "تایید شد"},
            "data": {"name": "John", "lastname": "Doe"}
        }
        
        m.get(f"{self.base_url}/users/info", json=expected_response)
        
        result = self.client.users.get_info()
        assert result["name"] == "John"
        assert result["lastname"] == "Doe"

    @requests_mock.Mocker()
    def test_authentication_error(self, m):
        """Test authentication error handling."""
        error_response = {
            "return": {"status": 401, "message": "توکن API نامعتبر"},
            "data": {}
        }
        
        m.get(f"{self.base_url}/users/info", json=error_response, status_code=401)
        
        with pytest.raises(GymixAuthenticationError) as exc_info:
            self.client.users.get_info()
        
        assert exc_info.value.status_code == 401
        assert "توکن API نامعتبر" in str(exc_info.value)

    @requests_mock.Mocker()
    def test_not_found_error(self, m):
        """Test not found error handling."""
        error_response = {
            "return": {"status": 404, "message": "باشگاه مورد نظر یافت نشد"},
            "data": {}
        }
        
        m.post(f"{self.base_url}/gym/info", json=error_response, status_code=404)
        
        with pytest.raises(GymixNotFoundError) as exc_info:
            self.client.gym.get_info("invalid_gym_key")
        
        assert exc_info.value.status_code == 404

    @requests_mock.Mocker()
    def test_forbidden_error(self, m):
        """Test forbidden error handling."""
        error_response = {
            "return": {"status": 403, "message": "اشتراک باشگاه منقضی شده است"},
            "data": {}
        }
        
        m.get(f"{self.base_url}/backup/list", json=error_response, status_code=403)
        
        with pytest.raises(GymixForbiddenError) as exc_info:
            self.client.backup.list("expired_gym_key")
        
        assert exc_info.value.status_code == 403

    def test_context_manager(self):
        """Test context manager functionality."""
        with GymixClient(api_token="test_token") as client:
            assert client.api_token == "test_token"
        # Client should be closed after exiting context

    def test_session_headers(self):
        """Test that session headers are set correctly."""
        client = GymixClient(api_token="test_token")
        
        assert client.session.headers["Authorization"] == "Bearer test_token"
        assert "Gymix-Python-SDK" in client.session.headers["User-Agent"]
