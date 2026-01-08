"""Telemetry module for Clinical Trials Monitor."""

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from .configurator import configure_telemetry

# Initialize tracer
tracer = trace.get_tracer(__name__)

__all__ = ['tracer', 'Status', 'StatusCode', 'configure_telemetry']
