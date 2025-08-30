from montecarlo_opentelemetry._llm import (
    add_llm_completions,
    add_llm_operation,
    add_llm_prompts,
    add_llm_provider,
    add_llm_request_model,
    add_llm_response_model,
    add_llm_tokens,
    create_llm_span,
)
from montecarlo_opentelemetry._setup import (
    get_tracer,
    setup,
)
from montecarlo_opentelemetry._tracing import (
    create_span_with_attributes,
    create_span_with_tags,
    create_span_with_task,
    create_span_with_workflow,
    trace,
    trace_with_attributes,
    trace_with_tags,
    trace_with_task,
    trace_with_workflow,
)

__all__ = [
    "setup",
    "get_tracer",
    "trace",
    "trace_with_tags",
    "trace_with_attributes",
    "trace_with_workflow",
    "trace_with_task",
    "create_span_with_tags",
    "create_span_with_attributes",
    "create_span_with_workflow",
    "create_span_with_task",
    "create_llm_span",
    "add_llm_provider",
    "add_llm_operation",
    "add_llm_request_model",
    "add_llm_response_model",
    "add_llm_prompts",
    "add_llm_completions",
    "add_llm_tokens",
]
