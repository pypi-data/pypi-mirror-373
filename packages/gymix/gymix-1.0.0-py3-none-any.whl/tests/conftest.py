"""Test configuration and fixtures."""

import pytest
from gymix import GymixClient


@pytest.fixture
def client():
    """Create a test client instance."""
    return GymixClient(api_token="test_token")


@pytest.fixture
def mock_user_response():
    """Mock user info response."""
    return {
        "return": {"status": 200, "message": "تایید شد"},
        "data": {
            "status": "active",
            "name": "John",
            "lastname": "Doe", 
            "phone": "09123456789",
            "address": "Tehran",
            "gyms": [{"id": "gym1", "name": "Test Gym", "location": "Tehran"}],
            "balance": 100000
        }
    }


@pytest.fixture  
def mock_gym_response():
    """Mock gym info response."""
    return {
        "return": {"status": 200, "message": "تایید شد"},
        "data": {
            "gym_info": {
                "name": "Test Gym",
                "location": "Tehran",
                "status": "Active",
                "created_at": "2025-08-29T12:00:00Z"
            },
            "subscription_info": {
                "id": "sub_123",
                "name": "Premium Plan",
                "price": 100000,
                "status": "active"
            }
        }
    }
