"""Custom exceptions for Gymix API client."""

from typing import Optional, Dict, Any


class GymixAPIError(Exception):
    """Base exception for all Gymix API errors."""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class GymixAuthenticationError(GymixAPIError):
    """Raised when authentication fails (401 Unauthorized)."""
    pass


class GymixForbiddenError(GymixAPIError):
    """Raised when access is forbidden (403 Forbidden)."""
    pass


class GymixNotFoundError(GymixAPIError):
    """Raised when a resource is not found (404 Not Found)."""
    pass


class GymixBadRequestError(GymixAPIError):
    """Raised when the request is invalid (400 Bad Request)."""
    pass


class GymixRateLimitError(GymixAPIError):
    """Raised when rate limit is exceeded (429 Too Many Requests)."""
    pass


class GymixServerError(GymixAPIError):
    """Raised when there's a server error (5xx status codes)."""
    pass


class GymixServiceUnavailableError(GymixAPIError):
    """Raised when the service is temporarily unavailable (503 Service Unavailable)."""
    pass
