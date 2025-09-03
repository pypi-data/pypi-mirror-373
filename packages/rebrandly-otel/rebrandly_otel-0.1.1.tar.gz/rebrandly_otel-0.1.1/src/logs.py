# logs.py
"""Logging implementation for Rebrandly OTEL SDK."""
import logging
from typing import Optional
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import (
    BatchLogRecordProcessor,
    ConsoleLogExporter,
    SimpleLogRecordProcessor
)
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry._logs import set_logger_provider

from src.otel_utils import *


class RebrandlyLogger:
    """Wrapper for OpenTelemetry logging with Rebrandly-specific features."""

    def __init__(self):
        self._logger: Optional[logging.Logger] = None
        self._provider: Optional[LoggerProvider] = None
        self._setup_logging()

    def _setup_logging(self):
        """Initialize logging with configured exporters."""

        # Create provider with resource
        self._provider = LoggerProvider(resource=create_resource())

        # Add console exporter for local debugging
        if is_otel_debug():
            console_exporter = ConsoleLogExporter()
            self._provider.add_log_record_processor(SimpleLogRecordProcessor(console_exporter))

        # Add OTLP exporter if configured
        if get_otlp_endpoint():
            otlp_exporter = OTLPLogExporter(endpoint=get_otlp_endpoint())
            batch_processor = BatchLogRecordProcessor(otlp_exporter, export_timeout_millis=get_millis_batch_time())
            self._provider.add_log_record_processor(batch_processor)

        # Set as global provider
        set_logger_provider(self._provider)

        # Configure standard logging
        self._configure_standard_logging()

    def _configure_standard_logging(self):
        """Configure standard Python logging with OTEL handler."""
        # Set up basic configuration
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            stream=sys.stdout,
            force=True
        )

        # Add OTEL handler
        otel_handler = LoggingHandler(logger_provider=self._provider)
        otel_handler.setLevel(logging.INFO)

        # Get root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(otel_handler)

        # Create service-specific logger
        self._logger = logging.getLogger(get_service_name())


    @property
    def logger(self) -> logging.Logger:
        """Get the standard Python logger."""
        if not self._logger:
            self._logger = logging.getLogger(get_service_name())
        return self._logger

    def force_flush(self, timeout_millis: int = 5000) -> bool:
        """
        Force flush all pending logs.

        Args:
            timeout_millis: Maximum time to wait for flush in milliseconds

        Returns:
            True if flush succeeded, False otherwise
        """
        if not self._provider:
            return True

        try:
            # Force flush the logger provider
            success = self._provider.force_flush(timeout_millis)

            # Also flush Python's logging handlers
            if self._logger:
                for handler in self._logger.handlers:
                    if hasattr(handler, 'flush'):
                        handler.flush()

            return success
        except Exception as e:
            print(f"[Logger] Error during force flush: {e}")
            return False

    def shutdown(self):
        """Shutdown the logger provider."""
        if self._provider:
            try:
                self._provider.shutdown()
                print("[Logger] Shutdown completed")
            except Exception as e:
                print(f"[Logger] Error during shutdown: {e}")
