# metrics.py
"""Metrics implementation for Rebrandly OTEL SDK."""
from typing import Optional, Dict, List
from dataclasses import dataclass
from enum import Enum
from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.metrics import Meter, Histogram, Instrument, Counter
from opentelemetry.metrics._internal import Gauge
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (PeriodicExportingMetricReader, ConsoleMetricExporter)
from opentelemetry.sdk.metrics._internal.aggregation import (ExplicitBucketHistogramAggregation)
from opentelemetry.sdk.metrics.view import View

from src.otel_utils import *

class MetricType(Enum):
    """Supported metric types."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    UP_DOWN_COUNTER = "up_down_counter"

@dataclass
class MetricDefinition:
    """Definition of a metric."""
    name: str
    description: str
    unit: str = "1"
    type: MetricType = MetricType.COUNTER

class RebrandlyMeter:
    """Wrapper for OpenTelemetry metrics with Rebrandly-specific features."""

    # Standardized metric definitions aligned with Node.js
    DEFAULT_METRICS = {
        'invocations': MetricDefinition(
            name='invocations',
            description='Number of invocations',
            unit='1',
            type=MetricType.COUNTER
        ),
        'successful_invocations': MetricDefinition(
            name='successful_invocations',
            description='Number of successful invocations',
            unit='1',
            type=MetricType.COUNTER
        ),
        'error_invocations': MetricDefinition(
            name='error_invocations',
            description='Number of error invocations',
            unit='1',
            type=MetricType.COUNTER
        ),
        'duration': MetricDefinition(
            name='duration',
            description='Duration of execution in milliseconds',
            unit='ms',
            type=MetricType.HISTOGRAM
        ),
        'cpu_usage_percentage': MetricDefinition(
            name='cpu_usage_percentage',
            description='CPU usage percentage',
            unit='%',
            type=MetricType.GAUGE
        ),
        'memory_usage_bytes': MetricDefinition(
            name='memory_usage_bytes',
            description='Memory usage in bytes',
            unit='By',
            type=MetricType.GAUGE
        ),
    }

    class GlobalMetrics:
        def __init__(self, rebrandly_meter):
            self.__rebrandly_meter = rebrandly_meter
            self.invocations: Counter = self.__rebrandly_meter.get_metric('invocations')
            self.successful_invocations: Counter = self.__rebrandly_meter.get_metric('successful_invocations')
            self.error_invocations: Counter = self.__rebrandly_meter.get_metric('error_invocations')
            self.duration: Histogram = self.__rebrandly_meter.get_metric('duration')
            self.cpu_usage_percentage: Gauge = self.__rebrandly_meter.get_metric('cpu_usage_percentage')
            self.memory_usage_bytes: Gauge = self.__rebrandly_meter.get_metric('memory_usage_bytes')


    def __init__(self):
        self._meter: Optional[Meter] = None
        self._provider: Optional[MeterProvider] = None
        self._metrics: Dict[str, Instrument] = {}
        self.__setup_metrics()
        self.__register_default_metrics()
        self.GlobalMetrics = RebrandlyMeter.GlobalMetrics(self)

    def __setup_metrics(self):
        """Initialize metrics with configured exporters."""

        readers = []

        # Add console exporter for local debugging
        if is_otel_debug():
            console_reader = PeriodicExportingMetricReader(
                ConsoleMetricExporter(),
                export_interval_millis=1000  # 10 seconds for debugging
            )
            readers.append(console_reader)

        # Add OTLP exporter if configured
        if get_otlp_endpoint() is not None:
            otlp_exporter = OTLPMetricExporter(endpoint=get_otlp_endpoint())
            otlp_reader = PeriodicExportingMetricReader(otlp_exporter, export_interval_millis=get_millis_batch_time())
            readers.append(otlp_reader)

        # Create views
        views = self.__create_views()

        # Create provider
        self._provider = MeterProvider(
            resource=create_resource(),
            metric_readers=readers,
            views=views
        )

        # Set as global provider
        metrics.set_meter_provider(self._provider)

        # Get meter
        self._meter = metrics.get_meter(get_service_name(), get_service_version())

    def __create_views(self) -> List[View]:
        """Create metric views for customization."""
        views = []

        # Histogram view with custom buckets
        histogram_view = View(
            instrument_type=Histogram,
            instrument_name="*",
            aggregation=ExplicitBucketHistogramAggregation((0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1, 2.5, 5, 7.5, 10)) # todo <-- define buckets
        )
        views.append(histogram_view)

        return views

    def __register_default_metrics(self):
        """Register default metrics."""
        for name, definition in self.DEFAULT_METRICS.items():
            self.register_metric(definition)

    @property
    def meter(self) -> Meter:
        """Get the underlying OpenTelemetry meter."""
        if not self._meter:
            # Return no-op meter if metrics are disabled
            return metrics.get_meter(__name__)
        return self._meter

    def force_flush(self, timeout_millis: int = 5000) -> bool:
        """
        Force flush all pending metrics.

        Args:
            timeout_millis: Maximum time to wait for flush in milliseconds

        Returns:
            True if flush succeeded, False otherwise
        """
        if not hasattr(self, '_provider') or not self._provider:
            return True

        try:
            # Get the internal provider (MeterProvider doesn't have direct flush)
            # We need to flush through the metric readers
            success = self._provider.force_flush(timeout_millis)
            return success
        except Exception as e:
            print(f"[Meter] Error during force flush: {e}")
            # For metrics, we might not have a flush method, so we return True
            return True

    def shutdown(self):
        """Shutdown the meter provider."""
        if hasattr(self, '_provider') and self._provider:
            try:
                self._provider.shutdown()
                print("[Meter] Shutdown completed")
            except Exception as e:
                print(f"[Meter] Error during shutdown: {e}")

    def register_metric(self, definition: MetricDefinition) -> Instrument:
        """Register a new metric."""
        if definition.name in self._metrics:
            return self._metrics[definition.name]

        metric = self.__create_metric(definition)
        self._metrics[definition.name] = metric
        return metric

    def __create_metric(self, definition: MetricDefinition) -> Instrument:
        """Create a metric instrument based on definition."""
        if definition.type == MetricType.COUNTER:
            return self.meter.create_counter(
                name=definition.name,
                unit=definition.unit,
                description=definition.description
            )
        elif definition.type == MetricType.HISTOGRAM:
            return self.meter.create_histogram(
                name=definition.name,
                unit=definition.unit,
                description=definition.description
            )
        elif definition.type == MetricType.UP_DOWN_COUNTER:
            return self.meter.create_up_down_counter(
                name=definition.name,
                unit=definition.unit,
                description=definition.description
            )
        elif definition.type == MetricType.GAUGE:
            # For gauges, we'll create them when needed with callbacks
            return self.meter.create_gauge(
                name=definition.name,
                unit=definition.unit,
                description=definition.description
            )
        else:
            raise ValueError(f"Unknown metric type: {definition.type}")

    def get_metric(self, name: str) -> Optional[Instrument]:
        """Get a registered metric by name."""
        return self._metrics.get(name)
