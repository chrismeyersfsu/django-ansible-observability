import os
import logging

from opentelemetry import trace
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.grpc import GrpcInstrumentorServer
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.richconsole import RichConsoleSpanExporter

from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor

from django.conf import settings


def _setup_tracing(service_name=None) -> Resource:
    # Service name is required for traces to be associated with a service
    resource = Resource(attributes={
        SERVICE_NAME: service_name,
    })

    # The TracerProvider is the entry point to tracing
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    # Configure a span exporter (e.g., OTLP)
    otlp_exporter = OTLPSpanExporter()
    processor = BatchSpanProcessor(otlp_exporter)
    provider.add_span_processor(processor)

    if getattr(settings, 'ANSIBLE_OBSERVE_OUTPUT_SPAN_TO_CONSOLE', None):
        rich_exporter = RichConsoleSpanExporter()
        console_processor = BatchSpanProcessor(rich_exporter)
        provider.add_span_processor(console_processor)

    return resource

def _setup_logging(resource: Resource, instrument_non_propagating: bool = True):
    logger_provider = LoggerProvider(resource=resource)
    set_logger_provider(logger_provider)

    # Configure OTLP exporter (adjust endpoint as needed)
    log_exporter = OTLPLogExporter()

    # Add a batch log record processor
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))

    # Integrate with Python's standard logging
    handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
    logging.getLogger().addHandler(handler)

    if instrument_non_propagating:
        # Django apps often configure named loggers with propagate=False for
        # intentional routing (e.g. awx.main.tasks, awx.main.scheduler).
        # Those records never reach the root logger and therefore miss the
        # LoggingHandler above. Attach the handler directly to each such
        # logger so their records still flow into the OTEL log pipeline.
        for _name, _logger in logging.Logger.manager.loggerDict.items():
            if isinstance(_logger, logging.Logger) and not _logger.propagate:
                _logger.addHandler(handler)

def _request_hook(span, request):
    test_name = request.META.get('HTTP_X_TEST_NAME')
    if test_name and span and span.is_recording():
        span.set_attribute('test.name', test_name)


def setup_tracing(service_name=None, instrument_non_propagating: bool = True):
    # Should rename this function to setup_telemetry()

    service_name = service_name or os.environ.get("OTEL_SERVICE_NAME", "aap-generic")

    resource = _setup_tracing(service_name)
    _setup_logging(resource, instrument_non_propagating=instrument_non_propagating)

    DjangoInstrumentor().instrument(request_hook=_request_hook)
    try:
        import psycopg2
        from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
        Psycopg2Instrumentor().instrument()
    except ModuleNotFoundError:
        try:
            import psycopg
            from opentelemetry.instrumentation.psycopg import PsycopgInstrumentor
            PsycopgInstrumentor().instrument()
        except ModuleNotFoundError:
            print("psycopg2 nor psycopg found. Failed to instrument psycopg.")
    RequestsInstrumentor().instrument()
    GrpcInstrumentorServer().instrument()
    LoggingInstrumentor().instrument()
