"""Gym endpoint for Gymix API."""

from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import GymixClient


class GymEndpoint:
    """Client for gym-related API endpoints."""
    
    def __init__(self, client: 'GymixClient'):
        self.client = client

    def get_info(self, gym_public_key: str) -> Dict[str, Any]:
        """Get gym details, subscription, and plan info.
        
        Args:
            gym_public_key: Public key of the gym
            
        Returns:
            Dict containing:
            - gym_info: Basic gym information (name, location, status, etc.)
            - subscription_info: Current subscription details
            - plan_info: Plan details and features
            - subscription_summary: Summary of subscription status
            
        Raises:
            GymixAuthenticationError: Invalid API token
            GymixNotFoundError: Gym not found or not owned by user
            GymixAPIError: Other API errors
        """
        data = {'gym_public_key': gym_public_key}
        response = self.client._make_request('POST', '/gym/info', data=data)
        return response.get('data', {})
