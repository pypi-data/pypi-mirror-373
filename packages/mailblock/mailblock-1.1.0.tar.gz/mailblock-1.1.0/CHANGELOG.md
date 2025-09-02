# Changelog

All notable changes to the MailBlock Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-08-28

### Added
- **Multiple Recipients Support**: Send emails to multiple recipients with arrays
- **CC/BCC Support**: Carbon copy and blind carbon copy functionality
- **Email Cancellation**: Cancel scheduled emails with `cancel_email_sync()` and `cancel_email()`
- **Bulk Email Cancellation**: Cancel multiple emails at once with `cancel_emails_sync()` and `cancel_emails()`
- **Scheduled Email Updates**: Update scheduled email content with `update_scheduled_email_sync()` and `update_scheduled_email()`
- **New Data Types**: `UpdateEmailData`, `CancelEmailResponse`, `BulkCancelResponse`, `UpdateEmailResponse`
- **Enhanced Validation**: Comprehensive validation for email arrays and IDs
- **Full Async Support**: All new features support both sync and async operations

### Enhanced
- **EmailBuilder**: Now supports `.cc()` and `.bcc()` methods with array inputs
- **EmailData**: Extended to support CC/BCC fields and multiple recipients
- **Validation**: Enhanced email validation for arrays and bulk operations
- **Type Safety**: Improved type hints throughout the SDK

### Fixed
- **Dependency Management**: Cleaned up duplicate dependencies between setup.py and requirements.txt
- **Package Structure**: Better separation of production and development dependencies

## [1.0.1] - 2025-08-12

### Fixed
- Corrected installation instructions in README from `pip install mailblock-python` to `pip install mailblock`
- Updated PyPI links to use correct package name `mailblock`
- Fixed all documentation references to use the correct package name

### Documentation
- Updated GitHub repository links
- Corrected PyPI project URL references

## [1.0.0] - 2025-08-12

### Added
- Initial release of MailBlock Python SDK
- Fluent builder pattern for email construction
- Both synchronous and asynchronous email sending
- Email scheduling support
- Comprehensive error handling and validation
- Advanced logging and debugging capabilities
- Automatic retry mechanism with exponential backoff
- Complete type hints and mypy support
- Context manager support for proper resource management
- Support for both text and HTML email content
- Custom logger integration
- Comprehensive test suite
- Full documentation and examples

### Dependencies
- `requests>=2.25.0` for HTTP client functionality
- `typing-extensions>=4.0.0` for Python <3.10 compatibility
- Optional `aiohttp>=3.8.0` for async support

### Supported Python Versions
- Python 3.8+
- Python 3.9
- Python 3.10
- Python 3.11
- Python 3.12