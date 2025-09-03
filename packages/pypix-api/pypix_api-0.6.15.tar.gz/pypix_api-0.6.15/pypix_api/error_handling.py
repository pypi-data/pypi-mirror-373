"""Sistema avancado de tratamento de erros para pypix-api.

Este modulo fornece classes de erro especializadas, context managers para
tratamento robusto de erros e utilitarios para debugging avancado.
"""

import json
import re
import traceback
from collections.abc import Callable
from datetime import datetime
from functools import wraps
from typing import Any

from pypix_api.logging import PIXLogger
from pypix_api.metrics import MetricsCollector


class PIXError(Exception):
    """Base exception class for pypix-api errors."""

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ):
        """Initialize PIX error.

        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            details: Additional error context
            cause: Original exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__.upper()
        self.details = details or {}
        self.cause = cause
        self.timestamp = datetime.now()
        self.traceback_info = traceback.format_exc() if cause else None

    def to_dict(self) -> dict[str, Any]:
        """Convert error to dictionary representation."""
        return {
            'error_type': self.__class__.__name__,
            'error_code': self.error_code,
            'message': self.message,
            'details': self.details,
            'timestamp': self.timestamp.isoformat(),
            'traceback': self.traceback_info,
            'cause': str(self.cause) if self.cause else None,
        }

    def __str__(self) -> str:
        """String representation of error."""
        parts = [f'{self.error_code}: {self.message}']

        if self.details:
            parts.append(f'Details: {json.dumps(self.details, indent=2)}')

        if self.cause:
            parts.append(f'Caused by: {self.cause!s}')

        return '\n'.join(parts)


class AuthenticationError(PIXError):
    """Raised when authentication fails."""

    def __init__(self, message: str = 'Authentication failed', **kwargs: Any):
        super().__init__(message, error_code='AUTH_ERROR', **kwargs)


class AuthorizationError(PIXError):
    """Raised when authorization/permission fails."""

    def __init__(self, message: str = 'Authorization failed', **kwargs: Any):
        super().__init__(message, error_code='AUTHZ_ERROR', **kwargs)


class ValidationError(PIXError):
    """Raised when data validation fails."""

    def __init__(
        self,
        message: str = 'Validation failed',
        field: str | None = None,
        **kwargs: Any,
    ):
        details = kwargs.get('details', {})
        if field:
            details['field'] = field
        kwargs['details'] = details
        super().__init__(message, error_code='VALIDATION_ERROR', **kwargs)


class APIError(PIXError):
    """Raised when API call fails."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: dict | None = None,
        **kwargs: Any,
    ):
        details = kwargs.get('details', {})
        if status_code:
            details['status_code'] = status_code
        if response_body:
            details['response_body'] = response_body
        kwargs['details'] = details
        super().__init__(message, error_code='API_ERROR', **kwargs)


class NetworkError(PIXError):
    """Raised when network communication fails."""

    def __init__(self, message: str = 'Network communication failed', **kwargs: Any):
        super().__init__(message, error_code='NETWORK_ERROR', **kwargs)


class ConfigurationError(PIXError):
    """Raised when configuration is invalid."""

    def __init__(self, message: str = 'Configuration error', **kwargs: Any):
        super().__init__(message, error_code='CONFIG_ERROR', **kwargs)


class CertificateError(PIXError):
    """Raised when certificate handling fails."""

    def __init__(self, message: str = 'Certificate error', **kwargs: Any):
        super().__init__(message, error_code='CERT_ERROR', **kwargs)


class RateLimitError(PIXError):
    """Raised when API rate limit is exceeded."""

    def __init__(
        self,
        message: str = 'Rate limit exceeded',
        retry_after: int | None = None,
        **kwargs: Any,
    ):
        details = kwargs.get('details', {})
        if retry_after:
            details['retry_after'] = retry_after
        kwargs['details'] = details
        super().__init__(message, error_code='RATE_LIMIT_ERROR', **kwargs)


class BankSpecificError(PIXError):
    """Raised for bank-specific errors."""

    def __init__(
        self,
        message: str,
        bank_code: str | None = None,
        bank_error_code: str | None = None,
        **kwargs: Any,
    ):
        details = kwargs.get('details', {})
        if bank_code:
            details['bank_code'] = bank_code
        if bank_error_code:
            details['bank_error_code'] = bank_error_code
        kwargs['details'] = details
        super().__init__(message, error_code='BANK_ERROR', **kwargs)


class PIXTransactionError(PIXError):
    """Raised when PIX transaction fails."""

    def __init__(
        self,
        message: str,
        txid: str | None = None,
        operation: str | None = None,
        **kwargs: Any,
    ):
        details = kwargs.get('details', {})
        if txid:
            details['txid'] = txid
        if operation:
            details['operation'] = operation
        kwargs['details'] = details
        super().__init__(message, error_code='PIX_TRANSACTION_ERROR', **kwargs)


class ErrorHandler:
    """Advanced error handler with logging and metrics integration."""

    def __init__(self, logger: PIXLogger | None = None):
        """Initialize error handler."""
        self.logger = logger or PIXLogger('pypix_api.errors')
        self.metrics = MetricsCollector()
        self.error_patterns = self._setup_error_patterns()

    def _setup_error_patterns(self) -> dict[str, type[PIXError]]:
        """Setup common error patterns for classification."""
        return {
            r'invalid.*client': AuthenticationError,
            r'unauthorized': AuthenticationError,
            r'forbidden': AuthorizationError,
            r'access.*denied': AuthorizationError,
            r'validation.*failed': ValidationError,
            r'invalid.*format': ValidationError,
            r'required.*field': ValidationError,
            r'rate.*limit': RateLimitError,
            r'too.*many.*requests': RateLimitError,
            r'certificate.*error': CertificateError,
            r'ssl.*error': CertificateError,
            r'network.*error': NetworkError,
            r'connection.*failed': NetworkError,
            r'timeout': NetworkError,
        }

    def classify_error(self, error: Exception, context: dict | None = None) -> PIXError:
        """Classify a generic exception as a specific PIX error."""
        error_msg = str(error).lower()

        # Try to match against known patterns
        for pattern, error_class in self.error_patterns.items():
            if re.search(pattern, error_msg):
                return error_class(
                    message=str(error), details=context or {}, cause=error
                )

        # Check specific exception types
        if isinstance(error, ConnectionError | TimeoutError):
            return NetworkError(message=str(error), cause=error)
        elif isinstance(error, PermissionError):
            return AuthorizationError(message=str(error), cause=error)
        elif isinstance(error, ValueError):
            return ValidationError(message=str(error), cause=error)

        # Default to generic PIXError
        return PIXError(
            message=str(error),
            error_code='UNKNOWN_ERROR',
            details=context or {},
            cause=error,
        )

    def handle_error(
        self, error: Exception, context: dict | None = None, reraise: bool = True
    ) -> PIXError | None:
        """Handle an error with logging and metrics."""
        # Classify if needed
        if isinstance(error, PIXError):
            pix_error = error
        else:
            pix_error = self.classify_error(error, context)

        # Log error
        self.logger.error(
            f'Error occurred: {pix_error.error_code}',
            error_code=pix_error.error_code,
            error_message=pix_error.message,
            error_details=pix_error.details,
            **context or {},
        )

        # Record metrics
        self.metrics.increment(
            'errors_total',
            tags={
                'error_type': pix_error.__class__.__name__,
                'error_code': pix_error.error_code,
            },
        )

        if reraise:
            raise pix_error

        return pix_error


class ErrorContext:
    """Context manager for robust error handling."""

    def __init__(
        self,
        operation: str,
        context: dict | None = None,
        handler: ErrorHandler | None = None,
        reraise: bool = True,
    ):
        """Initialize error context.

        Args:
            operation: Name of operation being performed
            context: Additional context for error handling
            handler: Custom error handler
            reraise: Whether to reraise handled errors
        """
        self.operation = operation
        self.context = context or {}
        self.context['operation'] = operation
        self.handler = handler or ErrorHandler()
        self.reraise = reraise

    def __enter__(self):
        """Enter error context."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Handle any exception that occurred."""
        if exc_type is not None:
            self.handler.handle_error(exc_val, self.context, self.reraise)
        return not self.reraise


def handle_errors(
    operation: str,
    context: dict | None = None,
    reraise: bool = True,
    logger: PIXLogger | None = None,
):
    """Decorator for automatic error handling."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any):
            handler = ErrorHandler(logger)
            func_context = {
                'function': func.__name__,
                'operation': operation,
                **(context or {}),
            }

            try:
                return func(*args, **kwargs)
            except Exception as e:
                return handler.handle_error(e, func_context, reraise)

        return wrapper

    return decorator


class ErrorRecovery:
    """Utilities for error recovery and retry logic."""

    @staticmethod
    def should_retry(error: Exception, max_retries: int = 3) -> bool:
        """Determine if an operation should be retried."""
        if isinstance(error, NetworkError | APIError | RateLimitError):
            return True

        if isinstance(error, APIError) and error.details.get('status_code', 0) >= 500:
            return True

        return False

    @staticmethod
    def get_retry_delay(attempt: int, base_delay: float = 1.0) -> float:
        """Calculate retry delay using exponential backoff."""
        return min(base_delay * (2**attempt), 60.0)  # Max 60 seconds

    @staticmethod
    def retry_with_backoff(
        func: Callable,
        max_retries: int = 3,
        base_delay: float = 1.0,
        logger: PIXLogger | None = None,
    ) -> Any:
        """Retry function with exponential backoff."""
        _logger = logger or PIXLogger('pypix_api.retry')

        for attempt in range(max_retries + 1):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries or not ErrorRecovery.should_retry(e):
                    _logger.error(
                        f'Operation failed after {attempt + 1} attempts',
                        error=str(e),
                        attempts=attempt + 1,
                    )
                    raise

                delay = ErrorRecovery.get_retry_delay(attempt, base_delay)
                _logger.warning(
                    f'Operation failed, retrying in {delay:.1f}s (attempt {attempt + 1}/{max_retries + 1})',
                    error=str(e),
                    attempt=attempt + 1,
                    delay=delay,
                )

                import time

                time.sleep(delay)


def create_error_report(
    error: PIXError, include_system_info: bool = True
) -> dict[str, Any]:
    """Create comprehensive error report for debugging."""
    report = error.to_dict()

    if include_system_info:
        import platform
        import sys

        report['system_info'] = {
            'python_version': sys.version,
            'platform': platform.platform(),
            'architecture': platform.architecture(),
        }

        # Add library version if available
        try:
            import pypix_api

            report['library_version'] = pypix_api.__version__
        except (ImportError, AttributeError):
            report['library_version'] = 'unknown'

    return report


# Export main classes and functions
__all__ = [
    'APIError',
    'AuthenticationError',
    'AuthorizationError',
    'BankSpecificError',
    'CertificateError',
    'ConfigurationError',
    'ErrorContext',
    'ErrorHandler',
    'ErrorRecovery',
    'NetworkError',
    'PIXError',
    'PIXTransactionError',
    'RateLimitError',
    'ValidationError',
    'create_error_report',
    'handle_errors',
]
