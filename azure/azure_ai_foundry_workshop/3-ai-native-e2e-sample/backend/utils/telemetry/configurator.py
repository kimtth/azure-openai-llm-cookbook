"""
Telemetry configuration module for Clinical Trials Monitor.

This module configures OpenTelemetry tracing for monitoring key operations
in the trial event simulation and processing pipeline.
"""

import os
import logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes

logger = logging.getLogger(__name__)

def configure_telemetry():
    """Configure OpenTelemetry tracing."""
    if os.getenv("OTEL_SDK_DISABLED", "false").lower() == "true":
        logger.info("OpenTelemetry SDK is disabled")
        return

    # Create resource attributes
    attributes = {
        ResourceAttributes.SERVICE_NAME: os.getenv("OTEL_SERVICE_NAME", "clinical-trials-monitor"),
        ResourceAttributes.DEPLOYMENT_ENVIRONMENT: os.getenv("DEPLOYMENT_ENVIRONMENT", "development")
    }
    
    # Add custom resource attributes
    if resource_attrs := os.getenv("OTEL_RESOURCE_ATTRIBUTES"):
        for attr in resource_attrs.split(","):
            key, value = attr.split("=")
            attributes[key.strip()] = value.strip()
    
    resource = Resource.create(attributes)
    logger.debug("Resource attributes: %s", attributes)

    # Initialize tracer provider with resource
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    # Configure OTLP exporter if endpoint is provided
    if endpoint := os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
        protocol = os.getenv("OTEL_EXPORTER_OTLP_PROTOCOL", "http/protobuf")
        logger.info("🔌 Configuring OTLP exporter with protocol: %s", protocol)
        
        otlp_exporter = OTLPSpanExporter(
            endpoint=endpoint,
            insecure=True  # For local development
        )
        span_processor = BatchSpanProcessor(otlp_exporter)
        provider.add_span_processor(span_processor)
        logger.info("✅ Configured OTLP exporter with endpoint: %s", endpoint)
    else:
        logger.warning("OTEL_EXPORTER_OTLP_ENDPOINT not set, telemetry export disabled")

    logger.info("✅ OpenTelemetry configuration complete")
