"""
MailBlock SDK Exception Classes

This module defines all custom exceptions used throughout the MailBlock SDK.
"""

from typing import Optional, Dict, Any


class MailBlockError(Exception):
    """Base exception class for all MailBlock SDK errors."""
    
    def __init__(
        self,
        message: str,
        error_type: Optional[str] = None,
        status_code: Optional[int] = None,
        request_id: Optional[str] = None,
        suggestion: Optional[str] = None,
        **kwargs: Any
    ):
        super().__init__(message)
        self.message = message
        self.error_type = error_type or "UNKNOWN_ERROR"
        self.status_code = status_code
        self.request_id = request_id
        self.suggestion = suggestion
        self.details = kwargs

    def __str__(self) -> str:
        parts = [self.message]
        if self.error_type:
            parts.append(f"Error Type: {self.error_type}")
        if self.request_id:
            parts.append(f"Request ID: {self.request_id}")
        if self.suggestion:
            parts.append(f"Suggestion: {self.suggestion}")
        return " | ".join(parts)


class ValidationError(MailBlockError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, **kwargs: Any):
        super().__init__(
            message=message,
            error_type="VALIDATION_ERROR",
            **kwargs
        )


class AuthenticationError(MailBlockError):
    """Raised when API key authentication fails."""
    
    def __init__(self, message: str, **kwargs: Any):
        super().__init__(
            message=message,
            error_type="AUTHENTICATION_ERROR",
            status_code=401,
            suggestion="Verify your API key is correct and has proper permissions",
            **kwargs
        )


class AuthorizationError(MailBlockError):
    """Raised when API key lacks required permissions."""
    
    def __init__(self, message: str, **kwargs: Any):
        super().__init__(
            message=message,
            error_type="AUTHORIZATION_ERROR",
            status_code=403,
            suggestion="Your API key may not have permission for this operation",
            **kwargs
        )


class RateLimitError(MailBlockError):
    """Raised when API rate limits are exceeded."""
    
    def __init__(self, message: str, **kwargs: Any):
        super().__init__(
            message=message,
            error_type="RATE_LIMIT_ERROR",
            status_code=429,
            suggestion="You are being rate limited. Wait a moment and try again",
            **kwargs
        )


class ServerError(MailBlockError):
    """Raised when the MailBlock API returns a server error."""
    
    def __init__(self, message: str, status_code: int = 500, **kwargs: Any):
        suggestion = {
            500: "Server error occurred. Try again in a few moments",
            502: "Bad Gateway. The server is temporarily unavailable",
            503: "Service temporarily unavailable. Please try again later",
            504: "Gateway timeout. The request took too long to process"
        }.get(status_code, "Server error occurred. Please try again later")
        
        super().__init__(
            message=message,
            error_type="SERVER_ERROR",
            status_code=status_code,
            suggestion=suggestion,
            **kwargs
        )


class NetworkError(MailBlockError):
    """Raised when network communication fails."""
    
    def __init__(self, message: str, **kwargs: Any):
        super().__init__(
            message=message,
            error_type="NETWORK_ERROR",
            suggestion="Check your internet connection and try again",
            **kwargs
        )


class TimeoutError(MailBlockError):
    """Raised when requests timeout."""
    
    def __init__(self, message: str, **kwargs: Any):
        super().__init__(
            message=message,
            error_type="TIMEOUT_ERROR",
            suggestion="Request timed out. Try again with a longer timeout",
            **kwargs
        )