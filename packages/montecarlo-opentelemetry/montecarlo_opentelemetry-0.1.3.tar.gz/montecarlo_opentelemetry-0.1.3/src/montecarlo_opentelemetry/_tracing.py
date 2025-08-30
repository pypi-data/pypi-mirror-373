import contextlib

import wrapt
from opentelemetry import baggage, context

from montecarlo_opentelemetry._setup import get_tracer


def trace(span_name: str):
    """
    Decorator to trace a function or method.

    This decorator will create a span and set it as the current span in
    the current tracer's context.

    :param span_name: Name of the span.
    """

    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        tracer = get_tracer()
        with tracer.start_as_current_span(span_name):
            return wrapped(*args, **kwargs)

    return wrapper


def trace_with_attributes(
    span_name: str, attributes: dict[str, str | int | float | bool]
):
    """
    Decorator to trace a function or method with attributes.

    This decorator will create a span and set it as the current span in
    the current tracer's context.

    For each attribute, it will prepend the key with the "montecarlo."
    prefix. It will add the attributes to the current span, and propagate
    them to child spans.

    :param span_name: Name of the span.
    :param attributes: Dictionary of attributes to add to the span.
    """

    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        ctx = context.get_current()

        for key, value in attributes.items():
            mc_key = f"montecarlo.{key}"
            ctx = baggage.set_baggage(mc_key, value, ctx)

        token = context.attach(ctx)
        try:
            tracer = get_tracer()
            with tracer.start_as_current_span(span_name):
                return wrapped(*args, **kwargs)
        finally:
            context.detach(token)

    return wrapper


def trace_with_tags(span_name: str, tags: list[str]):
    """
    Decorator to trace a function or method with tags.

    This decorator will create a span and set it as the current span in
    the current tracer's context. It merges the provided tags with any
    existing tags from the current context and propagates them to child
    spans.

    Tags are stored as a sorted comma-separated string in baggage under
    the key "montecarlo.tags".

    :param span_name: Name of the span.
    :param tags: List of tags to add to the span.
    """

    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        curr_ctx = context.get_current()

        # Merge existing tags with new tags.
        existing_tags = []
        curr_tags = baggage.get_baggage("montecarlo.tags", curr_ctx)
        if curr_tags and isinstance(curr_tags, str):
            existing_tags = curr_tags.split(",")
        all_tags = set(existing_tags + tags)
        joined_tags = ",".join(sorted(all_tags))

        ctx = baggage.set_baggage("montecarlo.tags", joined_tags, curr_ctx)

        token = context.attach(ctx)
        try:
            tracer = get_tracer()
            with tracer.start_as_current_span(span_name):
                return wrapped(*args, **kwargs)
        finally:
            context.detach(token)

    return wrapper


def trace_with_workflow(span_name: str, workflow_name: str):
    """
    Decorator to trace a function or method as part of a workflow.

    A workflow is a logical grouping of tasks.

    This decorator will create a span and set it as the current span in
    the current tracer's context. It sets the workflow name as an attribute
    under the key "montecarlo.workflow" and propagates it to child spans.

    :param span_name: Name of the span.
    :param workflow_name: Name of the workflow to associate with the span.
    """
    return trace_with_attributes(span_name, {"workflow": workflow_name})


def trace_with_task(span_name: str, task_name: str):
    """
    Decorator to trace a function or method as a task.

    A task is a unit of work that is part of a workflow.

    This decorator will create a span and set it as the current span in
    the current tracer's context. It sets the task name as an attribute
    under the key "montecarlo.task" and propagates it to child spans.

    :param span_name: Name of the span.
    :param task_name: Name of the task to associate with the span.
    """
    return trace_with_attributes(span_name, {"task": task_name})


@contextlib.contextmanager
def create_span_with_attributes(
    span_name: str, attributes: dict[str, str | int | float | bool]
):
    """
    Context manager to create a span with the given name, set it as the
    current span, and add attributes to it.

    For each attribute, it will prepend the key with the "montecarlo."
    prefix. It will add the attributes to the current span, and propagate
    them to child spans.

    :param span_name: Name of the span.
    :param attributes: Dictionary of attributes to add to the span.
    """
    ctx = context.get_current()

    for key, value in attributes.items():
        mc_key = f"montecarlo.{key}"
        ctx = baggage.set_baggage(mc_key, value, ctx)

    token = context.attach(ctx)
    try:
        tracer = get_tracer()
        with tracer.start_as_current_span(span_name) as span:
            yield span
    finally:
        context.detach(token)


@contextlib.contextmanager
def create_span_with_tags(span_name: str, tags: list[str]):
    """
    Context manager to create a span with the given name, set it as the
    current span, and add tags to it. It merges the provided tags with
    any existing tags from the current context and propagates them to
    child spans.

    Tags are stored as a sorted comma-separated string in baggage under
    the key "montecarlo.tags".

    :param span_name: Name of the span.
    :param tags: List of tags to add to the span.
    """
    curr_ctx = context.get_current()

    # Merge existing tags with new tags.
    existing_tags = []
    curr_tags = baggage.get_baggage("montecarlo.tags", curr_ctx)
    if curr_tags and isinstance(curr_tags, str):
        existing_tags = curr_tags.split(",")
    all_tags = set(existing_tags + tags)
    joined_tags = ",".join(sorted(all_tags))

    ctx = baggage.set_baggage("montecarlo.tags", joined_tags, curr_ctx)

    token = context.attach(ctx)
    try:
        tracer = get_tracer()
        with tracer.start_as_current_span(span_name) as span:
            yield span
    finally:
        context.detach(token)


@contextlib.contextmanager
def create_span_with_workflow(span_name: str, workflow_name: str):
    """
    Context manager to create a span with the given name, set it as the
    current span, and add a workflow attribute to it. It sets the
    workflow name to "montecarlo.workflow" and propagates it to child
    spans.

    A workflow is a logical grouping of tasks.

    :param span_name: Name of the span.
    :param workflow_name: Name of the workflow to associate with the span.
    """
    with create_span_with_attributes(span_name, {"workflow": workflow_name}) as span:
        yield span


@contextlib.contextmanager
def create_span_with_task(span_name: str, task_name: str):
    """
    Context manager to create a span with the given name, set it as the
    current span, and add a task attribute to it. It sets the task name
    to "montecarlo.task" and propagates it to child spans.

    A task is a unit of work that is part of a workflow.

    :param span_name: Name of the span.
    :param task_name: Name of the task to associate with the span.
    """
    with create_span_with_attributes(span_name, {"task": task_name}) as span:
        yield span
