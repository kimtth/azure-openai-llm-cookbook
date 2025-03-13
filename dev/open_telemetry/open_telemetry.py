import os
from openai import AzureOpenAI
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.trace.status import Status, StatusCode
from opentelemetry.sdk.resources import SERVICE_NAME, Resource


AZURE_OPENAI_API_KEY = "<your-api-key>"  # Replace with your OpenAI API key
AZURE_OPENAI_MODEL_NAME = "<your-value>"  # Vision model for image analysis
AZURE_OPENAI_API_VERSION = "<your-value>"  # API version for OpenAI
AZURE_OPENAI_ENDPOINT = "https://<your-value>.openai.azure.com"

# Configure the tracer provider
resource = Resource(attributes={SERVICE_NAME: "openai-client"})

trace.set_tracer_provider(TracerProvider(resource=resource))

# Configure console exporter for local debugging
console_exporter = ConsoleSpanExporter()
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(console_exporter))

# Optional: Configure OTLP exporter if sending to a collector
# otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4318/v1/traces")
# trace.get_tracer_provider().add_span_processor(
#     BatchSpanProcessor(otlp_exporter)
# )

# Create a tracer
tracer = trace.get_tracer("openai.telemetry")


def get_openai_completion(user_input):
    """Get completion from OpenAI with OpenTelemetry tracing."""

    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY") or AZURE_OPENAI_API_KEY,
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", AZURE_OPENAI_API_VERSION),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", AZURE_OPENAI_ENDPOINT),
    )
    model = (os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", AZURE_OPENAI_MODEL_NAME),)

    with tracer.start_as_current_span("openai.completion") as span:
        # Add user input as a span attribute
        span.set_attribute("user.input", user_input)
        span.set_attribute("openai.model", model)

        try:
            with tracer.start_as_current_span("openai.api_call"):
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": user_input},
                    ],
                )

            # Extract and record the response content
            assistant_message = response.choices[0].message.content
            span.set_attribute("openai.response", assistant_message)
            span.set_attribute(
                "openai.token_usage.total",
                response.usage.total_tokens if hasattr(response, "usage") else 0,
            )

            return assistant_message

        except Exception as e:
            span.set_status(Status(StatusCode.ERROR))
            span.record_exception(e)
            return f"Error: {str(e)}"


if __name__ == "__main__":
    while True:
        user_input = input("Enter your message (or 'quit' to exit): ")

        if user_input.lower() == "quit":
            break

        with tracer.start_as_current_span("process_user_request") as span:
            span.set_attribute("user.raw_input", user_input)

            response = get_openai_completion(user_input)
            print(f"Assistant: {response}")
