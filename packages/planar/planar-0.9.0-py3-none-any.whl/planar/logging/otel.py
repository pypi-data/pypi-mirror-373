import logging
from typing import Any

from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from pydantic import HttpUrl

from .attributes import ExtraAttributesFilter


def get_otel_collector_handler(
    otel_collector_endpoint: HttpUrl,
    resource_attributes: dict[str, Any] | None = None,
) -> logging.Handler:
    logger_provider = LoggerProvider(
        resource=Resource.create(
            resource_attributes
            or {
                "service.name": "planar-app",
            }
        ),
    )

    otlp_exporter = OTLPLogExporter(
        endpoint=str(otel_collector_endpoint),
        insecure=otel_collector_endpoint.scheme == "http",
    )
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(otlp_exporter))

    set_logger_provider(logger_provider)
    handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
    handler.addFilter(ExtraAttributesFilter())
    return handler


def setup_otel_logging(
    otel_collector_endpoint: HttpUrl,
    resource_attributes: dict[str, Any] | None = None,
) -> None:
    """
    Sets up the OpenTelemetry logging handler and adds it to the root logger.

    Args:
        otel_collector_endpoint: The endpoint of the OpenTelemetry collector.
        resource_attributes: A dictionary of resource attributes to add to the logs.
    """
    handler = get_otel_collector_handler(otel_collector_endpoint, resource_attributes)
    logging.getLogger().addHandler(handler)
