# Rebrandly OpenTelemetry SDK for Python

A comprehensive OpenTelemetry instrumentation SDK designed specifically for Rebrandly services, with built-in support for AWS Lambda functions and message processing.

## Overview

The Rebrandly OpenTelemetry SDK provides a unified interface for distributed tracing, metrics collection, and structured logging across Python applications. It offers automatic instrumentation for AWS Lambda functions, simplified span management, and seamless integration with OTLP-compatible backends.

## Installation

```bash
pip install rebrandly-otel-sdk
```

### Dependencies

- `opentelemetry-api`
- `opentelemetry-sdk`
- `opentelemetry-exporter-otlp-proto-grpc`
- `opentelemetry-semantic-conventions`
- `psutil` (for system metrics)

## Configuration

The SDK is configured through environment variables:

| Variable                           | Description | Default |
|------------------------------------|-------------|---------|
| `OTEL_SERVICE_NAME`                | Service identifier | `default-service-python` |
| `OTEL_SERVICE_VERSION`             | Service version | `1.0.0` |
| `OTEL_EXPORTER_OTLP_ENDPOINT`      | OTLP collector endpoint | `None` |
| `OTEL_DEBUG`                       | Enable console debugging | `false` |
| `BATCH_EXPORT_TIME_MILLIS`         | Batch export interval | `100` |
| `ENV` or `ENVIRONMENT` or `NODE_ENV`       | Deployment environment | `local` |

## Core Components

### RebrandlyOTEL Class

The main entry point for all telemetry operations. Implements a singleton pattern to ensure consistent instrumentation across your application.

#### Properties

- **`tracer`**: Returns the `RebrandlyTracer` instance for distributed tracing
- **`meter`**: Returns the `RebrandlyMeter` instance for metrics collection
- **`logger`**: Returns the configured Python logger with OpenTelemetry integration

#### Initialization

The SDK auto-initializes as soon as you embed it.

### Key Methods

#### `span(name, attributes=None, kind=SpanKind.INTERNAL, message=None)`

Context manager for creating traced spans with automatic error handling and status management.

#### `lambda_handler(name=None, attributes=None, kind=SpanKind.CONSUMER, auto_flush=True, skip_aws_link=True)`

Decorator for AWS Lambda functions with automatic instrumentation, metrics collection, and telemetry flushing.

#### `aws_message_handler(name=None, attributes=None, kind=SpanKind.CONSUMER, auto_flush=True)`

Decorator for processing individual AWS messages (SQS/SNS) with context propagation.

#### `aws_message_span(name, message=None, attributes=None, kind=SpanKind.CONSUMER)`

Context manager for creating spans from AWS messages with automatic context extraction.

#### `force_flush(start_datetime=None, timeout_millis=1000)`

Forces all pending telemetry data to be exported. Critical for serverless environments.

#### `shutdown()`

Gracefully shuts down all OpenTelemetry components.

## Built-in Metrics

The SDK automatically registers and tracks the following metrics:

### Standard Metrics

- **`invocations`** (Counter): Total number of function invocations
- **`successful_invocations`** (Counter): Number of successful completions
- **`error_invocations`** (Counter): Number of failed invocations
- **`duration`** (Histogram): Execution duration in milliseconds
- **`cpu_usage_percentage`** (Gauge): CPU utilization percentage
- **`memory_usage_bytes`** (Gauge): Memory usage in bytes

### Global Metrics Access

```python
from rebrandly_otel import meter

# Access pre-configured metrics
meter.GlobalMetrics.invocations.add(1, {'function': 'my_function'})
meter.GlobalMetrics.duration.record(150.5, {'source': 'api'})
```

## Tracing Features

### Automatic Context Propagation

The SDK automatically extracts and propagates trace context from:
- AWS SQS message attributes
- AWS SNS message attributes
- HTTP headers
- Custom carriers

### Span Attributes

Lambda spans automatically include:
- `faas.trigger`: Detected trigger type (sqs, sns, api_gateway, etc.)
- `faas.execution`: AWS request ID
- `faas.id`: Function ARN
- `cloud.provider`: Always "aws" for Lambda
- `cloud.platform`: Always "aws_lambda" for Lambda

### Exception Handling

Spans automatically capture exceptions with:
- Full exception details and stack traces
- Automatic status code setting
- Exception events in the span timeline

## Logging Integration

The SDK integrates with Python's standard logging module:

```python
from rebrandly_otel import logger

# Use as a standard Python logger
logger.info("Processing started", extra={"request_id": "123"})
logger.error("Processing failed", exc_info=True)
```

Features:
- Automatic trace context injection
- Structured logging support
- Console and OTLP export
- Log level configuration via environment

## AWS Lambda Support

### Trigger Detection

Automatically detects and labels Lambda triggers:
- API Gateway (v1 and v2)
- SQS
- SNS
- S3
- Kinesis
- DynamoDB
- EventBridge
- Batch

### Automatic Metrics

For Lambda functions, the SDK automatically captures:
- Function duration
- Memory usage
- CPU utilization
- Invocation counts by status

### Context Extraction

Automatically extracts trace context from:
- SQS MessageAttributes
- SNS MessageAttributes (including nested format)
- Custom message attributes

## Performance Considerations

### Batch Processing

- Configurable batch sizes and intervals
- Automatic batching for traces, metrics, and logs
- Optimized for high-throughput scenarios

### Lambda Optimization

- Automatic flushing before function freeze
- Minimal cold start impact
- Efficient memory usage
- Configurable timeout handling

## Export Formats

### Supported Exporters

- **OTLP/gRPC**: Primary export format for production
- **Console**: Available for local development and debugging

## Thread Safety

All components are thread-safe and can be used in multi-threaded applications:
- Singleton pattern ensures single initialization
- Thread-safe metric recording
- Concurrent span creation support

## Resource Attributes

Automatically includes:
- Service name and version
- Python runtime version
- Deployment environment
- Custom resource attributes via environment

## Error Handling

- Graceful degradation when OTLP endpoint unavailable
- Non-blocking telemetry operations
- Automatic retry with exponential backoff
- Comprehensive error logging

## Compatibility

- Python 3.7+
- AWS Lambda runtime support
- Compatible with OpenTelemetry Collector
- Works with any OTLP-compatible backend

## Examples

### Lambda - Send SNS / SQS message
```python
import os
import json
import boto3
from rebrandly_otel import otel, lambda_handler, logger

sqs = boto3.client('sqs')
QUEUE_URL = os.environ.get('SQS_URL')

@lambda_handler("sqs_sender")
def handler(event, context):
    logger.info("Starting SQS message send")

    # Get trace context for propagation
    trace_attrs = otel.tracer.get_attributes_for_aws_from_context()

    # Send message with trace context
    response = sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=json.dumps({"data": "test message"}),
        MessageAttributes=trace_attrs
    )

    logger.info(f"Sent SQS message: {response['MessageId']}")

    return {
        'statusCode': 200,
        'body': json.dumps({'messageId': response['MessageId']})
    }
```

### Lambda Receive SQS message
```python
import json
from rebrandly_otel import lambda_handler, logger, aws_message_span

@lambda_handler(name="sqs_receiver")
def handler(event, context):
    for record in event['Records']:
        # Process each message with trace context
        process_message(record)

def process_message(record):
    with aws_message_span("process_message_sqs_receiver", message=record) as s:
        logger.info(f"Processing message: {record['messageId']}")

        # Parse message body
        body = json.loads(record['body'])
        logger.info(f"Message data: {body}")
```

### Lambda Receive SNS message (record specific event)
```python
import json
from rebrandly_otel import lambda_handler, logger, aws_message_span

@lambda_handler(name="sns_receiver")
def handler(event, context):
    for record in event['Records']:
        # Process each message with trace context
        process_message(record)

def process_message(record):
    message = json.loads(record['Sns']['Message'])
    if message['event'] == 'whitelisted-event':
        with aws_message_span("process_message_sns_receiver", message=record) as s:
            logger.info(f"Processing message: {record['messageId']}")
    
            # Parse message body
            body = json.loads(record['body'])
            logger.info(f"Message data: {body}")
```

### More examples
You can find More examples [here](examples)

## License

Rebrandly Python SDK is released under the MIT License.

## Build and Deploy

> build --version
> 
> twine --version

If `build` gives you an error, try:

> pyproject-build --version
>
> twine --version