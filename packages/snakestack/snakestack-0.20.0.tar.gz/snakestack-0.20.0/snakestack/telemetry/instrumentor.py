import logging
import socket
from functools import lru_cache

try:
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.grpc import GrpcInstrumentorClient
    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
    from opentelemetry.instrumentation.logging import LoggingInstrumentor
    from opentelemetry.sdk.resources import SERVICE_NAME, Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import (
        BatchSpanProcessor,
        ConsoleSpanExporter,
        SimpleSpanProcessor,
    )
except ImportError:
    raise RuntimeError("Telemetry extra is not installed. Run `pip install snakestack[telemetry]`.")

logger = logging.getLogger(__name__)


@lru_cache(maxsize=None)
def instrument_app(
    service_name: str,
    test_mode: bool = False,
    enable_logging: bool = True,
    enable_httpx: bool = False,
    enable_grpc: bool = False,
    enable_mongodb: bool = False,
    logging_level: int = logging.INFO,
    otel_disabled: bool = False
) -> None:
    if otel_disabled:
        logger.info("OpenTelemetry is disabled.")
        return

    resource = Resource.create().merge(Resource(attributes={
        SERVICE_NAME: service_name,
        "service.instance.id": socket.gethostname(),
    }))

    provider = TracerProvider(resource=resource)
    exporter = ConsoleSpanExporter() if test_mode else OTLPSpanExporter(insecure=True)
    processor = SimpleSpanProcessor(exporter) if test_mode else BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

    if enable_logging:
        logger.debug("Instrumenting Logging client...")
        LoggingInstrumentor().instrument(set_logging_format=True, log_level=logging_level)

    if enable_httpx:
        logger.debug("Instrumenting HTTPX client...")
        HTTPXClientInstrumentor().instrument()

    if enable_grpc:
        logger.debug("Instrumenting gRPC client...")
        GrpcInstrumentorClient().instrument()

    if enable_mongodb:
        logger.debug("Instrumenting MongoDB client...")
        from snakestack.mongodb.patch import patch_motor_collection_methods
        patch_motor_collection_methods()
