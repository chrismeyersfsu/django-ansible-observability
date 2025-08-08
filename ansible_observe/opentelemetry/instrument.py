import os

from opentelemetry import trace
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.richconsole import RichConsoleSpanExporter


from django.conf import settings


def setup_tracing():
    # Service name is required for traces to be associated with a service
    resource = Resource(attributes={
        SERVICE_NAME: os.environ.get("OTEL_SERVICE_NAME", "aap-generic")
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

    DjangoInstrumentor().instrument()
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
