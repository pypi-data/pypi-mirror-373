"""
ItryID SDK - Modern Python SDK for user authentication and game progress management.
"""

from .client import ItryIDClient
from .exceptions import ItryIDError, NetworkError, AuthenticationError, ValidationError
from .models import User, GameProgress, APIResponse

__version__ = "2.0.0"
__all__ = ["ItryIDClient", "ItryIDError", "NetworkError", "AuthenticationError", "ValidationError", "User", "GameProgress", "APIResponse"]
