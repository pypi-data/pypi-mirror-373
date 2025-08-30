"""Users endpoint for Gymix API."""

from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import GymixClient


class UsersEndpoint:
    """Client for user-related API endpoints."""
    
    def __init__(self, client: 'GymixClient'):
        self.client = client

    def get_info(self) -> Dict[str, Any]:
        """Get current user's profile and gyms.
        
        Returns:
            Dict containing user information including:
            - status: User account status
            - name: User's first name
            - lastname: User's last name  
            - phone: User's phone number
            - address: User's address
            - gyms: List of user's gyms
            - balance: User's account balance
            
        Raises:
            GymixAuthenticationError: Invalid or missing auth token
            GymixForbiddenError: Account deactivated or restricted
            GymixAPIError: Other API errors
        """
        response = self.client._make_request('GET', '/users/info')
        return response.get('data', {})
