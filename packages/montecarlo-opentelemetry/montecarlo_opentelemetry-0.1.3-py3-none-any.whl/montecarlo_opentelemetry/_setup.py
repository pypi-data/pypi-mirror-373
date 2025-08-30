from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.instrumentation.threading import ThreadingInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import SpanLimits, SpanProcessor, TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from montecarlo_opentelemetry._span_processor import _MonteCarloSpanProcessor

MONTECARLO_TRACER_NAME = "montecarlo.tracer"


def setup(
    agent_name: str,
    otlp_endpoint: str,
    instrumentors: list[BaseInstrumentor] | None = None,
    span_processor: SpanProcessor | None = None,
    span_limits: SpanLimits | None = None,
) -> None:
    """
    Set up OpenTelemetry tracing with defaults suitable for Monte Carlo.

    The ``setup()`` function initializes a tracer provider, sets it as
    the global tracer provider, and calls ``instrument()`` on all
    provided instrumentors.

    :param: agent_name: Name of the agent, or service. This will be used
        to set the service.name resource.
    :param: otlp_endpoint: OTLP endpoint to export traces to.
    :param: instrumentors: List of instrumentors to initialize..
    :param: span_processor: Span processor to use. If provided, it will
        replace the BatchSpanProcessor that is configured by default.
    :param: span_limits: Span limits to use. If provided, it will replace
        the Monte Carlo default span limits.
    :return: None
    """
    resource = Resource.create(
        {
            SERVICE_NAME: agent_name,
        }
    )
    if span_limits is None:
        span_limits = SpanLimits(max_span_attributes=1024)
    tracer_provider = TracerProvider(resource=resource, span_limits=span_limits)

    mc_span_processor = _MonteCarloSpanProcessor()
    tracer_provider.add_span_processor(mc_span_processor)

    if span_processor is None:
        otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
        span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)

    trace.set_tracer_provider(tracer_provider)

    for instrumentor in instrumentors or []:
        if not instrumentor.is_instrumented_by_opentelemetry:
            instrumentor.instrument()

    threading_instrumentor = ThreadingInstrumentor()
    if not threading_instrumentor.is_instrumented_by_opentelemetry:
        threading_instrumentor.instrument()


def get_tracer() -> trace.Tracer:
    """
    Get a tracer with :data:`MONTECARLO_TRACER_NAME` as name.

    :return: :class:`opentelemetry.trace.Tracer`
    """
    return trace.get_tracer(MONTECARLO_TRACER_NAME)
