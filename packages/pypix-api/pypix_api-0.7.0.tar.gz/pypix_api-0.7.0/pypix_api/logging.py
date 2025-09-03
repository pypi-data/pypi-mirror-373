"""Sistema de logging estruturado para pypix-api.

Este modulo fornece funcionalidades de logging estruturado com suporte a
diferentes formatos de saida, contexto e metricas de performance.
"""

import json
import logging
import os
import time
import uuid
from datetime import datetime
from functools import wraps
from typing import Any


class StructuredFormatter(logging.Formatter):
    """Formatador para logs estruturados em JSON."""

    def __init__(self, include_trace: bool = True):
        """Initialize structured formatter.

        Args:
            include_trace: Include trace information in logs
        """
        super().__init__()
        self.include_trace = include_trace

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }

        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key not in [
                'name',
                'msg',
                'args',
                'levelname',
                'levelno',
                'pathname',
                'filename',
                'module',
                'lineno',
                'funcName',
                'created',
                'msecs',
                'relativeCreated',
                'thread',
                'threadName',
                'processName',
                'process',
                'getMessage',
                'exc_info',
                'exc_text',
                'stack_info',
            ]:
                log_entry[key] = value

        # Add exception info if present
        if record.exc_info and self.include_trace:
            log_entry['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_entry, ensure_ascii=False)


class PIXLogger:
    """Logger principal para operacoes PIX."""

    _instance = None
    _loggers: dict[str, logging.Logger] = {}

    def __new__(cls, name: str = 'pypix_api'):
        """Singleton pattern para loggers."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, name: str = 'pypix_api'):
        """Initialize PIX logger."""
        if name not in self._loggers:
            self._setup_logger(name)
        self.logger = self._loggers[name]
        self.context: dict[str, Any] = {}

    def _setup_logger(self, name: str) -> None:
        """Setup logger with appropriate handlers."""
        logger = logging.getLogger(name)

        # Avoid duplicate handlers
        if logger.handlers:
            self._loggers[name] = logger
            return

        logger.setLevel(logging.INFO)

        # Console handler with structured format
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Use structured format in production, simple in development
        if os.getenv('PYPIX_LOG_FORMAT') == 'json':
            formatter: logging.Formatter = StructuredFormatter()
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )

        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler if specified
        log_file = os.getenv('PYPIX_LOG_FILE')
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(StructuredFormatter())
            logger.addHandler(file_handler)

        self._loggers[name] = logger

    def add_context(self, **kwargs: Any) -> None:
        """Add context to all subsequent log messages."""
        self.context.update(kwargs)

    def clear_context(self) -> None:
        """Clear logging context."""
        self.context.clear()

    def _log_with_context(self, level: str, message: str, **kwargs: Any) -> None:
        """Log message with context."""
        extra = {**self.context, **kwargs}
        getattr(self.logger, level)(message, extra=extra)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""
        self._log_with_context('debug', message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        self._log_with_context('info', message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message."""
        self._log_with_context('warning', message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message."""
        self._log_with_context('error', message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        """Log critical message."""
        self._log_with_context('critical', message, **kwargs)


class APICallLogger:
    """Logger especializado para chamadas de API."""

    def __init__(self, logger: PIXLogger | None = None):
        """Initialize API call logger."""
        self.logger = logger or PIXLogger('pypix_api.api')

    def log_request(
        self,
        method: str,
        url: str,
        headers: dict | None = None,
        body: dict | None = None,
        **kwargs: Any,
    ) -> str:
        """Log API request with sanitized data."""
        request_id = str(uuid.uuid4())

        # Sanitize sensitive data
        safe_headers = self._sanitize_headers(headers or {})
        safe_body = self._sanitize_body(body or {})

        self.logger.info(
            f'API Request: {method} {url}',
            request_id=request_id,
            method=method,
            url=url,
            headers=safe_headers,
            body=safe_body,
            **kwargs,
        )

        return request_id

    def log_response(
        self,
        request_id: str,
        status_code: int,
        response_time: float,
        response_body: dict | None = None,
        **kwargs: Any,
    ) -> None:
        """Log API response."""
        safe_body = self._sanitize_body(response_body or {})

        level = 'info' if status_code < 400 else 'error'

        getattr(self.logger, level)(
            f'API Response: {status_code} ({response_time:.3f}s)',
            request_id=request_id,
            status_code=status_code,
            response_time=response_time,
            response_body=safe_body,
            **kwargs,
        )

    def _sanitize_headers(self, headers: dict[str, Any]) -> dict[str, Any]:
        """Remove sensitive data from headers."""
        sensitive_keys = {'authorization', 'x-api-key', 'cookie', 'set-cookie'}

        sanitized = {}
        for key, value in headers.items():
            if key.lower() in sensitive_keys:
                sanitized[key] = '[REDACTED]'
            else:
                sanitized[key] = value

        return sanitized

    def _sanitize_body(self, body: dict[str, Any]) -> dict[str, Any]:
        """Remove sensitive data from request/response body."""
        if not isinstance(body, dict):
            return body

        sensitive_keys = {
            'client_secret',
            'password',
            'token',
            'access_token',
            'refresh_token',
            'cpf',
            'cnpj',
            'account',
            'key',
        }

        sanitized = {}
        for key, value in body.items():
            if key.lower() in sensitive_keys or 'senha' in key.lower():
                sanitized[key] = '[REDACTED]'
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_body(value)  # type: ignore[assignment]
            else:
                sanitized[key] = value

        return sanitized


def log_performance(logger: PIXLogger | None = None, threshold: float = 1.0):
    """Decorator para medir e logar performance de funcoes.

    Args:
        logger: Logger instance to use
        threshold: Log warning if execution time exceeds threshold (seconds)
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any):
            _logger = logger or PIXLogger(f'pypix_api.{func.__module__}')

            start_time = time.time()
            function_id = str(uuid.uuid4())

            _logger.debug(
                f'Starting {func.__name__}',
                function=func.__name__,
                function_id=function_id,
                args_count=len(args),
                kwargs_keys=list(kwargs.keys()),
            )

            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time

                level = 'warning' if execution_time > threshold else 'debug'
                getattr(_logger, level)(
                    f'Completed {func.__name__} in {execution_time:.3f}s',
                    function=func.__name__,
                    function_id=function_id,
                    execution_time=execution_time,
                    success=True,
                )

                return result

            except Exception as e:
                execution_time = time.time() - start_time
                _logger.error(
                    f'Failed {func.__name__} after {execution_time:.3f}s: {e!s}',
                    function=func.__name__,
                    function_id=function_id,
                    execution_time=execution_time,
                    success=False,
                    error_type=type(e).__name__,
                    error_message=str(e),
                )
                raise

        return wrapper

    return decorator


def setup_logging(
    level: str = 'INFO', log_file: str | None = None, structured: bool = False
) -> PIXLogger:
    """Configure global logging for pypix-api.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for logging
        structured: Use structured JSON logging

    Returns:
        Configured PIXLogger instance
    """
    # Set environment variables for logger configuration
    if structured:
        os.environ['PYPIX_LOG_FORMAT'] = 'json'

    if log_file:
        os.environ['PYPIX_LOG_FILE'] = log_file

    # Configure root pypix logger
    logger = PIXLogger('pypix_api')
    logger.logger.setLevel(getattr(logging, level.upper()))

    logger.info(
        'Logging configured for pypix-api',
        level=level,
        structured=structured,
        log_file=log_file,
    )

    return logger


# Convenience functions for common logging patterns
def log_bank_operation(operation: str, bank: str, **kwargs: Any) -> None:
    """Log bank operation with context."""
    logger = PIXLogger('pypix_api.bank')
    logger.info(
        f'Bank operation: {operation}', operation=operation, bank=bank, **kwargs
    )


def log_pix_transaction(
    txid: str, operation_type: str, amount: str | None = None, **kwargs: Any
) -> None:
    """Log PIX transaction with context."""
    logger = PIXLogger('pypix_api.pix')
    logger.info(
        f'PIX {operation_type}: {txid}',
        txid=txid,
        operation_type=operation_type,
        amount=amount,
        **kwargs,
    )


def log_authentication(
    client_id: str, scope: str, success: bool, **kwargs: Any
) -> None:
    """Log authentication attempt."""
    logger = PIXLogger('pypix_api.auth')

    level = 'info' if success else 'warning'
    message = f'Authentication {"successful" if success else "failed"} for {client_id}'

    getattr(logger, level)(
        message, client_id=client_id, scope=scope, success=success, **kwargs
    )


# Export main classes and functions
__all__ = [
    'APICallLogger',
    'PIXLogger',
    'StructuredFormatter',
    'log_authentication',
    'log_bank_operation',
    'log_performance',
    'log_pix_transaction',
    'setup_logging',
]
