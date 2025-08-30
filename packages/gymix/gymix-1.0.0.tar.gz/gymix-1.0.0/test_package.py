#!/usr/bin/env python3
"""
Test script to verify Gymix SDK package functionality.

This script tests the basic functionality of the Gymix SDK without making actual API calls.
"""

import sys
import traceback
from io import BytesIO


def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        # Test main imports
        from gymix import GymixClient
        from gymix.exceptions import (
            GymixAPIError,
            GymixAuthenticationError,
            GymixForbiddenError,
            GymixNotFoundError,
            GymixRateLimitError,
            GymixServerError,
            GymixBadRequestError
        )
        
        # Test endpoint imports
        from gymix.endpoints.users import UsersEndpoint
        from gymix.endpoints.gym import GymEndpoint
        from gymix.endpoints.backup import BackupEndpoint
        from gymix.endpoints.health import HealthEndpoint
        
        print("✅ All imports successful")
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_client_initialization():
    """Test client initialization."""
    print("\nTesting client initialization...")
    
    try:
        from gymix import GymixClient
        
        # Test basic initialization
        client = GymixClient(api_token="test_token")
        
        assert client.api_token == "test_token"
        assert client.base_url == "https://api.gymix.ir"
        assert client.timeout == 30
        
        # Test custom initialization
        custom_client = GymixClient(
            api_token="custom_token",
            base_url="https://custom.api.com",
            timeout=60
        )
        
        assert custom_client.api_token == "custom_token"
        assert custom_client.base_url == "https://custom.api.com"
        assert custom_client.timeout == 60
        
        # Test endpoints are initialized
        assert hasattr(client, 'users')
        assert hasattr(client, 'gym')
        assert hasattr(client, 'backup')
        assert hasattr(client, 'health')
        
        # Test session headers
        assert "Authorization" in client.session.headers
        assert client.session.headers["Authorization"] == "Bearer test_token"
        assert "User-Agent" in client.session.headers
        
        print("✅ Client initialization successful")
        return True
        
    except Exception as e:
        print(f"❌ Client initialization failed: {e}")
        traceback.print_exc()
        return False


def test_exception_classes():
    """Test exception classes."""
    print("\nTesting exception classes...")
    
    try:
        from gymix.exceptions import GymixAPIError, GymixAuthenticationError
        
        # Test base exception
        base_error = GymixAPIError("Test error", 400, {"key": "value"})
        assert str(base_error) == "[400] Test error"
        assert base_error.status_code == 400
        assert base_error.response_data == {"key": "value"}
        
        # Test specific exception
        auth_error = GymixAuthenticationError("Auth failed", 401)
        assert auth_error.status_code == 401
        assert "Auth failed" in str(auth_error)
        
        # Test exception inheritance
        assert isinstance(auth_error, GymixAPIError)
        
        print("✅ Exception classes working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Exception classes test failed: {e}")
        traceback.print_exc()
        return False


def test_context_manager():
    """Test context manager functionality."""
    print("\nTesting context manager...")
    
    try:
        from gymix import GymixClient
        
        with GymixClient(api_token="test_token") as client:
            assert client.api_token == "test_token"
            assert hasattr(client, 'session')
        
        print("✅ Context manager working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Context manager test failed: {e}")
        traceback.print_exc()
        return False


def test_endpoint_methods():
    """Test that endpoint methods exist and can be called."""
    print("\nTesting endpoint method signatures...")
    
    try:
        from gymix import GymixClient
        
        client = GymixClient(api_token="test_token")
        
        # Test users endpoint
        assert hasattr(client.users, 'get_info')
        
        # Test gym endpoint
        assert hasattr(client.gym, 'get_info')
        
        # Test backup endpoint
        assert hasattr(client.backup, 'create')
        assert hasattr(client.backup, 'list')
        assert hasattr(client.backup, 'download')
        assert hasattr(client.backup, 'delete')
        assert hasattr(client.backup, 'get_plan')
        
        # Test health endpoint
        assert hasattr(client.health, 'check')
        
        print("✅ All endpoint methods exist")
        return True
        
    except Exception as e:
        print(f"❌ Endpoint methods test failed: {e}")
        traceback.print_exc()
        return False


def test_version_info():
    """Test version information."""
    print("\nTesting version information...")
    
    try:
        import gymix
        
        # Check version attributes exist
        assert hasattr(gymix, '__version__')
        assert hasattr(gymix, '__author__')
        assert hasattr(gymix, '__email__')
        
        print(f"✅ Version: {gymix.__version__}")
        print(f"✅ Author: {gymix.__author__}")
        print(f"✅ Email: {gymix.__email__}")
        return True
        
    except Exception as e:
        print(f"❌ Version info test failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("Gymix SDK Package Test Suite")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_client_initialization,
        test_exception_classes,
        test_context_manager,
        test_endpoint_methods,
        test_version_info,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 40)
    print("Test Results:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed! Package is ready for use.")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please fix the issues.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
