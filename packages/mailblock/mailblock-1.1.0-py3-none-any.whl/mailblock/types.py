"""
MailBlock SDK Type Definitions

This module defines type hints and data structures used throughout the SDK.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, Union, List
from enum import Enum

try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict


class ErrorType(Enum):
    """Enumeration of possible error types."""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    RATE_LIMIT_ERROR = "RATE_LIMIT_ERROR"
    CLIENT_ERROR = "CLIENT_ERROR"
    SERVER_ERROR = "SERVER_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


@dataclass
class EmailData:
    """Data structure for email information."""
    to: Union[str, List[str]]
    from_email: str  # 'from' is a Python keyword
    subject: str
    text: Optional[str] = None
    html: Optional[str] = None
    cc: Optional[Union[str, List[str]]] = None
    bcc: Optional[Union[str, List[str]]] = None
    scheduled_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate email data after initialization."""
        if not self.text and not self.html:
            raise ValueError("Either text or html content is required")


@dataclass
class APIResponse:
    """Standard API response structure."""
    success: bool
    request_id: str
    timestamp: datetime
    duration: int  # milliseconds
    error: Optional[str] = None
    error_type: Optional[str] = None
    suggestion: Optional[str] = None
    status_code: Optional[int] = None
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    endpoint: Optional[str] = None

    @classmethod
    def success_response(
        cls,
        data: Dict[str, Any],
        message: str,
        request_id: str,
        duration: int,
        timestamp: Optional[datetime] = None
    ) -> 'APIResponse':
        """Create a successful API response."""
        return cls(
            success=True,
            data=data,
            message=message,
            request_id=request_id,
            duration=duration,
            timestamp=timestamp or datetime.now()
        )

    @classmethod
    def error_response(
        cls,
        error: str,
        error_type: str,
        request_id: str,
        duration: int,
        status_code: Optional[int] = None,
        suggestion: Optional[str] = None,
        endpoint: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ) -> 'APIResponse':
        """Create an error API response."""
        return cls(
            success=False,
            error=error,
            error_type=error_type,
            status_code=status_code,
            suggestion=suggestion,
            request_id=request_id,
            duration=duration,
            endpoint=endpoint,
            timestamp=timestamp or datetime.now()
        )


class EmailPayload(TypedDict, total=False):
    """Type definition for email API payload."""
    to: Union[str, List[str]]
    subject: str
    text: Optional[str]
    html: Optional[str]
    cc: Optional[Union[str, List[str]]]
    bcc: Optional[Union[str, List[str]]]
    scheduled_at: Optional[str]

# Note: 'from' field will be added dynamically as it's a Python keyword


@dataclass
class ClientConfig:
    """Configuration for MailBlock client."""
    api_key: str
    base_url: str = "https://sdk-backend-production-20e1.up.railway.app"
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    debug: bool = False
    logger: Optional[Any] = None

    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.api_key or not self.api_key.strip():
            raise ValueError("API key must be a non-empty string")
        self.api_key = self.api_key.strip()


@dataclass
class CancelEmailResponse:
    """Response structure for email cancellation."""
    email_id: Union[str, int]
    previous_status: str
    current_status: str
    message: str


@dataclass
class BulkCancelResponse:
    """Response structure for bulk email cancellation."""
    success_count: int
    error_count: int
    total_count: int
    message: str
    results: List[Dict[str, Any]]


@dataclass
class UpdateEmailData:
    """Data structure for updating scheduled emails."""
    subject: Optional[str] = None
    body_html: Optional[str] = None
    body_text: Optional[str] = None
    scheduled_at: Optional[Union[datetime, str, None]] = None


@dataclass
class UpdateEmailResponse:
    """Response structure for email update operations."""
    message: str
    email: Dict[str, Any]
    tracking_updated: bool
    job_rescheduled: bool


# Type aliases for commonly used types
EmailAddress = Union[str, List[str]]
HTMLContent = str
TextContent = str
Timestamp = Union[datetime, str]
EmailId = Union[str, int]
EmailIds = List[Union[str, int]]