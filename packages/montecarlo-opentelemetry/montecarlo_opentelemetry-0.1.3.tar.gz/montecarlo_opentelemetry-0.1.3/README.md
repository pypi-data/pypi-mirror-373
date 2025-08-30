# Monte Carlo OpenTelemetry SDK

This library provides a Python SDK for tracing applications with OpenTelemetry for use with Monte Carlo's AI Observability solution.

To evaluate the effectiveness of AI agents, the first step is capturing the prompts sent to an LLM and the completions returned. The next challenge is categorizing these LLM calls, since different types of LLM calls require different evaluation approaches.

This SDK not only streamlines OpenTelemetry tracing setup, but it also makes it easy to add custom attributes to spans, enabling you to filter and select different subsets of spans for evaluation.

*This is alpha software. The API is subject to change.*

## Installation

### Install the SDK

Requires Python 3.10 or later.

```bash
$ pip install montecarlo-opentelemetry
```

### Install the instrumentation package(s) for the AI libraries you want to trace.

The Monte Carlo SDK can work with existing instrumentation for AI libraries to capture traces automatically. Choose the instrumentation library that matches the library you are using.

```bash
# For Langchain/LangGraph
$ pip install opentelemetry-instrumentation-langchain

# For OpenAI
$ pip install opentelemetry-instrumentation-openai
```

See a selection of available instrumentation libraries below.

## Quick Start

### Set up Tracing in Your Application
```python
# Import the Monte Carlo SDK.
import montecarlo_opentelemetry as mc

# Import the AI client library (Anthropic in this example.)
from anthropic import Anthropic

# Import the corresponding instrumentation library.
from opentelemetry.instrumentation.anthropic import AnthropicInstrumentor

# Create an Instrumentor object
anthropic_instrumentor = AnthropicInstrumentor()

# Set up tracing.
mc.setup(
    agent_name="my-agent",
    otlp_endpoint="http://localhost:4318/v1/traces",
    instrumentors=[anthropic_instrumentor],
)

# Use decorator to add a Monte Carlo workflow attribute.
@mc.trace_with_workflow("parent-function", "my-workflow")
def parent():
    child()

# Use decorator to add a Monte Carlo task attribute.
@mc.trace_with_task("child-function", "my-task)
def child():
    message = Anthropic().messages.create(
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": "Hello world!",
            }
        ],
        model="claude-sonnet-4-20250514",
    )
```

## Example

### Example Application
To see how the Monte Carlo SDK can be used to add identifying attributes to spans, let's look at an example application that's slighly larger than the Quick Start one.

This is a simplified "Travel Assistant" agent that can make hotel and flight reservations.
```python
# Fake LLM library that can make a call to an LLM.
from example.LLMLibrary import call_llm

def travel_assistant():
    flight_assistant()
    hotel_assistant()

def flight_assistant():
    plan_flight()
    book_flight()

def plan_flight():
    pass

def book_flight():
    call_llm()

def hotel_assistant():
    search_for_hotel()
    book_hotel()

def search_for_hotel():
    call_llm()

def book_hotel():
    call_llm()

```

If we traced each function in this application, the structure of the trace would look like this:
```text
travel_assistant
├── flight_assistant
│   ├── plan_flight
│   └── book_flight
│       └── call_llm
└── hotel_assistant
    ├── search_for_hotel
    │   └── call_llm
    └── book_hotel
        └── call_llm
```

In order to differentiate between different types of LLM calls, it would be helpful to add identifying attributes to spans. That way we could tell if an LLM call was part of a workflow managed by the flight assistant, or if it was part of the hotel booking task in the workflow managed by the hotel assistant.

### Adding Attributes with the Monte Carlo SDK

Let's see how we can use the Monte Carlo SDK to enhance the tracing data with identifying attributes.
```python
import montecarlo_opentelemetry as mc

# Fake LLM library that can make a call to an LLM.
from example.LLMLibrary import call_llm

# Fake LLM library instrumentation that will automatically create spans
# each time call_llm() is called.
from example.LLMLibrary.instrumentation import LLMInstrumentor

mc.setup(
    agent_name="travel-assistant",
    otlp_endpoint="http://localhost:4318/v1/traces",
    instrumentors=[LLMInstrumentor()],
)

@mc.trace_with_tags(span_name="travel_assistant", tags=["travel", "v1"])
def travel_assistant():
    flight_assistant()
    hotel_assistant()

@mc.trace_with_workflow(span_name="flight_assistant", workflow_name="flight")
def flight_assistant():
    plan_flight()
    book_flight()

@mc.trace_with_task(span_name="plan_flight", task_name="plan")
def plan_flight():
    pass

@mc.trace_with_task(span_name="book_flight", task_name="book")
def book_flight():
    call_llm()

@mc.trace_with_workflow(span_name="hotel_assistant", workflow_name="hotel")
def hotel_assistant():
    search_for_hotel()
    book_hotel()

@mc.trace_with_task(span_name="search_for_hotel", task_name="search")
def search_for_hotel():
    call_llm()

# Arguments can also be passed positionally.
@mc.trace_with_task("book_hotel", "book")
def book_hotel():
    call_llm()
```

Because `montecarlo.*` attributes propagate from parent to child spans, the `call_llm` spans will contain all of the `montecarlo.*` attributes were added to spans that occur above it in the trace hierarchy.

For example, the `call_llm` span for `book_flight` will not only have the `montecarlo.task = "book"` attribute that we added directly, but also the `montecarlo.workflow = "flight"` added on the `flight_assistant` span, and the `montecarlo.tags = "travel,v1"` attributes added on the `travel_assistant` span.

That results in the following trace structure:
```text
travel_assistant            <-- montecarlo.tags = "travel,v1"
│
├── flight_assistant        <-- montecarlo.workflow = "flight"
|   |                       <-- montecarlo.tags = "travel,v1"
|   |
│   ├── plan_flight         <-- montecarlo.task = "plan"
|   |                       <-- montecarlo.workflow = "flight"
|   |                       <-- montecarlo.tags = "travel,v1"
|   |
│   └── book_flight         <-- montecarlo.task = "book"
│       |                   <-- montecarlo.workflow = "flight"
│       |                   <-- montecarlo.tags = "travel,v1"
│       |
│       └── call_llm        <-- montecarlo.task = "book"
│                           <-- montecarlo.workflow = "flight"
│                           <-- montecarlo.tags = "travel,v1"
│
└── hotel_assistant         <-- montecarlo.workflow = "hotel"
    |                       <-- montecarlo.tags = "travel,v1"
    |
    ├── search_for_hotel    <-- montecarlo.task = "search"
    │   |                   <-- montecarlo.workflow = "hotel"
    │   |                   <-- montecarlo.tags = "travel,v1"
    │   |
    │   └── call_llm        <-- montecarlo.task = "search"
    │                       <-- montecarlo.workflow = "hotel"
    │                       <-- montecarlo.tags = "travel,v1"
    │
    └── book_hotel          <-- montecarlo.task = "book"
        |                   <-- montecarlo.workflow = "hotel"
        |                   <-- montecarlo.tags = "travel,v1"
        |
        └── call_llm        <-- montecarlo.task = "book"
                            <-- montecarlo.workflow = "hotel"
                            <-- montecarlo.tags = "travel,v1"
```

## Tracing LLM Calls Manually

Typically, an instrumentation library will be used to automatically trace LLM calls. When that's not possible, the `create_llm_span` context manager can be used to create a span for the LLM call manually.

The `create_llm_span` context manager will set request-related attributes. Since provider, model, operation, and prompts are known before the LLM call is made, they should be passed to the context manager so that the appropriate span attributes can be added automatically. Response-related attributes need to be added with the helper functions after the LLM call.

It is possible to record a list of prompts as attributes that is different than the prompts sent to the LLM. If you have sensitive data that should not be recorded as span attributes, you can pass a modified list of prompts to `create_llm_span`, and then pass the un-redacted prompts to the LLM.

```python
import montecarlo_opentelemetry as mc

# Fake LLM library that can make a call to an LLM.
from example.LLMLibrary import call_llm

prompts_to_record = [
    {"role": "system", "content": "You are a world-class greeter."},
    {"role": "user", "content": "Say hello to Bob."},
    {"role": "assistant", "content": "Hello Bob!"},
]

prompts_to_send = [
    {"role": "system", "content": "You are a world-class greeter."},
    {"role": "user", "content": "Say hello to Bob. Use SENSITIVE DATA."},
    {"role": "assistant", "content": "Hello Bob!"},
]

with mc.create_llm_span(
    span_name="example-span",
    provider="llm-provider",
    model="llm-model",
    operation="chat",
    prompts_to_record=prompts_to_record,
) as span:
    # Make LLM call.
    #
    # We are sending un-redacted prompts to the LLM. The LLM will see
    # "SENSITIVE DATA", but it won't be recorded as a span attribute.
    resp = call_llm(prompts_to_send)

    # Add response attributes to span.
    #
    # Assume that the response object has attributes like model, completions, etc.
    mc.add_llm_response_model(span, resp.model)
    mc.add_llm_completions(span, resp.completions)
    mc.add_llm_tokens(
        span,
        resp.prompt_tokens,
        resp.completion_tokens,
        resp.total_tokens,
        resp.cache_creation_input_tokens,
        resp.cache_read_input_tokens,
    )
```

## License

Apache 2.0 - See the [LICENSE](http://www.apache.org/licenses/LICENSE-2.0) for more information.

## Security

See SECURITY.md for more information.


## Available Instrumentation Packages

* [opentelemetry-instrumentation-alephalpha](https://pypi.org/project/opentelemetry-instrumentation-alephalpha/)
* [opentelemetry-instrumentation-anthropic](https://pypi.org/project/opentelemetry-instrumentation-anthropic/)
* [opentelemetry-instrumentation-bedrock](https://pypi.org/project/opentelemetry-instrumentation-bedrock/)
* [opentelemetry-instrumentation-chromadb](https://pypi.org/project/opentelemetry-instrumentation-chromadb/)
* [opentelemetry-instrumentation-cohere](https://pypi.org/project/opentelemetry-instrumentation-cohere/)
* [opentelemetry-instrumentation-crewai](https://pypi.org/project/opentelemetry-instrumentation-crewai/)
* [opentelemetry-instrumentation-google-generativeai](https://pypi.org/project/opentelemetry-instrumentation-google-generativeai/)
* [opentelemetry-instrumentation-groq](https://pypi.org/project/opentelemetry-instrumentation-groq/)
* [opentelemetry-instrumentation-haystack](https://pypi.org/project/opentelemetry-instrumentation-haystack/)
* [opentelemetry-instrumentation-lancedb](https://pypi.org/project/opentelemetry-instrumentation-lancedb/)
* [opentelemetry-instrumentation-langchain](https://pypi.org/project/opentelemetry-instrumentation-langchain/)
* [opentelemetry-instrumentation-llamaindex](https://pypi.org/project/opentelemetry-instrumentation-llamaindex/)
* [opentelemetry-instrumentation-marqo](https://pypi.org/project/opentelemetry-instrumentation-marqo/)
* [opentelemetry-instrumentation-mcp](https://pypi.org/project/opentelemetry-instrumentation-mcp/)
* [opentelemetry-instrumentation-milvus](https://pypi.org/project/opentelemetry-instrumentation-milvus/)
* [opentelemetry-instrumentation-mistralai](https://pypi.org/project/opentelemetry-instrumentation-mistralai/)
* [opentelemetry-instrumentation-ollama](https://pypi.org/project/opentelemetry-instrumentation-ollama/)
* [opentelemetry-instrumentation-openai](https://pypi.org/project/opentelemetry-instrumentation-openai/)
* [opentelemetry-instrumentation-openai-agents](https://pypi.org/project/opentelemetry-instrumentation-openai-agents/)
* [opentelemetry-instrumentation-pinecone](https://pypi.org/project/opentelemetry-instrumentation-pinecone/)
* [opentelemetry-instrumentation-qdrant](https://pypi.org/project/opentelemetry-instrumentation-qdrant/)
* [opentelemetry-instrumentation-replicate](https://pypi.org/project/opentelemetry-instrumentation-replicate/)
* [opentelemetry-instrumentation-sagemaker](https://pypi.org/project/opentelemetry-instrumentation-sagemaker/)
* [opentelemetry-instrumentation-together](https://pypi.org/project/opentelemetry-instrumentation-together/)
* [opentelemetry-instrumentation-transformers](https://pypi.org/project/opentelemetry-instrumentation-transformers/)
* [opentelemetry-instrumentation-vertexai](https://pypi.org/project/opentelemetry-instrumentation-vertexai/)
* [opentelemetry-instrumentation-watsonx](https://pypi.org/project/opentelemetry-instrumentation-watsonx/)
* [opentelemetry-instrumentation-weaviate](https://pypi.org/project/opentelemetry-instrumentation-weaviate/)
