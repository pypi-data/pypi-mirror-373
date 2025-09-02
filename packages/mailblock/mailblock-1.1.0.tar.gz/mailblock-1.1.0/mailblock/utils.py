"""
MailBlock SDK Utilities

This module provides utility functions used throughout the SDK.
"""

import re
import random
import string
import logging
from datetime import datetime
from typing import Optional, Dict, Any, Tuple, Union, List
from .exceptions import ValidationError, MailBlockError


def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email is valid, False otherwise
    """
    if not email or not isinstance(email, str):
        return False
    
    # More comprehensive email regex
    email_pattern = re.compile(
        r'^[a-zA-Z0-9.!#$%&\'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
    )
    return email_pattern.match(email.strip()) is not None


def generate_request_id() -> str:
    """
    Generate a unique request ID for tracking.
    
    Returns:
        Unique request ID string
    """
    random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
    timestamp_part = str(int(datetime.now().timestamp() * 1000))[-8:]  # Last 8 digits
    return f"req_{random_part}{timestamp_part}"


def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize and validate string input.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
        
    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(value, str):
        raise ValidationError("Value must be a string")
    
    cleaned = value.strip()
    if not cleaned:
        raise ValidationError("Value cannot be empty")
    
    if max_length and len(cleaned) > max_length:
        raise ValidationError(f"Value exceeds maximum length of {max_length} characters")
    
    return cleaned


def validate_future_date(date_value: datetime) -> datetime:
    """
    Validate that a date is in the future.
    
    Args:
        date_value: Date to validate
        
    Returns:
        Validated date
        
    Raises:
        ValidationError: If date is not in the future
    """
    if not isinstance(date_value, datetime):
        raise ValidationError("Date must be a datetime object")
    
    if date_value <= datetime.now():
        raise ValidationError("Scheduled date must be in the future")
    
    return date_value


def parse_date_string(date_string: str) -> datetime:
    """
    Parse date string into datetime object.
    
    Args:
        date_string: Date string to parse
        
    Returns:
        Parsed datetime object
        
    Raises:
        ValidationError: If parsing fails
    """
    try:
        # Try ISO format first
        return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
    except ValueError:
        try:
            # Try common formats
            formats = [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d %H:%M",
                "%Y-%m-%d",
                "%m/%d/%Y %H:%M:%S",
                "%m/%d/%Y",
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_string, fmt)
                except ValueError:
                    continue
                    
            raise ValueError("No matching format found")
            
        except ValueError as e:
            raise ValidationError(f"Invalid date format: {date_string}") from e


def categorize_http_error(status_code: int) -> str:
    """
    Categorize HTTP status codes into error types.
    
    Args:
        status_code: HTTP status code
        
    Returns:
        Error type string
    """
    if status_code == 400:
        return "VALIDATION_ERROR"
    elif status_code == 401:
        return "AUTHENTICATION_ERROR"
    elif status_code == 403:
        return "AUTHORIZATION_ERROR"
    elif status_code == 404:
        return "CLIENT_ERROR"
    elif status_code == 429:
        return "RATE_LIMIT_ERROR"
    elif 400 <= status_code < 500:
        return "CLIENT_ERROR"
    elif 500 <= status_code < 600:
        return "SERVER_ERROR"
    else:
        return "UNKNOWN_ERROR"


def get_error_suggestion(status_code: int) -> str:
    """
    Get helpful suggestion based on HTTP status code.
    
    Args:
        status_code: HTTP status code
        
    Returns:
        Helpful error suggestion
    """
    suggestions = {
        400: "Check your request parameters and try again",
        401: "Verify your API key is correct and has proper permissions",
        403: "Your API key may not have permission for this operation",
        404: "The API endpoint was not found. Check the base URL",
        429: "You are being rate limited. Wait a moment and try again",
        500: "Server error occurred. Try again in a few moments",
        502: "Bad Gateway. The server is temporarily unavailable",
        503: "Service temporarily unavailable. Please try again later",
        504: "Gateway timeout. The request took too long to process",
    }
    
    return suggestions.get(
        status_code, 
        "Please try again or contact support if the issue persists"
    )


def setup_logger(name: str, debug: bool = False) -> logging.Logger:
    """
    Set up a logger for the SDK.
    
    Args:
        name: Logger name
        debug: Enable debug logging
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '[%(asctime)s] %(name)s %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    logger.propagate = False
    
    return logger


def redact_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Redact sensitive information from data for logging.
    
    Args:
        data: Data dictionary
        
    Returns:
        Dictionary with sensitive data redacted
    """
    redacted = data.copy()
    sensitive_keys = ['text', 'html', 'api_key', 'authorization']
    
    for key in sensitive_keys:
        if key in redacted and redacted[key]:
            redacted[key] = "[REDACTED]"
    
    return redacted


def calculate_retry_delay(attempt: int, base_delay: float = 1.0) -> float:
    """
    Calculate exponential backoff delay for retries.
    
    Args:
        attempt: Current attempt number (starting from 1)
        base_delay: Base delay in seconds
        
    Returns:
        Delay in seconds
    """
    # Exponential backoff with jitter
    delay = base_delay * (2 ** (attempt - 1))
    jitter = random.uniform(0.1, 0.5)
    return delay + jitter


def validate_email_or_array(emails: Union[str, List[str]], field_name: str) -> Union[str, List[str]]:
    """
    Validate single email address or array of email addresses.
    
    Args:
        emails: Single email string or list of email strings
        field_name: Name of the field for error messages
        
    Returns:
        Validated email(s)
        
    Raises:
        ValidationError: If validation fails
    """
    if isinstance(emails, str):
        if not validate_email(emails):
            raise ValidationError(f"Invalid {field_name} email address: {emails}")
        return emails
    elif isinstance(emails, list):
        if len(emails) == 0:
            raise ValidationError(f"{field_name} array cannot be empty")
        
        validated_emails = []
        for email in emails:
            if not isinstance(email, str):
                raise ValidationError(f"All {field_name} email addresses must be strings")
            if not validate_email(email):
                raise ValidationError(f"Invalid {field_name} email address: {email}")
            validated_emails.append(email)
        return validated_emails
    else:
        raise ValidationError(f"{field_name} must be a string or array of strings")


def validate_email_fields(
    to: Union[str, List[str]], 
    from_email: str,
    cc: Optional[Union[str, List[str]]] = None,
    bcc: Optional[Union[str, List[str]]] = None
) -> None:
    """
    Validate all email fields in an email data structure.
    
    Args:
        to: Recipient email(s)
        from_email: Sender email
        cc: CC email(s) (optional)
        bcc: BCC email(s) (optional)
        
    Raises:
        ValidationError: If any email validation fails
    """
    # Validate 'to' field
    validate_email_or_array(to, 'recipient')
    
    # Validate 'from' field (always single email)
    if not validate_email(from_email):
        raise ValidationError(f"Invalid sender email address: {from_email}")
    
    # Validate 'cc' field if provided
    if cc is not None:
        validate_email_or_array(cc, 'cc')
    
    # Validate 'bcc' field if provided
    if bcc is not None:
        validate_email_or_array(bcc, 'bcc')


def validate_email_id(email_id: Union[str, int]) -> Union[str, int]:
    """
    Validate email ID format.
    
    Args:
        email_id: Email ID to validate
        
    Returns:
        Validated email ID
        
    Raises:
        ValidationError: If email ID is invalid
    """
    if not email_id:
        raise ValidationError("Email ID is required")
    
    if not isinstance(email_id, (str, int)):
        raise ValidationError("Email ID must be a string or number")
        
    return email_id


def validate_email_ids(email_ids: List[Union[str, int]]) -> List[Union[str, int]]:
    """
    Validate array of email IDs.
    
    Args:
        email_ids: List of email IDs to validate
        
    Returns:
        Validated email IDs list
        
    Raises:
        ValidationError: If validation fails
    """
    if not email_ids:
        raise ValidationError("Email IDs array is required")
    
    if not isinstance(email_ids, list):
        raise ValidationError("Email IDs must be an array")
    
    if len(email_ids) == 0:
        raise ValidationError("Email IDs array cannot be empty")
    
    validated_ids = []
    for email_id in email_ids:
        validated_ids.append(validate_email_id(email_id))
    
    return validated_ids