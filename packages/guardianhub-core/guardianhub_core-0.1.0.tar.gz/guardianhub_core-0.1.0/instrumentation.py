"""
Centralized configuration for OpenTelemetry tracing and metrics.
This module provides consistent observability configuration across all services.
"""
import os
from typing import Optional

from opentelemetry import trace, metrics
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource, SERVICE_VERSION, DEPLOYMENT_ENVIRONMENT
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter
import logging

logger = logging.getLogger(__name__)

def configure_instrumentation(
    app,
    service_name: str,
    environment: str = None,
    service_version: str = None,
    otlp_endpoint: str = None,
    enable_console_export: bool = False
):
    """
    Configures OpenTelemetry instrumentation for the FastAPI application.

    Args:
        app: The FastAPI application instance.
        service_name: The name of the service, used for resource identification.
        environment: Deployment environment (e.g., 'dev', 'staging', 'prod').
        service_version: Version of the service.
        otlp_endpoint: OTLP collector endpoint URL.
        enable_console_export: If True, exports traces to console (useful for local development).
    """
    # Get configuration from environment variables if not provided
    environment = environment or os.getenv('ENVIRONMENT', 'development')
    service_version = service_version or os.getenv('SERVICE_VERSION', '0.1.0')
    otlp_endpoint = otlp_endpoint or os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT')

    # Create resource with service name and attributes
    resource = Resource.create(
        attributes={
            SERVICE_NAME: service_name,
            SERVICE_VERSION: service_version,
            DEPLOYMENT_ENVIRONMENT: environment
        }
    )

    # Configure tracing
    try:
        # Set up tracer provider
        tracer_provider = TracerProvider(resource=resource)

        # Add console exporter if enabled
        if enable_console_export:
            console_exporter = ConsoleSpanExporter()
            tracer_provider.add_span_processor(
                BatchSpanProcessor(console_exporter)
            )
            logger.info("Console span exporter enabled")

        # Add OTLP exporter if endpoint is configured
        if otlp_endpoint:
            otlp_exporter = OTLPSpanExporter(endpoint=f"{otlp_endpoint}/v1/traces")
            tracer_provider.add_span_processor(
                BatchSpanProcessor(otlp_exporter)
            )
            logger.info(f"OTLP exporter configured for {otlp_endpoint}")

        trace.set_tracer_provider(tracer_provider)

        # Configure metrics
        metric_readers = []

        if enable_console_export:
            metric_readers.append(PeriodicExportingMetricReader(
                ConsoleMetricExporter(),
                export_interval_millis=5000
            ))

        if otlp_endpoint:
            metric_readers.append(PeriodicExportingMetricReader(
                OTLPMetricExporter(endpoint=f"{otlp_endpoint}/v1/metrics"),
                export_interval_millis=5000
            ))

        if metric_readers:
            metrics.set_meter_provider(MeterProvider(
                resource=resource,
                metric_readers=metric_readers
            ))

        # Instrument FastAPI
        FastAPIInstrumentor.instrument_app(
            app,
            tracer_provider=tracer_provider,
            excluded_urls="/health,/metrics"
        )

        logger.info("OpenTelemetry instrumentation configured successfully")

    except Exception as e:
        logger.error(f"Failed to configure OpenTelemetry instrumentation: {e}", exc_info=True)
        # Continue without instrumentation if configuration fails
