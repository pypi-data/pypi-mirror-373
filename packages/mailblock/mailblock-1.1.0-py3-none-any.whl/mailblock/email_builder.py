"""
MailBlock Email Builder

This module provides the EmailBuilder class for constructing emails with a fluent interface.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional, Union, List
from .exceptions import ValidationError
from .utils import validate_email_or_array, sanitize_string, validate_future_date, parse_date_string
from .types import EmailData, APIResponse

if TYPE_CHECKING:
    from .client import MailBlock


class EmailBuilder:
    """
    Fluent interface for building emails.
    
    This class implements the Builder pattern to provide a clean, chainable
    interface for constructing email messages.
    """
    
    def __init__(self, client: 'MailBlock'):
        """
        Initialize EmailBuilder.
        
        Args:
            client: MailBlock client instance
        """
        self._client = client
        self._to: Optional[Union[str, List[str]]] = None
        self._from: Optional[str] = None
        self._subject: Optional[str] = None
        self._text: Optional[str] = None
        self._html: Optional[str] = None
        self._cc: Optional[Union[str, List[str]]] = None
        self._bcc: Optional[Union[str, List[str]]] = None
        self._scheduled_at: Optional[datetime] = None

    def to(self, emails: Union[str, List[str]]) -> 'EmailBuilder':
        """
        Set the recipient email address(es).
        
        Args:
            emails: Single recipient email address or list of email addresses
            
        Returns:
            EmailBuilder instance for chaining
            
        Raises:
            ValidationError: If email format is invalid
        """
        self._to = validate_email_or_array(emails, 'recipient')
        return self

    def from_email(self, email: str) -> 'EmailBuilder':
        """
        Set the sender email address.
        
        Note: Method named 'from_email' since 'from' is a Python keyword.
        
        Args:
            email: Sender email address
            
        Returns:
            EmailBuilder instance for chaining
            
        Raises:
            ValidationError: If email format is invalid
        """
        if not email or not isinstance(email, str):
            raise ValidationError("Sender email address must be a non-empty string")
        
        email = email.strip()
        # Use the original validate_email for single sender
        from .utils import validate_email
        if not validate_email(email):
            raise ValidationError(f"Invalid sender email address: {email}")
        
        self._from = email
        return self

    def subject(self, subject: str) -> 'EmailBuilder':
        """
        Set the email subject.
        
        Args:
            subject: Email subject line
            
        Returns:
            EmailBuilder instance for chaining
            
        Raises:
            ValidationError: If subject is invalid
        """
        try:
            self._subject = sanitize_string(subject, max_length=998)  # RFC 5322 limit
        except ValidationError as e:
            raise ValidationError(f"Invalid subject: {e.message}") from e
        
        return self

    def text(self, content: str) -> 'EmailBuilder':
        """
        Set the plain text content.
        
        Args:
            content: Plain text email content
            
        Returns:
            EmailBuilder instance for chaining
            
        Raises:
            ValidationError: If content is invalid
        """
        if not content or not isinstance(content, str):
            raise ValidationError("Text content must be a non-empty string")
        
        self._text = content.strip()
        if not self._text:
            raise ValidationError("Text content cannot be empty after trimming")
        
        return self

    def html(self, content: str) -> 'EmailBuilder':
        """
        Set the HTML content.
        
        Args:
            content: HTML email content
            
        Returns:
            EmailBuilder instance for chaining
            
        Raises:
            ValidationError: If content is invalid
        """
        if not content or not isinstance(content, str):
            raise ValidationError("HTML content must be a non-empty string")
        
        self._html = content.strip()
        if not self._html:
            raise ValidationError("HTML content cannot be empty after trimming")
        
        return self

    def schedule_at(self, date: Union[datetime, str]) -> 'EmailBuilder':
        """
        Schedule the email for future delivery.
        
        Args:
            date: Schedule date as datetime object or ISO string
            
        Returns:
            EmailBuilder instance for chaining
            
        Raises:
            ValidationError: If date is invalid or not in the future
        """
        if isinstance(date, datetime):
            scheduled_date = validate_future_date(date)
        elif isinstance(date, str):
            parsed_date = parse_date_string(date)
            scheduled_date = validate_future_date(parsed_date)
        else:
            raise ValidationError(
                "Scheduled date must be a datetime object or valid date string"
            )
        
        self._scheduled_at = scheduled_date
        return self

    def cc(self, emails: Optional[Union[str, List[str]]]) -> 'EmailBuilder':
        """
        Set the CC (carbon copy) email address(es).
        
        Args:
            emails: Single CC email address, list of email addresses, or None
            
        Returns:
            EmailBuilder instance for chaining
            
        Raises:
            ValidationError: If email format is invalid
        """
        if emails is not None:
            self._cc = validate_email_or_array(emails, 'cc')
        else:
            self._cc = None
        return self

    def bcc(self, emails: Optional[Union[str, List[str]]]) -> 'EmailBuilder':
        """
        Set the BCC (blind carbon copy) email address(es).
        
        Args:
            emails: Single BCC email address, list of email addresses, or None
            
        Returns:
            EmailBuilder instance for chaining
            
        Raises:
            ValidationError: If email format is invalid
        """
        if emails is not None:
            self._bcc = validate_email_or_array(emails, 'bcc')
        else:
            self._bcc = None
        return self

    def build(self) -> EmailData:
        """
        Build and validate the email data.
        
        Returns:
            EmailData object with validated email information
            
        Raises:
            ValidationError: If required fields are missing or invalid
        """
        # Validate required fields
        if not self._to:
            raise ValidationError("Recipient email address (to) is required")
        
        if not self._from:
            raise ValidationError("Sender email address (from) is required")
        
        if not self._subject:
            raise ValidationError("Email subject is required")
        
        if not self._text and not self._html:
            raise ValidationError("Either text or HTML content is required")
        
        return EmailData(
            to=self._to,
            from_email=self._from,
            subject=self._subject,
            text=self._text,
            html=self._html,
            cc=self._cc,
            bcc=self._bcc,
            scheduled_at=self._scheduled_at
        )

    async def send(self) -> APIResponse:
        """
        Build and send the email.
        
        Returns:
            APIResponse with the result of the send operation
            
        Raises:
            ValidationError: If email data is invalid
            MailBlockError: If sending fails
        """
        email_data = self.build()
        return await self._client.send_email(email_data)

    def send_sync(self) -> APIResponse:
        """
        Build and send the email synchronously.
        
        Returns:
            APIResponse with the result of the send operation
            
        Raises:
            ValidationError: If email data is invalid
            MailBlockError: If sending fails
        """
        email_data = self.build()
        return self._client.send_email_sync(email_data)

    def __repr__(self) -> str:
        """String representation of EmailBuilder."""
        parts = []
        if self._to:
            to_preview = str(self._to) if isinstance(self._to, str) else f"{len(self._to)} recipients"
            parts.append(f"to={to_preview}")
        if self._from:
            parts.append(f"from={self._from}")
        if self._cc:
            cc_preview = str(self._cc) if isinstance(self._cc, str) else f"{len(self._cc)} cc"
            parts.append(f"cc={cc_preview}")
        if self._bcc:
            bcc_preview = str(self._bcc) if isinstance(self._bcc, str) else f"{len(self._bcc)} bcc"
            parts.append(f"bcc={bcc_preview}")
        if self._subject:
            subject_preview = self._subject[:30] + "..." if len(self._subject) > 30 else self._subject
            parts.append(f"subject='{subject_preview}'")
        if self._scheduled_at:
            parts.append(f"scheduled_at={self._scheduled_at.isoformat()}")
        
        return f"EmailBuilder({', '.join(parts)})"