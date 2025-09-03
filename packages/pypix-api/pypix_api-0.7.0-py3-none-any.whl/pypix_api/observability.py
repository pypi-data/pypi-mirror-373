"""Modulo de observabilidade integrado para pypix-api.

Este modulo combina logging, metricas e tratamento de erros em uma interface
unificada para monitoramento completo da biblioteca.
"""

import functools
import time
from collections.abc import Callable
from contextlib import contextmanager
from typing import Any

from pypix_api.error_handling import ErrorHandler
from pypix_api.logging import APICallLogger, PIXLogger
from pypix_api.metrics import MetricsCollector, PerformanceTracker


class ObservabilityMixin:
    """Mixin para adicionar observabilidade a classes da API."""

    def __init__(self, *args: Any, **kwargs: Any):
        """Initialize observability components."""
        super().__init__(*args, **kwargs)

        # Setup observability components
        self._setup_observability()

    def _setup_observability(self):
        """Setup logging, metrics and error handling."""
        # Determine logger name based on class
        logger_name = f'pypix_api.{self.__class__.__module__}.{self.__class__.__name__}'

        self.logger = PIXLogger(logger_name)
        self.api_logger = APICallLogger(self.logger)
        self.metrics = MetricsCollector()
        self.error_handler = ErrorHandler(self.logger)

        # Add context for all operations
        self.logger.add_context(
            class_name=self.__class__.__name__, instance_id=id(self)
        )

    @contextmanager
    def observe_operation(self, operation: str, **context: Any):
        """Context manager for observing operations with full telemetry."""
        operation_id = f'{operation}_{int(time.time() * 1000)}'

        # Add operation context
        full_context = {'operation': operation, 'operation_id': operation_id, **context}

        # Start tracking
        with PerformanceTracker(operation, full_context):
            self.logger.info(f'Starting {operation}', **full_context)

            try:
                yield

                self.logger.info(f'Completed {operation}', **full_context)
                self.metrics.increment(f'{operation}.success', tags=full_context)

            except Exception as e:
                # Handle error with full observability
                error_context = {**full_context, 'error': str(e)}

                pix_error = self.error_handler.handle_error(
                    e, error_context, reraise=False
                )

                self.logger.error(f'Failed {operation}', **error_context)
                self.metrics.increment(f'{operation}.failure', tags=error_context)

                raise pix_error from e

    def observe_api_call(self, method: str, url: str, **kwargs: Any):
        """Decorator/context for observing API calls."""

        @contextmanager
        def api_call_context():
            request_id = self.api_logger.log_request(method, url, **kwargs)
            start_time = time.time()

            try:
                yield request_id

                response_time = time.time() - start_time
                self.api_logger.log_response(request_id, 200, response_time, **kwargs)

                self.metrics.record_api_call(
                    method,
                    url,
                    200,
                    response_time,
                    getattr(self, 'bank_name', 'unknown'),
                )

            except Exception as e:
                response_time = time.time() - start_time
                status_code = getattr(e, 'status_code', 500)

                self.api_logger.log_response(
                    request_id, status_code, response_time, error=str(e), **kwargs
                )

                self.metrics.record_api_call(
                    method,
                    url,
                    status_code,
                    response_time,
                    getattr(self, 'bank_name', 'unknown'),
                    error=str(e),
                )

                raise

        return api_call_context()


def observable_method(
    operation_name: str | None = None, track_performance: bool = True
):
    """Decorator para tornar metodos observaveis automaticamente."""

    def decorator(func: Callable) -> Callable:
        name = operation_name or f'{func.__module__}.{func.__name__}'

        @functools.wraps(func)
        def wrapper(self, *args: Any, **kwargs: Any):
            # Check if instance has observability
            if not hasattr(self, 'logger'):
                return func(self, *args, **kwargs)

            with self.observe_operation(name):
                if track_performance:
                    with PerformanceTracker(f'method.{func.__name__}'):
                        return func(self, *args, **kwargs)
                else:
                    return func(self, *args, **kwargs)

        return wrapper

    return decorator


class ObservabilityConfig:
    """Configuracao centralizada de observabilidade."""

    def __init__(self):
        """Initialize observability configuration."""
        import os

        # Logging configuration
        self.log_level = os.getenv('PYPIX_LOG_LEVEL', 'INFO')
        self.log_format = os.getenv('PYPIX_LOG_FORMAT', 'text')  # text or json
        self.log_file = os.getenv('PYPIX_LOG_FILE')

        # Metrics configuration
        self.metrics_enabled = (
            os.getenv('PYPIX_METRICS_ENABLED', 'true').lower() == 'true'
        )
        self.metrics_export_path = os.getenv('PYPIX_METRICS_EXPORT_PATH')
        self.metrics_flush_interval = int(
            os.getenv('PYPIX_METRICS_FLUSH_INTERVAL', '300')
        )

        # Error handling configuration
        self.error_reporting = (
            os.getenv('PYPIX_ERROR_REPORTING', 'true').lower() == 'true'
        )
        self.detailed_tracebacks = (
            os.getenv('PYPIX_DETAILED_TRACEBACKS', 'false').lower() == 'true'
        )

        # Performance tracking
        self.performance_threshold = float(
            os.getenv('PYPIX_PERFORMANCE_THRESHOLD', '1.0')
        )
        self.track_all_methods = (
            os.getenv('PYPIX_TRACK_ALL_METHODS', 'false').lower() == 'true'
        )

    @classmethod
    def from_dict(cls, config: dict[str, Any]) -> 'ObservabilityConfig':
        """Create configuration from dictionary."""
        instance = cls()
        for key, value in config.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        return instance

    def setup_global_observability(self):
        """Setup global observability based on configuration."""
        from pypix_api.logging import setup_logging

        # Setup logging
        setup_logging(
            level=self.log_level,
            log_file=self.log_file,
            structured=(self.log_format == 'json'),
        )

        # Configure metrics
        if not self.metrics_enabled:
            # Disable metrics collection
            metrics = MetricsCollector()
            metrics.enabled = False


class HealthCheck:
    """Health check utilities for monitoring system status."""

    def __init__(self):
        """Initialize health check."""
        self.logger = PIXLogger('pypix_api.health')
        self.metrics = MetricsCollector()

    def check_system_health(self) -> dict[str, Any]:
        """Perform comprehensive system health check."""
        health_status: dict[str, Any] = {
            'status': 'healthy',
            'timestamp': time.time(),
            'checks': {},
        }

        try:
            # Check logging system
            health_status['checks']['logging'] = self._check_logging()

            # Check metrics system
            health_status['checks']['metrics'] = self._check_metrics()

            # Check error handling
            health_status['checks']['error_handling'] = self._check_error_handling()

            # Check memory usage
            health_status['checks']['memory'] = self._check_memory()

            # Determine overall status
            failed_checks = [
                name
                for name, check in health_status['checks'].items()
                if not check.get('healthy', True)
            ]

            if failed_checks:
                health_status['status'] = 'degraded'
                health_status['failed_checks'] = failed_checks

        except Exception as e:
            health_status['status'] = 'unhealthy'
            health_status['error'] = str(e)

            self.logger.error('Health check failed', error=str(e))

        return health_status

    def _check_logging(self) -> dict[str, Any]:
        """Check logging system health."""
        try:
            test_logger = PIXLogger('pypix_api.health_test')
            test_logger.info('Health check test message')

            return {'healthy': True, 'loggers_count': len(PIXLogger._loggers)}
        except Exception as e:
            return {'healthy': False, 'error': str(e)}

    def _check_metrics(self) -> dict[str, Any]:
        """Check metrics system health."""
        try:
            summary = self.metrics.get_summary()

            return {
                'healthy': True,
                'total_metrics': summary['total_metrics'],
                'total_api_calls': summary['total_api_calls'],
                'memory_usage': summary['memory_usage'],
            }
        except Exception as e:
            return {'healthy': False, 'error': str(e)}

    def _check_error_handling(self) -> dict[str, Any]:
        """Check error handling system."""
        try:
            handler = ErrorHandler()

            # Test error classification
            test_error = ValueError('Test error')
            _ = handler.classify_error(test_error)

            return {'healthy': True, 'error_patterns': len(handler.error_patterns)}
        except Exception as e:
            return {'healthy': False, 'error': str(e)}

    def _check_memory(self) -> dict[str, Any]:
        """Check memory usage."""
        try:
            import os

            import psutil

            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()

            return {
                'healthy': True,
                'rss_mb': memory_info.rss / (1024 * 1024),
                'vms_mb': memory_info.vms / (1024 * 1024),
            }
        except ImportError:
            return {
                'healthy': True,
                'note': 'psutil not available for memory monitoring',
            }
        except Exception as e:
            return {'healthy': False, 'error': str(e)}


# Global configuration instance
_config = ObservabilityConfig()


def configure_observability(config: dict | ObservabilityConfig | None = None):
    """Configure global observability settings."""
    global _config

    if isinstance(config, dict):
        _config = ObservabilityConfig.from_dict(config)
    elif isinstance(config, ObservabilityConfig):
        _config = config

    _config.setup_global_observability()


def get_observability_status() -> dict[str, Any]:
    """Get current observability system status."""
    health_check = HealthCheck()
    return health_check.check_system_health()


def create_observability_report() -> dict[str, Any]:
    """Create comprehensive observability report."""
    from pypix_api.metrics import get_metrics_summary

    report = {
        'timestamp': time.time(),
        'health': get_observability_status(),
        'metrics_summary': get_metrics_summary(),
        'configuration': {
            'log_level': _config.log_level,
            'log_format': _config.log_format,
            'metrics_enabled': _config.metrics_enabled,
            'error_reporting': _config.error_reporting,
        },
    }

    return report


# Export main classes and functions
__all__ = [
    'HealthCheck',
    'ObservabilityConfig',
    'ObservabilityMixin',
    'configure_observability',
    'create_observability_report',
    'get_observability_status',
    'observable_method',
]
