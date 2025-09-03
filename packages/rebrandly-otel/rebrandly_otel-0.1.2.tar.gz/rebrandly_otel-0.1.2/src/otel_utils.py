
# otel_utils.py

import os
import sys

from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.attributes import service_attributes
from opentelemetry.semconv._incubating.attributes import process_attributes, deployment_attributes

def create_resource(name: str = None, version: str = None) -> Resource:

    if name is None:
        name = get_service_name()
    if version is None:
        version = get_service_version()

    resource = Resource.create(
        {
            service_attributes.SERVICE_NAME: name,
            service_attributes.SERVICE_VERSION: version,
            process_attributes.PROCESS_RUNTIME_VERSION: f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            deployment_attributes.DEPLOYMENT_ENVIRONMENT: os.environ.get('ENV', os.environ.get('ENVIRONMENT', os.environ.get('NODE_ENV', 'local')))
        }
    )
    return resource


def get_service_name(service_name: str = None) -> str:
    if service_name is None:
        return os.environ.get('OTEL_SERVICE_NAME', 'default-service-python')
    return service_name


def get_service_version(service_version: str = None) -> str:
    if service_version is None:
        return os.environ.get('OTEL_SERVICE_VERSION', '1.0.0')
    return service_version


def get_otlp_endpoint(otlp_endpoint: str = None) -> str:
    if otlp_endpoint is None:
        return os.environ.get('OTEL_EXPORTER_OTLP_ENDPOINT', None)
    return otlp_endpoint

def is_otel_debug() -> bool:
    return os.environ.get('OTEL_DEBUG', 'false').lower() == 'true'


def get_millis_batch_time():
    try:
        return int(os.environ.get('BATCH_EXPORT_TIME_MILLIS', 100))
    except:
        return 5000