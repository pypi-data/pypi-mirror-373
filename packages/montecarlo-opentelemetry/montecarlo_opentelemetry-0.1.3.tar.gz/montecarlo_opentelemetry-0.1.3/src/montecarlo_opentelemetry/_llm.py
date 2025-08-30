import contextlib
from typing import List

from opentelemetry.trace import Span

from montecarlo_opentelemetry._setup import get_tracer


@contextlib.contextmanager
def create_llm_span(
    span_name: str,
    provider: str,
    model: str,
    operation: str,
    prompts_to_record: List[dict[str, str]],
):
    """
    Context manager to create a span for an LLM operation.

    Should only be used when the LLM call is not automatically traced.

    Once the LLM call is made, additional attributes from the response
    can be added to the span using the provided helper functions:
        - add_llm_response_model()
        - add_llm_completions()
        - add_llm_tokens()

    :param span_name: Name of the span.
    :param provider: Provider name.
    :param model: Model name.
    :param operation: Operation name.
    :param prompts_to_record: List of prompts to record as attributes.
        This will usually be the same list of prompts sent to the LLM.
        But, if you need to redact sensitive information before
        recording them as attributes, you can pass in a modified list
        of prompts to be added to the span.
    """
    tracer = get_tracer()
    with tracer.start_as_current_span(span_name) as span:
        add_llm_provider(span, provider)
        add_llm_request_model(span, model)
        add_llm_operation(span, operation)
        add_llm_prompts(span, prompts_to_record)
        yield span


def add_llm_provider(span: Span, provider: str):
    """
    Add the LLM provider attribute to the span.

    :param span: Span.
    :param provider: Provider name.
    """
    span.set_attribute(key="gen_ai.provider.name", value=provider)


def add_llm_operation(span: Span, operation: str):
    """
    Add the LLM operation attribute to the span.

    :param span: Span.
    :param operation: Operation name.
    """
    span.set_attribute(key="gen_ai.operation.name", value=operation)


def add_llm_request_model(span: Span, model: str):
    """
    Add the LLM request model attribute to the span.

    :param span: Span.
    :param model: Request model name.
    """
    span.set_attribute(key="gen_ai.request.model", value=model)


def add_llm_response_model(span: Span, model: str):
    """
    Add the LLM response model attribute to the span.

    :param span: Span.
    :param model: Response model name.
    """
    span.set_attribute(key="gen_ai.response.model", value=model)


def add_llm_prompts(span: Span, prompts: List[dict[str, str]]):
    """
    Add the LLM prompts to the span as attributes.

    :param span: Span.
    :param prompts: List of prompts. Expected keys in each prompt are
        "role" and "content".
    """
    for idx, prompt in enumerate(prompts):
        span.set_attribute(
            key=f"gen_ai.prompt.{idx}.role", value=prompt.get("role", "")
        )
        span.set_attribute(
            key=f"gen_ai.prompt.{idx}.content", value=prompt.get("content", "")
        )


def add_llm_completions(span: Span, completions: List[dict[str, str]]):
    """
    Add the LLM completions to the span as attributes.

    :param span: Span.
    :param completions: List of completions. Expected keys in each completion are
        "role" and "content".
    """
    for idx, completion in enumerate(completions):
        span.set_attribute(
            key=f"gen_ai.completion.{idx}.role", value=completion.get("role", "")
        )
        span.set_attribute(
            key=f"gen_ai.completion.{idx}.content", value=completion.get("content", "")
        )


def add_llm_tokens(
    span: Span,
    prompt_tokens: int,
    completion_tokens: int,
    total_tokens: int,
    cache_creation_input_tokens: int,
    cache_read_input_tokens: int,
):
    """
    Add the LLM tokens to the span as attributes.

    :param span: Span.
    :param prompt_tokens: Number of tokens in the prompt.
    :param completion_tokens: Number of tokens in the completion.
    :param total_tokens: Total number of tokens.
    :param cache_creation_input_tokens: Number of tokens in the cache creation input.
    :param cache_read_input_tokens: Number of tokens in the cache read input.
    """
    span.set_attribute(key="gen_ai.usage.input_tokens", value=prompt_tokens)
    span.set_attribute(key="gen_ai.usage.output_tokens", value=completion_tokens)
    span.set_attribute(key="llm.usage.total_tokens", value=total_tokens)
    span.set_attribute(
        key="gen_ai.usage.cache_creation_input_tokens",
        value=cache_creation_input_tokens,
    )
    span.set_attribute(
        key="gen_ai.usage.cache_read_input_tokens", value=cache_read_input_tokens
    )
