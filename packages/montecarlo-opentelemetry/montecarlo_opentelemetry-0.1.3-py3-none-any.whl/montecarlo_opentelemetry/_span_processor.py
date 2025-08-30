from typing import Optional

from opentelemetry.baggage import get_all
from opentelemetry.context import Context, get_value
from opentelemetry.sdk.trace import ReadableSpan, SpanProcessor
from opentelemetry.trace import Span

MONTECARLO_PREFIX = "montecarlo."


def _coerce_attribute_value(value: object) -> str | int | float | bool:
    """Coerce attribute value to a primitive type (str, int, float, bool)."""
    match value:
        case str() | int() | float() | bool():
            return value
        case _:
            return str(value)


class _MonteCarloSpanProcessor(SpanProcessor):
    """Custom span processor that adds attributes important to Monte Carlo."""

    def on_start(self, span: Span, parent_context: Optional[Context] = None) -> None:
        """
        Add attributes to span from relevant items in Context.

        :param span: Current Span to add attributes to.
        :param parent_context: Parent context, defaults to None
        """
        # Get montecarlo attributes from baggage.
        baggage = get_all(parent_context)
        for k, v in baggage.items():
            if k.startswith(MONTECARLO_PREFIX):
                val = _coerce_attribute_value(v)
                span.set_attribute(k, val)

        # Get langchain association_properties, if present.
        if association_properties := get_value("association_properties"):
            if isinstance(association_properties, dict):
                for k, v in association_properties.items():
                    key = f"{MONTECARLO_PREFIX}association_properties.{k}"
                    val = _coerce_attribute_value(v)
                    span.set_attribute(key, val)

    def on_end(self, span: ReadableSpan) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        return True
