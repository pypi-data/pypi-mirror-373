# NTT AI Observability Exporter

A specialized telemetry exporter for NTT AI Foundry projects using Azure Monitor OpenTelemetry. This package simplifies telemetry setup for AI applications built with Azure services.

## Features

- **Single & Multi-Destination Telemetry**: Send telemetry to one or multiple Azure Monitor instances
- **Automatic instrumentation** of Azure SDK libraries
- **Simplified configuration** for Azure Monitor OpenTelemetry
- **Specialized support** for Semantic Kernel telemetry
- **Azure AI Foundry compatibility** with content recording
- **GenAI content recording** for prompts and responses
- **Comprehensive logging, tracing, and metrics** collection

## Installation

```bash
# Using pip
pip install ntt-ai-observability-exporter

# Using uv
uv pip install ntt-ai-observability-exporter
```

## Usage

### Single Destination Telemetry (Standard)

```python
from ntt_ai_observability_exporter import configure_telemetry

# Simple one-line setup for single Application Insights instance
configure_telemetry(
    connection_string="InstrumentationKey=your-key;IngestionEndpoint=your-endpoint",
    customer_name="your-customer",
    agent_name="your-agent"
)

# Now use your AI components - telemetry is automatic!
```

### Multi-Destination Telemetry (NEW!)

Send the same telemetry data to multiple Azure Monitor instances simultaneously:

```python
from ntt_ai_observability_exporter.telemetry_multi import configure_telemetry_azure_monitor

# Configure telemetry for multiple Application Insights instances
configure_telemetry_azure_monitor(
    connection_strings=[
        "InstrumentationKey=key1;IngestionEndpoint=https://region1.in.applicationinsights.azure.com/",
        "InstrumentationKey=key2;IngestionEndpoint=https://region2.in.applicationinsights.azure.com/",
        "InstrumentationKey=key3;IngestionEndpoint=https://region3.in.applicationinsights.azure.com/"
    ],
    customer_name="multi-customer",
    agent_name="multi-agent",
    enable_genai_content=True,           # Enable GenAI content recording
    genai_content_mode="all",            # "all" or "sanitized"
    enable_semantic_kernel_diagnostics=True  # Enable Semantic Kernel diagnostics
)

# All telemetry (traces, logs, metrics) will be sent to ALL destinations!
```

#### Multi-Destination Features

- **Duplicate to Multiple Targets**: Same telemetry sent to all connection strings
- **GenAI Content Recording**: Capture prompts and responses automatically
- **Semantic Kernel Integration**: Full diagnostic support
- **Live Metrics**: Real-time monitoring for all destinations
- **Comprehensive Instrumentation**: Azure AI, OpenAI, HTTP clients, and more

### Configuration Options

```python
# Standard single destination with all options
configure_telemetry(
    connection_string="InstrumentationKey=your-key;IngestionEndpoint=your-endpoint",
    customer_name="your-customer",
    agent_name="your-agent",
    enable_content_recording=True,
    content_recording_mode="all",
    enable_azure_monitor_tracing=True
)

# Multi-destination with advanced options
configure_telemetry_azure_monitor(
    connection_strings=["conn1", "conn2", "conn3"],
    customer_name="customer",
    agent_name="agent",
    enable_live_metrics=True,
    metric_export_interval_millis=15000,
    disable_offline_storage=False,
    logger_names=["semantic_kernel", "azure", "custom_logger"]
)

```

## What Gets Instrumented Automatically

The package automatically instruments:

- **Azure SDK libraries** (azure.ai.projects, azure.ai.inference, azure.ai.agents)
- **HTTP client libraries** (requests, aiohttp, urllib3)
- **OpenAI Python client** (when available)
- **Semantic Kernel** (when enabled)
- **Azure AI Foundry components** with GenAI content recording

This means when you use Azure AI components, telemetry is captured without any additional code.

## Telemetry Types Captured

The configuration captures:

- **Traces**: Request flows, GenAI operations, and distributed tracing
- **Metrics**: Performance measurements, token usage, response times
- **Logs**: Structured logging from Azure SDKs and application code

## Configuration Parameters

### Standard Telemetry (`configure_telemetry`)

- `connection_string`: Azure Monitor connection string
- `customer_name`: Maps to `service.name` in OpenTelemetry resource
- `agent_name`: Maps to `service.instance.id` in OpenTelemetry resource
- `enable_content_recording`: Enable GenAI content recording (default: True)
- `content_recording_mode`: "all" or "sanitized" (default: "all")
- `enable_azure_monitor_tracing`: Enable Azure Monitor tracing (default: True)

### Multi-Destination Telemetry (`configure_telemetry_azure_monitor`)

- `connection_strings`: List of Azure Monitor connection strings
- `customer_name`: Service name identifier
- `agent_name`: Service instance identifier
- `enable_genai_content`: Enable GenAI content recording (default: True)
- `genai_content_mode`: "all" or "sanitized" (default: "all")
- `enable_semantic_kernel_diagnostics`: Enable Semantic Kernel OTEL (default: True)
- `enable_live_metrics`: Enable live metrics for all destinations (default: True)
- `metric_export_interval_millis`: Metrics export interval (default: 15000)
- `logger_names`: Additional logger names to capture (default: ["semantic_kernel", "azure", "azure.core"])

## Environment Variables

You can set these environment variables instead of passing parameters:

- `AZURE_MONITOR_CONNECTION_STRING`: The connection string for Azure Monitor
- `CUSTOMER_NAME`: Maps to `service.name` in OpenTelemetry resource
- `AGENT_NAME`: Maps to `service.instance.id` in OpenTelemetry resource
- `AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED`: Enable GenAI content recording
- `AZURE_TRACING_GEN_AI_CONTENT_RECORDING_MODE`: Content recording mode
- `SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS`: Enable SK diagnostics

## Example Use Cases

### Single Application Insights (Standard Use Case)

```python
from ntt_ai_observability_exporter import configure_telemetry

# Configure telemetry for your Azure AI project
configure_telemetry(
    connection_string="InstrumentationKey=xxx;IngestionEndpoint=https://westeurope-5.in.applicationinsights.azure.com/",
    customer_name="customer-name-foundry",
    agent_name="ai-foundry-agent"
)

# Use Azure AI components - telemetry is automatic
from azure.ai.projects import AIProjectClient
client = AIProjectClient(...)
# All operations are automatically instrumented
```

### Multiple Application Insights (Multi-Tenant/Multi-Region)

```python
from ntt_ai_observability_exporter.telemetry_multi import configure_telemetry_azure_monitor

# Send telemetry to multiple destinations simultaneously
configure_telemetry_azure_monitor(
    connection_strings=[
        "InstrumentationKey=tenant1;IngestionEndpoint=https://region1.in.applicationinsights.azure.com/",
        "InstrumentationKey=tenant2;IngestionEndpoint=https://region2.in.applicationinsights.azure.com/",
        "InstrumentationKey=central;IngestionEndpoint=https://central.in.applicationinsights.azure.com/"
    ],
    customer_name="multi-tenant-customer",
    agent_name="multi-region-agent"
)

# Use any Azure AI services - telemetry goes to ALL destinations
from azure.ai.inference import ChatCompletionsClient
from semantic_kernel import Kernel

client = ChatCompletionsClient(...)  # Monitored in all App Insights
kernel = Kernel()                    # Monitored in all App Insights
```


## Semantic Kernel Telemetry Support

For applications using Semantic Kernel, use the specialized configuration function:

```python
from ntt_ai_observability_exporter import configure_semantic_kernel_telemetry

# Configure Semantic Kernel telemetry BEFORE creating any Kernel instances
configure_semantic_kernel_telemetry(
    connection_string="your_connection_string",
    customer_name="your_customer_name",
    agent_name="your_agent_name"
)

# Then create and use your Semantic Kernel
from semantic_kernel import Kernel
kernel = Kernel()
# ... rest of your code
```

## Development and Testing

### Installation for Development

Install the package with development dependencies:

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Or install with just testing dependencies
pip install -e ".[test]"

# Or install from requirements-dev.txt
pip install -r requirements-dev.txt
```

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src/ntt_ai_observability_exporter

# Run tests with detailed coverage report
pytest --cov=src/ntt_ai_observability_exporter --cov-report=term-missing

# Run specific test file
pytest tests/test_semantic_kernel_telemetry.py -v
```

### Test Coverage

The package includes comprehensive unit tests with:
- **95%+ overall test coverage**
- **100% coverage** for all telemetry modules
- **45+ test cases** covering all functionality including multi-destination telemetry
- Validation of configuration, error handling, and Azure Monitor integration
- Mock-based testing for reliable CI/CD pipelines

### Code Quality

The project uses:
- **pytest** for testing framework
- **black** for code formatting
- **flake8** for linting
- **mypy** for type checking
- **isort** for import sorting
