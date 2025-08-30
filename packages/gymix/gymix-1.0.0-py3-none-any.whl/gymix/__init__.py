"""Gymix Python SDK - Official client library for Gymix API."""

from .client import GymixClient
from .exceptions import (
    GymixAPIError,
    GymixAuthenticationError,
    GymixForbiddenError,
    GymixNotFoundError,
    GymixRateLimitError,
    GymixServerError,
    GymixBadRequestError
)

__version__ = "1.0.0"
__author__ = "Gymix Team"
__email__ = "support@gymix.ir"

__all__ = [
    "GymixClient",
    "GymixAPIError",
    "GymixAuthenticationError", 
    "GymixForbiddenError",
    "GymixNotFoundError",
    "GymixRateLimitError",
    "GymixServerError",
    "GymixBadRequestError",
]
