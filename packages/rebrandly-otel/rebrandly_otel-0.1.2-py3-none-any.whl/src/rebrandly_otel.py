# rebrandly_otel.py
"""
Rebrandly OpenTelemetry SDK - Simplified instrumentation for Rebrandly services.
"""
import time
import psutil
import functools
from contextlib import contextmanager
from datetime import datetime
from opentelemetry.trace import Status, StatusCode, SpanKind
from typing import Optional, Dict, Any, Callable, TypeVar
from opentelemetry import baggage, propagate, context

from src.traces import RebrandlyTracer
from src.metrics import RebrandlyMeter
from src.logs import RebrandlyLogger


T = TypeVar('T')

class RebrandlyOTEL:
    """Main entry point for Rebrandly's OpenTelemetry instrumentation."""

    _instance: Optional['RebrandlyOTEL'] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._tracer: Optional[RebrandlyTracer] = None
            self._meter: Optional[RebrandlyMeter] = None
            self._logger: Optional[RebrandlyLogger] = None
            self.__class__._initialized = True

    def initialize(self, **kwargs) -> 'RebrandlyOTEL':
        # Force initialization of components
        _ = self.tracer
        _ = self.meter
        _ = self.logger

        return self

    @property
    def tracer(self) -> RebrandlyTracer:
        """Get the tracer instance."""
        if self._tracer is None:
            self._tracer = RebrandlyTracer()
        return self._tracer

    @property
    def meter(self) -> RebrandlyMeter:
        """Get the meter instance."""
        if self._meter is None:
            self._meter = RebrandlyMeter()
        return self._meter

    @property
    def logger(self) -> RebrandlyLogger:
        """Get the logger instance."""
        if self._logger is None:
            self._logger = RebrandlyLogger()
        return self._logger

    # Convenience methods for common operations

    @contextmanager
    def span(self,
             name: str,
             attributes: Optional[Dict[str, Any]] = None,
             kind: SpanKind = SpanKind.INTERNAL,
             message=None):
        """Create a span using context manager."""
        with self.tracer.start_span(name, attributes=attributes, kind=kind) as span:
            try:
                yield span
                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    def trace_decorator(self,
                        name: Optional[str] = None,
                        attributes: Optional[Dict[str, Any]] = None,
                        kind: SpanKind = SpanKind.INTERNAL) -> Callable[[T], T]:
        """Decorator for tracing functions."""
        def decorator(func: T) -> T:
            span_name = name or f"{func.__module__}.{func.__name__}"

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                with self.span(span_name, attributes=attributes, kind=kind):
                    return func(*args, **kwargs)

            return wrapper
        return decorator

    def lambda_handler(self,
                       name: Optional[str] = None,
                       attributes: Optional[Dict[str, Any]] = None,
                       kind: SpanKind = SpanKind.CONSUMER,
                       auto_flush: bool = True,
                       skip_aws_link: bool = True):
        """
        Decorator specifically for Lambda handlers with automatic flushing.

        Args:
            name: Optional span name (defaults to 'lambda.{function_name}')
            attributes: Additional span attributes
            kind: Span kind (defaults to SERVER)
            auto_flush: If True, automatically flush after handler completes

        Usage:
            @lambda_handler()
            def my_handler(event, context): ...

            @lambda_handler(name="custom_span_name")
            def my_handler(event, context): ...

            @lambda_handler(name="my_span", attributes={"env": "prod"})
            def my_handler(event, context): ...
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(event=None, context=None):
                # Determine span name
                span_name = name or f"lambda.{func.__name__}"
                start_func = datetime.now()

                # Build span attributes
                span_attributes = attributes or {}

                span_attributes['faas.trigger'] = self._detect_lambda_trigger(event)

                # Add Lambda-specific attributes if context is available
                if context is not None:
                    span_attributes.update({
                        "faas.execution": getattr(context, 'aws_request_id', 'unknown'),
                        "faas.id": getattr(context, 'function_name', 'unknown'),
                        "cloud.provider": "aws",
                        "cloud.platform": "aws_lambda"
                    })

                result = None
                try:
                    # Increment invocations counter
                    self.meter.GlobalMetrics.invocations.add(1, {'function': span_name})

                    # Create span and execute function
                    record = None
                    span_function = self.span
                    if not skip_aws_link and event is not None and 'Records' in event and len(event['Records']) > 0 and 'MessageAttributes' in event['Records'][0]:
                        span_function = self.aws_message_span
                        record = event['Records'][0]

                    with span_function(span_name, message=record, attributes=span_attributes, kind=kind) as span_context:
                        # Add event type as span event
                        if event is not None:
                            span_context.add_event("lambda.invocation.start", attributes={"event.type": type(event).__name__})

                            result = func(event, context)
                        else:
                            result = func()

                        # Add result information if applicable
                        if isinstance(result, dict):
                            if 'statusCode' in result:
                                span_context.set_attribute("http.status_code", result['statusCode'])
                                # Set span status based on HTTP status code
                                if result['statusCode'] >= 400:
                                    span_context.set_status(Status(StatusCode.ERROR, f"HTTP {result['statusCode']}"))
                                else:
                                    span_context.set_status(Status(StatusCode.OK))

                        # Increment success counter
                        self.meter.GlobalMetrics.successful_invocations.add(1, {'function': span_name})

                        return result

                except Exception as e:
                    # Increment error counter
                    self.meter.GlobalMetrics.error_invocations.add(1, {'function': span_name, 'error': type(e).__name__})
                    raise

                finally:
                    if auto_flush:
                        self.logger.logger.info(f"[OTEL] Lambda handler '{span_name}' completed, flushing telemetry...")
                        self.force_flush(start_datetime=start_func)

            return wrapper
        return decorator

    def aws_message_handler(self,
                       name: Optional[str] = None,
                       attributes: Optional[Dict[str, Any]] = None,
                       kind: SpanKind = SpanKind.CONSUMER,
                       auto_flush: bool = True):
        """
        require a record object parameter to the function
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(record=None, *args, **kwargs):
                # Determine span name
                span_name = name or f"lambda.{func.__name__}"
                start_func = datetime.now()

                # Build span attributes
                span_attributes = attributes or {}

                result = None
                try:
                    # Increment invocations counter
                    print('XXX 2')
                    self.meter.GlobalMetrics.invocations.add(1, {'handler': span_name})

                    # Create span and execute function
                    span_function = self.span
                    if record is not None and 'MessageAttributes' in record:
                        span_function = self.aws_message_span

                    with span_function(span_name, message=record, attributes=span_attributes, kind=kind) as span_context:
                        # Execute the actual handler function
                        result = func(record, *args, **kwargs)

                        # Add result attributes if applicable
                        if result and isinstance(result, dict):
                            if 'statusCode' in result:
                                span_context.set_attribute("handler.status_code", result['statusCode'])

                                # Set span status based on status code
                                if result['statusCode'] >= 400:
                                    span_context.set_status(
                                        Status(StatusCode.ERROR, f"Handler returned {result['statusCode']}")
                                    )
                                else:
                                    span_context.set_status(Status(StatusCode.OK))

                            # Add custom result attributes if present
                            if 'processed' in result:
                                span_context.set_attribute("handler.processed", result['processed'])
                            if 'skipped' in result:
                                span_context.set_attribute("handler.skipped", result['skipped'])

                        # Add completion event
                        span_context.add_event("lambda.invocation.complete", attributes={
                            "handler.success": True
                        })

                        # Increment success counter
                        self.meter.GlobalMetrics.successful_invocations.add(1, {'handler': span_name})

                        return result

                except Exception as e:
                    # Increment error counter
                    self.meter.GlobalMetrics.error_invocations.add(1, {'handler': span_name, 'error': type(e).__name__})

                    # Record the exception in the span
                    span_context.record_exception(e)
                    span_context.set_status(Status(StatusCode.ERROR, str(e)))

                    # Re-raise the exception
                    raise

                finally:
                    if auto_flush:
                        self.logger.logger.info(f"[OTEL] Lambda handler '{span_name}' completed, flushing telemetry...")
                        self.force_flush(start_datetime=start_func)

            return wrapper
        return decorator

    def force_flush(self, start_datetime: datetime=None, timeout_millis: int = 1000) -> bool:
        """
        Force flush all telemetry data.
        This is CRITICAL for Lambda functions to ensure data is sent before function freezes.

        Args:
            timeout_millis: Maximum time to wait for flush in milliseconds

        Returns:
            True if all flushes succeeded, False otherwise
        """
        success = True

        if start_datetime is not None:
            end_func = datetime.now()
            duration = (end_func - start_datetime).total_seconds() * 1000
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()

            # Record metrics using standardized names
            self.meter.GlobalMetrics.duration.record(duration, {'source': 'force_flush'})
            self.meter.GlobalMetrics.memory_usage_bytes.set(memory.used)
            self.meter.GlobalMetrics.cpu_usage_percentage.set(cpu_percent)
            self.logger.logger.info(f"[OTEL] Function duration: {duration}ms, Memory usage: {memory.percent}%, CPU usage: {cpu_percent}%")

        try:
            # Flush traces
            if self._tracer:
                if not self._tracer.force_flush(timeout_millis):
                    success = False

            # Flush metrics
            if self._meter:
                if not self._meter.force_flush(timeout_millis):
                    success = False

            # Flush logs
            if self._logger:
                if not self._logger.force_flush(timeout_millis):
                    success = False

            # Add a small delay to ensure network operations complete
            time.sleep(0.1)

        except Exception as e:
            success = False

        return success

    def shutdown(self):
        """
        Shutdown all OTEL components gracefully.
        Call this at the end of your Lambda handler if you want to ensure clean shutdown.
        """
        try:
            if self._tracer:
                self._tracer.shutdown()
            if self._meter:
                self._meter.shutdown()
            if self._logger:
                self._logger.shutdown()
            self.logger.logger.info("[OTEL] Shutdown completed")
        except Exception as e:
            self.logger.logger.info(f"[OTEL] Error during shutdown: {e}")

    def _detect_lambda_trigger(self, event: Any) -> str:
        """Detect Lambda trigger type from event."""
        if not event or not isinstance(event, dict):
            return 'direct'

        if 'Records' in event:
            first_record = event['Records'][0] if event['Records'] else None
            if first_record:
                event_source = first_record.get('eventSource', '')
                if event_source == 'aws:sqs':
                    return 'sqs'
                elif event_source == 'aws:sns':
                    return 'sns'
                elif event_source == 'aws:s3':
                    return 's3'
                elif event_source == 'aws:kinesis':
                    return 'kinesis'
                elif event_source == 'aws:dynamodb':
                    return 'dynamodb'

        if 'httpMethod' in event:
            return 'api_gateway'
        if 'requestContext' in event and 'http' in event.get('requestContext', {}):
            return 'api_gateway_v2'
        if event.get('source') == 'aws.events':
            return 'eventbridge'
        if event.get('source') == 'aws.scheduler':
            return 'eventbridge_scheduler'
        if 'jobName' in event:
            return 'batch'

        return 'unknown'

    def set_baggage(self, key: str, value: str):
        """Set baggage item."""
        return baggage.set_baggage(key, value)

    def get_baggage(self, key: str) -> Optional[str]:
        """Get baggage item."""
        return baggage.get_baggage(key)

    def inject_context(self, carrier: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Inject trace context into headers for outbound requests."""
        if carrier is None:
            carrier = {}
        propagate.inject(carrier)
        return carrier

    def extract_context(self, carrier: Dict[str, Any]) -> context.Context:
        """Extract trace context from incoming request headers."""
        return propagate.extract(carrier)

    def attach_context(self, carrier: Dict[str, Any]) -> object:
        """Extract and attach context, returning a token for cleanup."""
        ctx = self.extract_context(carrier)
        return context.attach(ctx)

    def detach_context(self, token):
        """Detach a previously attached context."""
        context.detach(token)

    @contextmanager
    def aws_message_span(self,
                         name: str,
                         message: Dict[str, Any]=None,
                         attributes: Optional[Dict[str, Any]] = None,
                         kind: SpanKind = SpanKind.CONSUMER):
        """Create span from AWS message with extracted context."""
        # Extract context from the message if it contains trace context
        token = None
        if message and isinstance(message, dict):
            carrier = {}

            # Check for trace context in different possible locations
            if 'MessageAttributes' in message:
                # SQS format
                for key, value in message.get('MessageAttributes', {}).items():
                    if isinstance(value, dict) and 'StringValue' in value:
                        carrier[key] = value['StringValue']
            elif 'Sns' in message and 'MessageAttributes' in message['Sns']:
                # SNS format - MessageAttributes are nested under 'Sns'
                for key, value in message['Sns'].get('MessageAttributes', {}).items():
                    if isinstance(value, dict):
                        # SNS uses 'Value' instead of 'StringValue'
                        if 'Value' in value:
                            carrier[key] = value['Value']
                        elif 'StringValue' in value:
                            carrier[key] = value['StringValue']
            elif 'messageAttributes' in message:
                # Alternative format
                for key, value in message.get('messageAttributes', {}).items():
                    if isinstance(value, dict) and 'stringValue' in value:
                        carrier[key] = value['stringValue']

            # If we found trace context, attach it
            if carrier:
                token = self.attach_context(carrier)

        # Create a span with the potentially extracted context
        combined_attributes = attributes or {}

        # Add message-specific attributes
        if message and isinstance(message, dict):
            # Add SNS-specific attributes
            if 'Sns' in message:
                sns_msg = message['Sns']
                if 'MessageId' in sns_msg:
                    combined_attributes['messaging.message_id'] = sns_msg['MessageId']
                if 'TopicArn' in sns_msg:
                    combined_attributes['messaging.destination'] = sns_msg['TopicArn']
                combined_attributes['messaging.system'] = 'aws_sns'
            # Add SQS-specific attributes
            elif 'messageId' in message:
                combined_attributes['messaging.message_id'] = message['messageId']
                if 'eventSource' in message:
                    combined_attributes['messaging.system'] = message['eventSource']

            # Add common attributes
            if 'awsRegion' in message:
                combined_attributes['cloud.region'] = message['awsRegion']

        try:
            # Use the regular span method which properly handles context
            with self.span(name, attributes=combined_attributes, kind=kind) as span:
                yield span
        finally:
            # Detach context if we attached one
            if token:
                self.detach_context(token)


# Create Singleton instance
otel = RebrandlyOTEL()

# Export commonly used functions
span = otel.span
aws_message_span = otel.aws_message_span
traces = otel.trace_decorator
tracer = otel.tracer
meter = otel.meter
logger = otel.logger.logger
lambda_handler = otel.lambda_handler
aws_message_handler = otel.aws_message_handler
initialize = otel.initialize
inject_context = otel.inject_context
extract_context = otel.extract_context
attach_context = otel.attach_context
detach_context = otel.detach_context
force_flush = otel.force_flush
shutdown = otel.shutdown