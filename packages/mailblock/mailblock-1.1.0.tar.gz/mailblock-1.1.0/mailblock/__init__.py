"""
MailBlock Python SDK

Official Python SDK for the MailBlock email service.
Provides a clean, Pythonic interface for sending emails with comprehensive
error handling, logging, and validation.

Basic Usage:
    ```python
    from mailblock import MailBlock
    
    # Initialize client
    client = MailBlock("your-api-key")
    
    # Send email using builder pattern
    response = client.email() \
        .to("recipient@example.com") \
        .from_email("sender@example.com") \
        .subject("Hello World") \
        .text("This is a test email") \
        .send_sync()
    
    if response.success:
        print(f"Email sent! ID: {response.data['id']}")
    else:
        print(f"Error: {response.error}")
    ```

Advanced Usage:
    ```python
    import asyncio
    from datetime import datetime, timedelta
    from mailblock import MailBlock
    
    async def send_scheduled_email():
        client = MailBlock("your-api-key", debug=True)
        
        # Schedule email for tomorrow
        tomorrow = datetime.now() + timedelta(days=1)
        
        response = await client.email() \
            .to("user@example.com") \
            .from_email("noreply@yourapp.com") \
            .subject("Scheduled Newsletter") \
            .html("<h1>Hello!</h1><p>This is scheduled content.</p>") \
            .schedule_at(tomorrow) \
            .send()
        
        return response
    
    # Run async example
    response = asyncio.run(send_scheduled_email())
    ```
"""

from .client import MailBlock
from .email_builder import EmailBuilder
from .exceptions import (
    MailBlockError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    RateLimitError,
    ServerError,
    NetworkError,
    TimeoutError,
)
from .types import EmailData, APIResponse, ClientConfig, UpdateEmailData, CancelEmailResponse, BulkCancelResponse, UpdateEmailResponse

# Version information
__version__ = "1.1.0"
__author__ = "MailBlock Team"
__email__ = "support@mailblock.com"
__license__ = "MIT"

# Public API
__all__ = [
    # Main classes
    "MailBlock",
    "EmailBuilder",
    
    # Data types
    "EmailData",
    "APIResponse",
    "ClientConfig",
    "UpdateEmailData",
    "CancelEmailResponse", 
    "BulkCancelResponse",
    "UpdateEmailResponse",
    
    # Exceptions
    "MailBlockError",
    "ValidationError",
    "AuthenticationError",
    "AuthorizationError",
    "RateLimitError",
    "ServerError",
    "NetworkError",
    "TimeoutError",
    
    # Version info
    "__version__",
]

# Module-level convenience function
def create_client(
    api_key: str,
    base_url: str = "https://sdk-backend-production-20e1.up.railway.app",
    **kwargs
) -> MailBlock:
    """
    Create a MailBlock client instance.
    
    Convenience function for creating a client with common settings.
    
    Args:
        api_key: Your MailBlock API key
        base_url: API base URL (optional)
        **kwargs: Additional client configuration options
        
    Returns:
        Configured MailBlock client instance
        
    Example:
        ```python
        import mailblock
        
        client = mailblock.create_client("your-api-key", debug=True)
        ```
    """
    return MailBlock(api_key, base_url=base_url, **kwargs)


# Backward compatibility aliases
Client = MailBlock  # Alternative name for the main client class