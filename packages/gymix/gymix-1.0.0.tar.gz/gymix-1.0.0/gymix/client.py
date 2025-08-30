"""Main Gymix API client."""

import json
from typing import Dict, Any, Optional, BinaryIO
import requests

from .exceptions import (
    GymixAPIError,
    GymixAuthenticationError,
    GymixForbiddenError,
    GymixNotFoundError,
    GymixBadRequestError,
    GymixRateLimitError,
    GymixServerError,
    GymixServiceUnavailableError
)
from .endpoints.users import UsersEndpoint
from .endpoints.gym import GymEndpoint  
from .endpoints.backup import BackupEndpoint
from .endpoints.health import HealthEndpoint


class GymixClient:
    """Main client for interacting with the Gymix API."""
    
    def __init__(
        self,
        api_token: str,
        base_url: str = "https://api.gymix.ir",
        timeout: int = 30
    ):
        """Initialize the Gymix client.
        
        Args:
            api_token: Your Gymix API token
            base_url: Base URL for the API (default: https://api.gymix.ir)
            timeout: Request timeout in seconds (default: 30)
        """
        self.api_token = api_token
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_token}',
            'User-Agent': 'Gymix-Python-SDK/1.0.0'
        })
        
        # Initialize endpoint clients
        self.users = UsersEndpoint(self)
        self.gym = GymEndpoint(self)
        self.backup = BackupEndpoint(self)
        self.health = HealthEndpoint(self)

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        require_auth: bool = True
    ) -> Dict[str, Any]:
        """Make an HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, DELETE, etc.)
            endpoint: API endpoint path
            params: Query parameters
            data: Form data
            files: Files to upload
            json_data: JSON data to send
            require_auth: Whether authentication is required
            
        Returns:
            Parsed JSON response
            
        Raises:
            GymixAPIError: For various API errors
        """
        url = f"{self.base_url}{endpoint}"
        
        # Prepare headers
        headers = {}
        if not require_auth:
            # Remove auth header for health endpoint
            headers['Authorization'] = None
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                files=files,
                json=json_data,
                headers=headers,
                timeout=self.timeout
            )
            
            # Handle different response types
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = {"message": response.text}
            
            # Check for errors
            if not response.ok:
                self._handle_error_response(response.status_code, response_data)
            
            return response_data
            
        except requests.exceptions.Timeout:
            raise GymixAPIError("Request timeout")
        except requests.exceptions.ConnectionError:
            raise GymixAPIError("Connection error")
        except requests.exceptions.RequestException as e:
            raise GymixAPIError(f"Request failed: {str(e)}")

    def _handle_error_response(self, status_code: int, response_data: Dict[str, Any]) -> None:
        """Handle error responses from the API.
        
        Args:
            status_code: HTTP status code
            response_data: Response data from API
            
        Raises:
            Appropriate GymixAPIError subclass
        """
        # Extract error message
        message = "Unknown error"
        if "return" in response_data and "message" in response_data["return"]:
            message = response_data["return"]["message"]
        elif "message" in response_data:
            message = response_data["message"]
        
        # Map status codes to exceptions
        if status_code == 400:
            raise GymixBadRequestError(message, status_code, response_data)
        elif status_code == 401:
            raise GymixAuthenticationError(message, status_code, response_data)
        elif status_code == 403:
            raise GymixForbiddenError(message, status_code, response_data)
        elif status_code == 404:
            raise GymixNotFoundError(message, status_code, response_data)
        elif status_code == 429:
            raise GymixRateLimitError(message, status_code, response_data)
        elif status_code == 503:
            raise GymixServiceUnavailableError(message, status_code, response_data)
        elif status_code >= 500:
            raise GymixServerError(message, status_code, response_data)
        else:
            raise GymixAPIError(message, status_code, response_data)

    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
