"""Custom exceptions for ItryID SDK."""

class ItryIDError(Exception):
    """Base exception for ItryID SDK."""
    pass

class NetworkError(ItryIDError):
    """Raised when network request fails."""
    pass

class AuthenticationError(ItryIDError):
    """Raised when authentication fails."""
    pass

class ValidationError(ItryIDError):
    """Raised when input validation fails."""
    pass

class ServerError(ItryIDError):
    """Raised when server returns an error."""
    pass
