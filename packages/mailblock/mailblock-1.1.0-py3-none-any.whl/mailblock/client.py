"""
MailBlock Python SDK Client

This module provides the main MailBlock client class for sending emails.
"""

import time
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, Union
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from .email_builder import EmailBuilder
from .exceptions import (
    MailBlockError, ValidationError, AuthenticationError, 
    AuthorizationError, RateLimitError, ServerError, 
    NetworkError, TimeoutError
)
from .types import EmailData, APIResponse, ClientConfig, UpdateEmailData, EmailId, EmailIds
from .utils import (
    generate_request_id, categorize_http_error, get_error_suggestion,
    setup_logger, redact_sensitive_data, calculate_retry_delay,
    validate_email_id, validate_email_ids, parse_date_string
)


class MailBlock:
    """
    MailBlock Python SDK Client
    
    Main client class for interacting with the MailBlock API.
    Provides methods for sending emails with comprehensive error handling,
    logging, and retry mechanisms.
    """
    
    def __init__(
        self, 
        api_key: str,
        base_url: str = "https://sdk-backend-production-20e1.up.railway.app",
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        debug: bool = False,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize MailBlock client.
        
        Args:
            api_key: Your MailBlock API key
            base_url: API base URL
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Base delay between retries in seconds
            debug: Enable debug logging
            logger: Custom logger instance
            
        Raises:
            ValidationError: If API key is invalid
        """
        self.config = ClientConfig(
            api_key=api_key,
            base_url=base_url.rstrip('/'),
            timeout=timeout,
            max_retries=max_retries,
            retry_delay=retry_delay,
            debug=debug,
            logger=logger
        )
        
        self.logger = logger or setup_logger("mailblock", debug)
        self._setup_session()
    
    def _setup_session(self) -> None:
        """Set up requests session with retry strategy."""
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=self.config.retry_delay,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.session.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}",
            "User-Agent": "MailBlock-Python-SDK/1.0.0"
        })

    def _log(self, level: str, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Internal logging method.
        
        Args:
            level: Log level (info, debug, error, warning)
            message: Log message
            data: Additional data to log
        """
        if not self.config.debug and level == 'debug':
            return
        
        log_method = getattr(self.logger, level, self.logger.info)
        
        if data:
            # Redact sensitive information
            safe_data = redact_sensitive_data(data)
            log_method(f"{message} - {safe_data}")
        else:
            log_method(message)

    def email(self) -> EmailBuilder:
        """
        Create a new email builder instance.
        
        Returns:
            EmailBuilder instance for fluent email construction
        """
        return EmailBuilder(self)

    def send_email_sync(self, email_data: EmailData) -> APIResponse:
        """
        Send an email synchronously.
        
        Args:
            email_data: Email data to send
            
        Returns:
            APIResponse with the result
            
        Raises:
            MailBlockError: If sending fails
        """
        request_id = generate_request_id()
        start_time = time.time()
        timestamp = datetime.now()

        self._log('info', 'Initiating email send request', {
            'request_id': request_id,
            'to': email_data.to,
            'from': email_data.from_email,
            'subject': email_data.subject[:50] + '...' if len(email_data.subject) > 50 else email_data.subject,
            'scheduled': email_data.scheduled_at is not None
        })

        try:
            # Prepare payload
            payload = self._prepare_payload(email_data)
            endpoint = f"{self.config.base_url}/v1/send-email"
            
            self._log('debug', 'Sending API request', {
                'request_id': request_id,
                'endpoint': endpoint,
                'payload': redact_sensitive_data(payload)
            })

            # Make the request
            response = self.session.post(
                endpoint,
                json=payload,
                timeout=self.config.timeout,
                headers={"X-Request-ID": request_id}
            )
            
            duration = int((time.time() - start_time) * 1000)  # Convert to milliseconds
            
            self._log('debug', 'API response received', {
                'request_id': request_id,
                'status_code': response.status_code,
                'duration': f"{duration}ms",
                'success': response.ok
            })

            # Handle response
            if response.ok:
                result = response.json()
                
                self._log('info', f"Email {'scheduled' if email_data.scheduled_at else 'sent'} successfully", {
                    'request_id': request_id,
                    'duration': f"{duration}ms",
                    'email_id': result.get('id')
                })

                return APIResponse.success_response(
                    data=result,
                    message="Email scheduled successfully" if email_data.scheduled_at else "Email sent successfully",
                    request_id=request_id,
                    duration=duration,
                    timestamp=timestamp
                )
            else:
                return self._handle_error_response(response, request_id, duration, timestamp, endpoint)

        except requests.exceptions.Timeout as e:
            duration = int((time.time() - start_time) * 1000)
            self._log('error', 'Request timed out', {
                'request_id': request_id,
                'timeout': self.config.timeout,
                'duration': f"{duration}ms"
            })
            
            raise TimeoutError(
                f"Request timed out after {self.config.timeout} seconds",
                request_id=request_id
            ) from e

        except requests.exceptions.ConnectionError as e:
            duration = int((time.time() - start_time) * 1000)
            self._log('error', 'Connection error occurred', {
                'request_id': request_id,
                'error': str(e),
                'duration': f"{duration}ms"
            })
            
            raise NetworkError(
                f"Failed to connect to MailBlock API: {str(e)}",
                request_id=request_id
            ) from e

        except requests.exceptions.RequestException as e:
            duration = int((time.time() - start_time) * 1000)
            self._log('error', 'Request failed with exception', {
                'request_id': request_id,
                'error': str(e),
                'duration': f"{duration}ms"
            })
            
            raise MailBlockError(
                f"Request failed: {str(e)}",
                error_type="REQUEST_ERROR",
                request_id=request_id
            ) from e

    async def send_email(self, email_data: EmailData) -> APIResponse:
        """
        Send an email asynchronously.
        
        Note: This method requires aiohttp to be installed.
        
        Args:
            email_data: Email data to send
            
        Returns:
            APIResponse with the result
            
        Raises:
            MailBlockError: If sending fails
            ImportError: If aiohttp is not installed
        """
        try:
            import aiohttp
            import asyncio
        except ImportError as e:
            raise ImportError(
                "aiohttp is required for async operations. Install with: pip install aiohttp"
            ) from e

        request_id = generate_request_id()
        start_time = time.time()
        timestamp = datetime.now()

        self._log('info', 'Initiating async email send request', {
            'request_id': request_id,
            'to': email_data.to,
            'from': email_data.from_email,
            'subject': email_data.subject[:50] + '...' if len(email_data.subject) > 50 else email_data.subject
        })

        try:
            payload = self._prepare_payload(email_data)
            endpoint = f"{self.config.base_url}/v1/send-email"
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.config.api_key}",
                "X-Request-ID": request_id,
                "User-Agent": "MailBlock-Python-SDK/1.0.0"
            }

            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(endpoint, json=payload, headers=headers) as response:
                    duration = int((time.time() - start_time) * 1000)
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        self._log('info', f"Email {'scheduled' if email_data.scheduled_at else 'sent'} successfully", {
                            'request_id': request_id,
                            'duration': f"{duration}ms",
                            'email_id': result.get('id')
                        })

                        return APIResponse.success_response(
                            data=result,
                            message="Email scheduled successfully" if email_data.scheduled_at else "Email sent successfully",
                            request_id=request_id,
                            duration=duration,
                            timestamp=timestamp
                        )
                    else:
                        error_data = await response.json() if response.content_type == 'application/json' else {}
                        return self._create_error_response_from_async(
                            response.status, error_data, request_id, duration, timestamp, endpoint
                        )

        except asyncio.TimeoutError as e:
            duration = int((time.time() - start_time) * 1000)
            raise TimeoutError(
                f"Async request timed out after {self.config.timeout} seconds",
                request_id=request_id
            ) from e

        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            self._log('error', 'Async request failed', {
                'request_id': request_id,
                'error': str(e),
                'duration': f"{duration}ms"
            })
            
            raise MailBlockError(
                f"Async request failed: {str(e)}",
                error_type="ASYNC_ERROR",
                request_id=request_id
            ) from e

    def _prepare_payload(self, email_data: EmailData) -> Dict[str, Any]:
        """
        Prepare email payload for API request.
        
        Args:
            email_data: Email data to convert
            
        Returns:
            Dictionary payload for API request
        """
        payload = {
            "to": email_data.to,
            "from": email_data.from_email,  # 'from' is valid in dict keys
            "subject": email_data.subject
        }
        
        if email_data.text:
            payload["text"] = email_data.text
        
        if email_data.html:
            payload["html"] = email_data.html
        
        if email_data.cc:
            payload["cc"] = email_data.cc
        
        if email_data.bcc:
            payload["bcc"] = email_data.bcc
        
        if email_data.scheduled_at:
            payload["scheduled_at"] = email_data.scheduled_at.isoformat()
        
        return payload

    def _handle_error_response(
        self, 
        response: requests.Response, 
        request_id: str, 
        duration: int, 
        timestamp: datetime,
        endpoint: str
    ) -> APIResponse:
        """Handle error response from API."""
        try:
            error_data = response.json()
            error_message = error_data.get('error', f'HTTP error! status: {response.status_code}')
        except (json.JSONDecodeError, ValueError):
            error_message = f'HTTP error! status: {response.status_code}'

        error_type = categorize_http_error(response.status_code)
        suggestion = get_error_suggestion(response.status_code)

        self._log('error', 'API request failed', {
            'request_id': request_id,
            'error': error_message,
            'status_code': response.status_code,
            'error_type': error_type,
            'suggestion': suggestion
        })

        # Raise appropriate exception
        if response.status_code == 401:
            raise AuthenticationError(error_message, request_id=request_id)
        elif response.status_code == 403:
            raise AuthorizationError(error_message, request_id=request_id)
        elif response.status_code == 429:
            raise RateLimitError(error_message, request_id=request_id)
        elif 500 <= response.status_code < 600:
            raise ServerError(error_message, status_code=response.status_code, request_id=request_id)

        return APIResponse.error_response(
            error=error_message,
            error_type=error_type,
            suggestion=suggestion,
            status_code=response.status_code,
            request_id=request_id,
            duration=duration,
            endpoint=endpoint,
            timestamp=timestamp
        )

    def _create_error_response_from_async(
        self,
        status_code: int,
        error_data: Dict[str, Any],
        request_id: str,
        duration: int,
        timestamp: datetime,
        endpoint: str
    ) -> APIResponse:
        """Create error response from async request."""
        error_message = error_data.get('error', f'HTTP error! status: {status_code}')
        error_type = categorize_http_error(status_code)
        suggestion = get_error_suggestion(status_code)

        self._log('error', 'Async API request failed', {
            'request_id': request_id,
            'error': error_message,
            'status_code': status_code,
            'error_type': error_type
        })

        return APIResponse.error_response(
            error=error_message,
            error_type=error_type,
            suggestion=suggestion,
            status_code=status_code,
            request_id=request_id,
            duration=duration,
            endpoint=endpoint,
            timestamp=timestamp
        )

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if hasattr(self, 'session'):
            self.session.close()

    def cancel_email_sync(self, email_id: EmailId) -> APIResponse:
        """
        Cancel a scheduled email synchronously.
        
        Args:
            email_id: ID of the email to cancel
            
        Returns:
            APIResponse with the result
            
        Raises:
            ValidationError: If email_id is invalid
            MailBlockError: If cancellation fails
        """
        validate_email_id(email_id)
        
        request_id = generate_request_id()
        start_time = time.time()
        timestamp = datetime.now()
        
        self._log('info', 'Initiating email cancellation request', {
            'request_id': request_id,
            'email_id': email_id
        })
        
        try:
            endpoint = f"{self.config.base_url}/v1/cancel-email/{email_id}"
            
            self._log('debug', 'Sending cancellation API request', {
                'request_id': request_id,
                'endpoint': endpoint,
                'email_id': email_id
            })
            
            response = self.session.post(
                endpoint,
                timeout=self.config.timeout,
                headers={"X-Request-ID": request_id}
            )
            
            duration = int((time.time() - start_time) * 1000)
            
            self._log('debug', 'Cancellation API response received', {
                'request_id': request_id,
                'status_code': response.status_code,
                'duration': f"{duration}ms",
                'success': response.ok
            })
            
            if response.ok:
                result = response.json()
                
                self._log('info', 'Email cancelled successfully', {
                    'request_id': request_id,
                    'duration': f"{duration}ms",
                    'email_id': result.get('email_id'),
                    'previous_status': result.get('previous_status'),
                    'current_status': result.get('current_status')
                })
                
                return APIResponse.success_response(
                    data=result,
                    message="Email cancelled successfully",
                    request_id=request_id,
                    duration=duration,
                    timestamp=timestamp
                )
            else:
                return self._handle_error_response(response, request_id, duration, timestamp, endpoint)
                
        except requests.exceptions.Timeout as e:
            duration = int((time.time() - start_time) * 1000)
            raise TimeoutError(
                f"Cancellation request timed out after {self.config.timeout} seconds",
                request_id=request_id
            ) from e
            
        except requests.exceptions.ConnectionError as e:
            duration = int((time.time() - start_time) * 1000)
            raise NetworkError(
                f"Failed to connect to MailBlock API: {str(e)}",
                request_id=request_id
            ) from e
            
        except requests.exceptions.RequestException as e:
            duration = int((time.time() - start_time) * 1000)
            raise MailBlockError(
                f"Cancellation request failed: {str(e)}",
                error_type="REQUEST_ERROR",
                request_id=request_id
            ) from e
    
    async def cancel_email(self, email_id: EmailId) -> APIResponse:
        """
        Cancel a scheduled email asynchronously.
        
        Args:
            email_id: ID of the email to cancel
            
        Returns:
            APIResponse with the result
            
        Raises:
            ValidationError: If email_id is invalid
            MailBlockError: If cancellation fails
            ImportError: If aiohttp is not installed
        """
        try:
            import aiohttp
            import asyncio
        except ImportError as e:
            raise ImportError(
                "aiohttp is required for async operations. Install with: pip install aiohttp"
            ) from e
            
        validate_email_id(email_id)
        
        request_id = generate_request_id()
        start_time = time.time()
        timestamp = datetime.now()
        
        self._log('info', 'Initiating async email cancellation request', {
            'request_id': request_id,
            'email_id': email_id
        })
        
        try:
            endpoint = f"{self.config.base_url}/v1/cancel-email/{email_id}"
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.config.api_key}",
                "X-Request-ID": request_id,
                "User-Agent": "MailBlock-Python-SDK/1.0.0"
            }
            
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(endpoint, headers=headers) as response:
                    duration = int((time.time() - start_time) * 1000)
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        self._log('info', 'Email cancelled successfully', {
                            'request_id': request_id,
                            'duration': f"{duration}ms",
                            'email_id': result.get('email_id')
                        })
                        
                        return APIResponse.success_response(
                            data=result,
                            message="Email cancelled successfully",
                            request_id=request_id,
                            duration=duration,
                            timestamp=timestamp
                        )
                    else:
                        error_data = await response.json() if response.content_type == 'application/json' else {}
                        return self._create_error_response_from_async(
                            response.status, error_data, request_id, duration, timestamp, endpoint
                        )
                        
        except asyncio.TimeoutError as e:
            duration = int((time.time() - start_time) * 1000)
            raise TimeoutError(
                f"Async cancellation request timed out after {self.config.timeout} seconds",
                request_id=request_id
            ) from e
            
        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            self._log('error', 'Async cancellation request failed', {
                'request_id': request_id,
                'error': str(e),
                'duration': f"{duration}ms"
            })
            
            raise MailBlockError(
                f"Async cancellation request failed: {str(e)}",
                error_type="ASYNC_ERROR",
                request_id=request_id
            ) from e
    
    def cancel_emails_sync(self, email_ids: EmailIds) -> APIResponse:
        """
        Cancel multiple scheduled emails synchronously.
        
        Args:
            email_ids: List of email IDs to cancel
            
        Returns:
            APIResponse with the bulk cancellation result
            
        Raises:
            ValidationError: If email_ids are invalid
            MailBlockError: If cancellation fails
        """
        validate_email_ids(email_ids)
        
        request_id = generate_request_id()
        start_time = time.time()
        timestamp = datetime.now()
        
        self._log('info', 'Initiating bulk email cancellation request', {
            'request_id': request_id,
            'email_ids': email_ids,
            'count': len(email_ids)
        })
        
        try:
            payload = {'email_ids': email_ids}
            endpoint = f"{self.config.base_url}/v1/cancel-email"
            
            self._log('debug', 'Sending bulk cancellation API request', {
                'request_id': request_id,
                'endpoint': endpoint,
                'payload': payload
            })
            
            response = self.session.post(
                endpoint,
                json=payload,
                timeout=self.config.timeout,
                headers={"X-Request-ID": request_id}
            )
            
            duration = int((time.time() - start_time) * 1000)
            
            self._log('debug', 'Bulk cancellation API response received', {
                'request_id': request_id,
                'status_code': response.status_code,
                'duration': f"{duration}ms",
                'success': response.ok
            })
            
            if response.ok:
                result = response.json()
                
                self._log('info', 'Bulk email cancellation completed', {
                    'request_id': request_id,
                    'duration': f"{duration}ms",
                    'success_count': result.get('success_count'),
                    'error_count': result.get('error_count'),
                    'total_requested': len(email_ids)
                })
                
                message = result.get('message') or f"Cancelled {result.get('success_count', 0)} of {len(email_ids)} emails"
                
                return APIResponse.success_response(
                    data=result,
                    message=message,
                    request_id=request_id,
                    duration=duration,
                    timestamp=timestamp
                )
            else:
                return self._handle_error_response(response, request_id, duration, timestamp, endpoint)
                
        except requests.exceptions.Timeout as e:
            duration = int((time.time() - start_time) * 1000)
            raise TimeoutError(
                f"Bulk cancellation request timed out after {self.config.timeout} seconds",
                request_id=request_id
            ) from e
            
        except requests.exceptions.ConnectionError as e:
            duration = int((time.time() - start_time) * 1000)
            raise NetworkError(
                f"Failed to connect to MailBlock API: {str(e)}",
                request_id=request_id
            ) from e
            
        except requests.exceptions.RequestException as e:
            duration = int((time.time() - start_time) * 1000)
            raise MailBlockError(
                f"Bulk cancellation request failed: {str(e)}",
                error_type="REQUEST_ERROR",
                request_id=request_id
            ) from e
    
    async def cancel_emails(self, email_ids: EmailIds) -> APIResponse:
        """
        Cancel multiple scheduled emails asynchronously.
        
        Args:
            email_ids: List of email IDs to cancel
            
        Returns:
            APIResponse with the bulk cancellation result
            
        Raises:
            ValidationError: If email_ids are invalid
            MailBlockError: If cancellation fails
            ImportError: If aiohttp is not installed
        """
        try:
            import aiohttp
            import asyncio
        except ImportError as e:
            raise ImportError(
                "aiohttp is required for async operations. Install with: pip install aiohttp"
            ) from e
            
        validate_email_ids(email_ids)
        
        request_id = generate_request_id()
        start_time = time.time()
        timestamp = datetime.now()
        
        self._log('info', 'Initiating async bulk email cancellation request', {
            'request_id': request_id,
            'email_ids': email_ids,
            'count': len(email_ids)
        })
        
        try:
            payload = {'email_ids': email_ids}
            endpoint = f"{self.config.base_url}/v1/cancel-email"
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.config.api_key}",
                "X-Request-ID": request_id,
                "User-Agent": "MailBlock-Python-SDK/1.0.0"
            }
            
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(endpoint, json=payload, headers=headers) as response:
                    duration = int((time.time() - start_time) * 1000)
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        self._log('info', 'Bulk email cancellation completed', {
                            'request_id': request_id,
                            'duration': f"{duration}ms",
                            'success_count': result.get('success_count'),
                            'error_count': result.get('error_count')
                        })
                        
                        message = result.get('message') or f"Cancelled {result.get('success_count', 0)} of {len(email_ids)} emails"
                        
                        return APIResponse.success_response(
                            data=result,
                            message=message,
                            request_id=request_id,
                            duration=duration,
                            timestamp=timestamp
                        )
                    else:
                        error_data = await response.json() if response.content_type == 'application/json' else {}
                        return self._create_error_response_from_async(
                            response.status, error_data, request_id, duration, timestamp, endpoint
                        )
                        
        except asyncio.TimeoutError as e:
            duration = int((time.time() - start_time) * 1000)
            raise TimeoutError(
                f"Async bulk cancellation request timed out after {self.config.timeout} seconds",
                request_id=request_id
            ) from e
            
        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            self._log('error', 'Async bulk cancellation request failed', {
                'request_id': request_id,
                'error': str(e),
                'duration': f"{duration}ms"
            })
            
            raise MailBlockError(
                f"Async bulk cancellation request failed: {str(e)}",
                error_type="ASYNC_ERROR",
                request_id=request_id
            ) from e

    def update_scheduled_email_sync(self, email_id: EmailId, updates: UpdateEmailData) -> APIResponse:
        """
        Update a scheduled email synchronously.
        
        Args:
            email_id: ID of the email to update
            updates: UpdateEmailData object with fields to update
            
        Returns:
            APIResponse with the update result
            
        Raises:
            ValidationError: If parameters are invalid
            MailBlockError: If update fails
        """
        validate_email_id(email_id)
        
        request_id = generate_request_id()
        start_time = time.time()
        timestamp = datetime.now()
        
        self._log('info', 'Initiating scheduled email update request', {
            'request_id': request_id,
            'email_id': email_id,
            'updates': list(updates.__dict__.keys()) if hasattr(updates, '__dict__') else 'unknown'
        })
        
        # Prepare payload - only include fields that are not None
        payload = {}
        if updates.subject is not None:
            payload['subject'] = updates.subject
        if updates.body_html is not None:
            payload['body_html'] = updates.body_html
        if updates.body_text is not None:
            payload['body_text'] = updates.body_text
        if updates.scheduled_at is not None:
            if updates.scheduled_at is None:  # Explicit None to unschedule
                payload['scheduled_at'] = None
            elif isinstance(updates.scheduled_at, datetime):
                payload['scheduled_at'] = updates.scheduled_at.isoformat()
            elif isinstance(updates.scheduled_at, str):
                # Validate date string
                try:
                    parsed_date = parse_date_string(updates.scheduled_at)
                    payload['scheduled_at'] = updates.scheduled_at
                except ValidationError:
                    raise ValidationError("Invalid scheduled_at date format")
            else:
                raise ValidationError("scheduled_at must be a datetime object, valid date string, or None")
        
        if not payload:
            raise ValidationError("At least one field must be provided for update (subject, body_html, body_text, or scheduled_at)")
        
        try:
            endpoint = f"{self.config.base_url}/v1/update-scheduled-email/{email_id}"
            
            self._log('debug', 'Sending update API request', {
                'request_id': request_id,
                'endpoint': endpoint,
                'payload': redact_sensitive_data(payload)
            })
            
            response = self.session.put(
                endpoint,
                json=payload,
                timeout=self.config.timeout,
                headers={"X-Request-ID": request_id}
            )
            
            duration = int((time.time() - start_time) * 1000)
            
            self._log('debug', 'Update API response received', {
                'request_id': request_id,
                'status_code': response.status_code,
                'duration': f"{duration}ms",
                'success': response.ok
            })
            
            if response.ok:
                result = response.json()
                
                self._log('info', 'Scheduled email updated successfully', {
                    'request_id': request_id,
                    'duration': f"{duration}ms",
                    'email_id': result.get('email', {}).get('id'),
                    'status': result.get('email', {}).get('status'),
                    'tracking_updated': result.get('tracking_updated'),
                    'job_rescheduled': result.get('job_rescheduled')
                })
                
                return APIResponse.success_response(
                    data={
                        'message': result.get('message'),
                        'email': result.get('email'),
                        'tracking_updated': result.get('tracking_updated'),
                        'job_rescheduled': result.get('job_rescheduled')
                    },
                    message="Email updated successfully",
                    request_id=request_id,
                    duration=duration,
                    timestamp=timestamp
                )
            else:
                return self._handle_error_response(response, request_id, duration, timestamp, endpoint)
                
        except requests.exceptions.Timeout as e:
            duration = int((time.time() - start_time) * 1000)
            raise TimeoutError(
                f"Update request timed out after {self.config.timeout} seconds",
                request_id=request_id
            ) from e
            
        except requests.exceptions.ConnectionError as e:
            duration = int((time.time() - start_time) * 1000)
            raise NetworkError(
                f"Failed to connect to MailBlock API: {str(e)}",
                request_id=request_id
            ) from e
            
        except requests.exceptions.RequestException as e:
            duration = int((time.time() - start_time) * 1000)
            raise MailBlockError(
                f"Update request failed: {str(e)}",
                error_type="REQUEST_ERROR",
                request_id=request_id
            ) from e
    
    async def update_scheduled_email(self, email_id: EmailId, updates: UpdateEmailData) -> APIResponse:
        """
        Update a scheduled email asynchronously.
        
        Args:
            email_id: ID of the email to update
            updates: UpdateEmailData object with fields to update
            
        Returns:
            APIResponse with the update result
            
        Raises:
            ValidationError: If parameters are invalid
            MailBlockError: If update fails
            ImportError: If aiohttp is not installed
        """
        try:
            import aiohttp
            import asyncio
        except ImportError as e:
            raise ImportError(
                "aiohttp is required for async operations. Install with: pip install aiohttp"
            ) from e
            
        validate_email_id(email_id)
        
        request_id = generate_request_id()
        start_time = time.time()
        timestamp = datetime.now()
        
        self._log('info', 'Initiating async scheduled email update request', {
            'request_id': request_id,
            'email_id': email_id,
            'updates': list(updates.__dict__.keys()) if hasattr(updates, '__dict__') else 'unknown'
        })
        
        # Prepare payload - same logic as sync version
        payload = {}
        if updates.subject is not None:
            payload['subject'] = updates.subject
        if updates.body_html is not None:
            payload['body_html'] = updates.body_html
        if updates.body_text is not None:
            payload['body_text'] = updates.body_text
        if updates.scheduled_at is not None:
            if updates.scheduled_at is None:
                payload['scheduled_at'] = None
            elif isinstance(updates.scheduled_at, datetime):
                payload['scheduled_at'] = updates.scheduled_at.isoformat()
            elif isinstance(updates.scheduled_at, str):
                try:
                    parsed_date = parse_date_string(updates.scheduled_at)
                    payload['scheduled_at'] = updates.scheduled_at
                except ValidationError:
                    raise ValidationError("Invalid scheduled_at date format")
            else:
                raise ValidationError("scheduled_at must be a datetime object, valid date string, or None")
        
        if not payload:
            raise ValidationError("At least one field must be provided for update")
        
        try:
            endpoint = f"{self.config.base_url}/v1/update-scheduled-email/{email_id}"
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.config.api_key}",
                "X-Request-ID": request_id,
                "User-Agent": "MailBlock-Python-SDK/1.0.0"
            }
            
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.put(endpoint, json=payload, headers=headers) as response:
                    duration = int((time.time() - start_time) * 1000)
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        self._log('info', 'Scheduled email updated successfully', {
                            'request_id': request_id,
                            'duration': f"{duration}ms",
                            'email_id': result.get('email', {}).get('id')
                        })
                        
                        return APIResponse.success_response(
                            data={
                                'message': result.get('message'),
                                'email': result.get('email'),
                                'tracking_updated': result.get('tracking_updated'),
                                'job_rescheduled': result.get('job_rescheduled')
                            },
                            message="Email updated successfully",
                            request_id=request_id,
                            duration=duration,
                            timestamp=timestamp
                        )
                    else:
                        error_data = await response.json() if response.content_type == 'application/json' else {}
                        return self._create_error_response_from_async(
                            response.status, error_data, request_id, duration, timestamp, endpoint
                        )
                        
        except asyncio.TimeoutError as e:
            duration = int((time.time() - start_time) * 1000)
            raise TimeoutError(
                f"Async update request timed out after {self.config.timeout} seconds",
                request_id=request_id
            ) from e
            
        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            self._log('error', 'Async update request failed', {
                'request_id': request_id,
                'error': str(e),
                'duration': f"{duration}ms"
            })
            
            raise MailBlockError(
                f"Async update request failed: {str(e)}",
                error_type="ASYNC_ERROR",
                request_id=request_id
            ) from e

    def __repr__(self) -> str:
        """String representation of MailBlock client."""
        return f"MailBlock(base_url='{self.config.base_url}', debug={self.config.debug})"