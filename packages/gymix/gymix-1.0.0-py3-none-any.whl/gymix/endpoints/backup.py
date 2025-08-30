"""Backup endpoint for Gymix API."""

from typing import Dict, Any, BinaryIO, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import GymixClient


class BackupEndpoint:
    """Client for backup-related API endpoints."""
    
    def __init__(self, client: 'GymixClient'):
        self.client = client

    def create(self, gym_public_key: str, file: BinaryIO) -> Dict[str, Any]:
        """Upload a backup ZIP file for a gym.
        
        Args:
            gym_public_key: Public key of the gym
            file: Binary file object containing the ZIP backup
            
        Returns:
            Dict containing:
            - id: Backup ID
            - file_name: Name of the uploaded file
            - created_at: Timestamp of creation
            - size: File size in bytes
            - plan_info: Plan information and limits
            
        Raises:
            GymixAuthenticationError: Invalid API token
            GymixNotFoundError: Gym not found or not owned by user
            GymixForbiddenError: Subscription expired or backup not included in plan
            GymixRateLimitError: Daily backup limit reached
            GymixBadRequestError: Invalid file type (must be ZIP)
            GymixServerError: S3 upload failed
            GymixAPIError: Other API errors
        """
        data = {'gym_public_key': gym_public_key}
        files = {'file': file}
        response = self.client._make_request('POST', '/backup/create', data=data, files=files)
        return response.get('data', {})

    def get_plan(self, gym_public_key: str) -> Dict[str, Any]:
        """Get backup plan info and usage for a gym.
        
        Args:
            gym_public_key: Public key of the gym
            
        Returns:
            Dict containing:
            - plan_info: Plan details and backup features
            - current_usage: Current backup usage statistics
            - subscription_info: Subscription expiration info
            
        Raises:
            GymixAuthenticationError: Invalid API token
            GymixNotFoundError: Gym not found or not owned by user
            GymixForbiddenError: Subscription expired
            GymixAPIError: Other API errors
        """
        data = {'gym_public_key': gym_public_key}
        response = self.client._make_request('GET', '/backup/plan', params={'data': data})
        return response.get('data', {})

    def list(self, gym_public_key: str, verified: Optional[bool] = None) -> Dict[str, Any]:
        """List all backups for a gym.
        
        Args:
            gym_public_key: Public key of the gym
            verified: Optional filter for verified backups
            
        Returns:
            Dict containing:
            - backups: List of backup objects
            - total_count: Total number of backups
            - verified: Whether results are verified
            
        Raises:
            GymixAuthenticationError: Invalid API token
            GymixNotFoundError: Gym not found or not owned by user
            GymixForbiddenError: Subscription expired
            GymixAPIError: Other API errors
        """
        data = {'gym_public_key': gym_public_key}
        if verified is not None:
            data['verified'] = verified
            
        response = self.client._make_request('GET', '/backup/list', params={'data': data})
        return response.get('data', {})

    def download(self, backup_id: str, gym_public_key: str) -> Dict[str, Any]:
        """Get a signed download URL for a backup file.
        
        Args:
            backup_id: ID of the backup to download
            gym_public_key: Public key of the gym
            
        Returns:
            Dict containing:
            - backup_id: ID of the backup
            - file_name: Name of the backup file
            - download_url: Signed URL for downloading (expires in 24 hours)
            - expires_in: Expiration time info
            - created_at: Backup creation timestamp
            - cached: Whether result was cached
            
        Raises:
            GymixAuthenticationError: Invalid API token
            GymixNotFoundError: Gym or backup not found
            GymixForbiddenError: Subscription expired
            GymixBadRequestError: Backup missing bucket info
            GymixServerError: S3 error or download URL generation failed
            GymixAPIError: Other API errors
        """
        data = {'gym_public_key': gym_public_key}
        response = self.client._make_request('POST', f'/backup/download/{backup_id}', data=data)
        return response.get('data', {})

    def delete(self, backup_id: str, gym_public_key: str) -> Dict[str, Any]:
        """Delete a backup file from S3 and database.
        
        Args:
            backup_id: ID of the backup to delete
            gym_public_key: Public key of the gym
            
        Returns:
            Dict containing:
            - backup_id: ID of the deleted backup
            - message: Success message
            
        Raises:
            GymixAuthenticationError: Invalid API token
            GymixNotFoundError: Gym or backup not found
            GymixForbiddenError: Subscription expired
            GymixBadRequestError: Backup missing bucket info
            GymixAPIError: Other API errors
        """
        data = {'gym_public_key': gym_public_key}
        response = self.client._make_request('DELETE', f'/backup/delete/{backup_id}', data=data)
        return response.get('data', {})
