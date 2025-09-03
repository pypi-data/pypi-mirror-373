"""Sistema de metricas e telemetria para pypix-api.

Este modulo coleta e reporta metricas de uso da biblioteca para monitoramento
e otimizacao de performance.
"""

import json
import os
import threading
import time
from collections import Counter, defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class MetricEntry:
    """Entrada de metrica individual."""

    name: str
    value: float
    timestamp: datetime
    tags: dict[str, str] = field(default_factory=dict)
    unit: str = 'count'


@dataclass
class APICallMetric:
    """Metrica para chamadas de API."""

    method: str
    endpoint: str
    status_code: int
    response_time: float
    timestamp: datetime
    bank: str
    error: str | None = None


class MetricsCollector:
    """Coletor central de metricas."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Singleton pattern for metrics collector."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize metrics collector."""
        if hasattr(self, '_initialized'):
            return

        self._initialized = True
        self.metrics: list[MetricEntry] = []
        self.api_calls: list[APICallMetric] = []
        self.counters: dict[str, int] = Counter()
        self.gauges: dict[str, float] = {}
        self.histograms: dict[str, list[float]] = defaultdict(list)
        self.start_time = datetime.now()
        self._lock = threading.Lock()

        # Enable/disable metrics collection
        self.enabled = os.getenv('PYPIX_METRICS_ENABLED', 'true').lower() == 'true'

        # Auto-flush configuration
        self.auto_flush_interval = int(
            os.getenv('PYPIX_METRICS_FLUSH_INTERVAL', '300')
        )  # 5 minutes
        self.max_metrics = int(os.getenv('PYPIX_METRICS_MAX_BUFFER', '1000'))

        if self.enabled:
            self._setup_auto_flush()

    def _setup_auto_flush(self):
        """Setup automatic metrics flushing."""

        def flush_periodically():
            while self.enabled:
                time.sleep(self.auto_flush_interval)
                if len(self.metrics) > 0 or len(self.api_calls) > 0:
                    self.flush_metrics()

        flush_thread = threading.Thread(target=flush_periodically, daemon=True)
        flush_thread.start()

    def increment(
        self, name: str, value: int = 1, tags: dict[str, str] | None = None
    ) -> None:
        """Increment a counter metric."""
        if not self.enabled:
            return

        with self._lock:
            key = f'{name}:{json.dumps(tags or {}, sort_keys=True)}'
            self.counters[key] += value

            self.metrics.append(
                MetricEntry(
                    name=name,
                    value=value,
                    timestamp=datetime.now(),
                    tags=tags or {},
                    unit='count',
                )
            )

            self._check_buffer_size()

    def gauge(
        self, name: str, value: float, tags: dict[str, str] | None = None
    ) -> None:
        """Set a gauge metric value."""
        if not self.enabled:
            return

        with self._lock:
            key = f'{name}:{json.dumps(tags or {}, sort_keys=True)}'
            self.gauges[key] = value

            self.metrics.append(
                MetricEntry(
                    name=name,
                    value=value,
                    timestamp=datetime.now(),
                    tags=tags or {},
                    unit='gauge',
                )
            )

            self._check_buffer_size()

    def histogram(
        self, name: str, value: float, tags: dict[str, str] | None = None
    ) -> None:
        """Record a histogram value."""
        if not self.enabled:
            return

        with self._lock:
            key = f'{name}:{json.dumps(tags or {}, sort_keys=True)}'
            self.histograms[key].append(value)

            self.metrics.append(
                MetricEntry(
                    name=name,
                    value=value,
                    timestamp=datetime.now(),
                    tags=tags or {},
                    unit='histogram',
                )
            )

            self._check_buffer_size()

    def timing(
        self, name: str, duration: float, tags: dict[str, str] | None = None
    ) -> None:
        """Record timing metric in seconds."""
        self.histogram(f'{name}.duration', duration, tags)

    def record_api_call(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        response_time: float,
        bank: str,
        error: str | None = None,
    ) -> None:
        """Record API call metrics."""
        if not self.enabled:
            return

        with self._lock:
            self.api_calls.append(
                APICallMetric(
                    method=method,
                    endpoint=endpoint,
                    status_code=status_code,
                    response_time=response_time,
                    timestamp=datetime.now(),
                    bank=bank,
                    error=error,
                )
            )

            # Also record as regular metrics
            tags = {
                'method': method,
                'bank': bank,
                'status_code': str(status_code),
                'success': str(error is None),
            }

            self.increment('api_calls_total', tags=tags)
            self.histogram('api_call_duration', response_time, tags=tags)

            if error:
                self.increment('api_errors_total', tags={**tags, 'error': error})

            self._check_buffer_size()

    def _check_buffer_size(self) -> None:
        """Check if buffer needs flushing."""
        total_metrics = len(self.metrics) + len(self.api_calls)
        if total_metrics >= self.max_metrics:
            self.flush_metrics()

    def get_summary(self) -> dict[str, Any]:
        """Get metrics summary."""
        with self._lock:
            uptime = (datetime.now() - self.start_time).total_seconds()

            # API call statistics
            total_api_calls = len(self.api_calls)
            successful_calls = sum(1 for call in self.api_calls if call.error is None)

            response_times = [call.response_time for call in self.api_calls]
            avg_response_time = (
                sum(response_times) / len(response_times) if response_times else 0
            )

            # Counter totals
            counter_summary = dict(self.counters.most_common(10))

            return {
                'uptime_seconds': uptime,
                'total_metrics': len(self.metrics),
                'total_api_calls': total_api_calls,
                'successful_api_calls': successful_calls,
                'error_rate': (total_api_calls - successful_calls) / total_api_calls
                if total_api_calls > 0
                else 0,
                'average_response_time': avg_response_time,
                'top_counters': counter_summary,
                'memory_usage': self._estimate_memory_usage(),
                'last_flush': getattr(self, '_last_flush', None),
            }

    def _estimate_memory_usage(self) -> dict[str, int]:
        """Estimate memory usage of metrics."""
        import sys

        return {
            'metrics_bytes': sys.getsizeof(self.metrics),
            'api_calls_bytes': sys.getsizeof(self.api_calls),
            'counters_bytes': sys.getsizeof(self.counters),
            'total_estimated': sys.getsizeof(self.metrics)
            + sys.getsizeof(self.api_calls)
            + sys.getsizeof(self.counters),
        }

    def flush_metrics(self, export_path: str | None = None) -> bool:
        """Flush metrics to storage/export."""
        if not self.enabled:
            return False

        with self._lock:
            if not self.metrics and not self.api_calls:
                return False

            # Determine export path
            if export_path is None:
                export_path = os.getenv('PYPIX_METRICS_EXPORT_PATH')

            if export_path:
                success = self._export_to_file(export_path)
            else:
                success = self._export_to_console()

            if success:
                # Clear flushed metrics (keep last 100 for summary)
                self.metrics = self.metrics[-100:]
                self.api_calls = self.api_calls[-100:]
                self._last_flush = datetime.now()

            return success

    def _export_to_file(self, file_path: str) -> bool:
        """Export metrics to JSON file."""
        try:
            export_data = {
                'timestamp': datetime.now().isoformat(),
                'summary': self.get_summary(),
                'metrics': [
                    {
                        'name': m.name,
                        'value': m.value,
                        'timestamp': m.timestamp.isoformat(),
                        'tags': m.tags,
                        'unit': m.unit,
                    }
                    for m in self.metrics
                ],
                'api_calls': [
                    {
                        'method': call.method,
                        'endpoint': call.endpoint,
                        'status_code': call.status_code,
                        'response_time': call.response_time,
                        'timestamp': call.timestamp.isoformat(),
                        'bank': call.bank,
                        'error': call.error,
                    }
                    for call in self.api_calls
                ],
            }

            Path(file_path).parent.mkdir(parents=True, exist_ok=True)

            # Append to file or create new
            if Path(file_path).exists():
                with open(file_path, 'a') as f:
                    f.write('\n' + json.dumps(export_data, ensure_ascii=False))
            else:
                with open(file_path, 'w') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)

            return True

        except Exception as e:
            print(f'Failed to export metrics to file: {e}')
            return False

    def _export_to_console(self) -> bool:
        """Export metrics summary to console."""
        try:
            summary = self.get_summary()
            print('\n=== pypix-api Metrics Summary ===')
            print(f'Uptime: {summary["uptime_seconds"]:.1f}s')
            print(
                f'API Calls: {summary["total_api_calls"]} (Success: {summary["successful_api_calls"]})'
            )
            print(f'Error Rate: {summary["error_rate"]:.2%}')
            print(f'Avg Response Time: {summary["average_response_time"]:.3f}s')
            print('================================\n')
            return True
        except Exception:
            return False

    def clear_metrics(self) -> None:
        """Clear all collected metrics."""
        with self._lock:
            self.metrics.clear()
            self.api_calls.clear()
            self.counters.clear()
            self.gauges.clear()
            self.histograms.clear()


def timed_function(metric_name: str | None = None, tags: dict[str, str] | None = None):
    """Decorator to automatically time function execution."""

    def decorator(func: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any):
            start_time = time.time()
            name = metric_name or f'function.{func.__name__}'

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                metrics = MetricsCollector()
                metrics.timing(name, duration, tags)
                metrics.increment(
                    f'{name}.calls', tags={**(tags or {}), 'success': 'true'}
                )

                return result

            except Exception as e:
                duration = time.time() - start_time

                metrics = MetricsCollector()
                metrics.timing(name, duration, tags)
                metrics.increment(
                    f'{name}.calls',
                    tags={
                        **(tags or {}),
                        'success': 'false',
                        'error': type(e).__name__,
                    },
                )
                metrics.increment(
                    f'{name}.errors', tags={**(tags or {}), 'error': type(e).__name__}
                )

                raise

        return wrapper

    return decorator


class PerformanceTracker:
    """Context manager para tracking de performance."""

    def __init__(self, operation_name: str, tags: dict[str, str] | None = None):
        """Initialize performance tracker."""
        self.operation_name = operation_name
        self.tags = tags or {}
        self.start_time = None
        self.metrics = MetricsCollector()

    def __enter__(self):
        """Start tracking."""
        self.start_time = time.time()
        self.metrics.increment(f'{self.operation_name}.started', tags=self.tags)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End tracking and record metrics."""
        if self.start_time:
            duration = time.time() - self.start_time

            success_tags = {**self.tags, 'success': str(exc_type is None)}

            self.metrics.timing(self.operation_name, duration, success_tags)
            self.metrics.increment(
                f'{self.operation_name}.completed', tags=success_tags
            )

            if exc_type is not None:
                error_tags = {**self.tags, 'error': exc_type.__name__}
                self.metrics.increment(f'{self.operation_name}.errors', tags=error_tags)


# Convenience functions for common metrics
def track_bank_operation(bank: str, operation: str) -> PerformanceTracker:
    """Track bank operation performance."""
    return PerformanceTracker(
        'bank_operation', tags={'bank': bank, 'operation': operation}
    )


def track_api_call(method: str, endpoint: str) -> PerformanceTracker:
    """Track API call performance."""
    return PerformanceTracker('api_call', tags={'method': method, 'endpoint': endpoint})


def get_metrics_summary() -> dict[str, Any]:
    """Get current metrics summary."""
    return MetricsCollector().get_summary()


def export_metrics(file_path: str | None = None) -> bool:
    """Export metrics to file or console."""
    return MetricsCollector().flush_metrics(file_path)


def clear_metrics() -> None:
    """Clear all metrics."""
    MetricsCollector().clear_metrics()


# Export main classes and functions
__all__ = [
    'APICallMetric',
    'MetricEntry',
    'MetricsCollector',
    'PerformanceTracker',
    'clear_metrics',
    'export_metrics',
    'get_metrics_summary',
    'timed_function',
    'track_api_call',
    'track_bank_operation',
]
