"""Exception classes for the Sovant SDK."""

from typing import Any, Dict, Optional


class SovantError(Exception):
    """Base exception for all Sovant errors."""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.details = details or {}


class AuthenticationError(SovantError):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, 401)


class RateLimitError(SovantError):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None):
        super().__init__(message, 429)
        self.retry_after = retry_after


class ValidationError(SovantError):
    """Raised when validation fails."""
    
    def __init__(
        self,
        message: str = "Validation failed",
        errors: Optional[Dict[str, list[str]]] = None,
    ):
        super().__init__(message, 400)
        self.errors = errors or {}


class NotFoundError(SovantError):
    """Raised when a resource is not found."""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, 404)


class NetworkError(SovantError):
    """Raised when a network error occurs."""
    
    def __init__(self, message: str = "Network request failed"):
        super().__init__(message)