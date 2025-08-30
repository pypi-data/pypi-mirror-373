"""Health endpoint for Gymix API."""

from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import GymixClient


class HealthEndpoint:
    """Client for health check API endpoints."""
    
    def __init__(self, client: 'GymixClient'):
        self.client = client

    def check(self) -> Dict[str, Any]:
        """Check API health status and basic system information.
        
        Returns:
            Dict containing:
            - status: Health status ("healthy" or "unhealthy")
            - timestamp: Current timestamp
            - version: API version
            - uptime: Service uptime
            - database: Database connection status
            - storage: Storage system status
            
        Raises:
            GymixServiceUnavailableError: API temporarily unavailable
            GymixAPIError: Other API errors
        """
        response = self.client._make_request('GET', '/health', require_auth=False)
        return response.get('data', {})
