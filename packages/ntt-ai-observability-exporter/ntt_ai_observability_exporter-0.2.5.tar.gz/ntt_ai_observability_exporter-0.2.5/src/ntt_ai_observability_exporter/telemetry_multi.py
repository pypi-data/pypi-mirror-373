# Multi-Application Insights telemetry setup using OpenTelemetry and Azure Monitor exporters.
# Sends the same traces, logs, and metrics to multiple Application Insights resources.
#
# GenAI content recording (Azure AI Foundry):
# - By default, this enables content recording (prompts/responses) with mode="all"
# - It also enables Semantic Kernel OTEL diagnostics by default
# - You can turn either off via configure_multi_azure_monitor(...) flags
#
# Requirements (install what you use):
# - opentelemetry-sdk==1.36.0
# - opentelemetry-api==1.36.0
# - opentelemetry-instrumentation-requests
# - azure-monitor-opentelemetry-exporter>=1.0.0
# - azure-core
# - requests
# Optional for Azure AI Foundry GenAI spans with content:
# - azure-ai-inference (and/or azure-ai-agents)
# Optional if you use OpenAI python client instead of azure.ai.inference:
# - opentelemetry-instrumentation-openai

import logging
import os
import time
from typing import Dict, List, Optional

# Set up logger
logger = logging.getLogger("ntt_ai_observability")

from opentelemetry import trace, metrics
from opentelemetry.metrics import set_meter_provider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.metrics.view import View, DropAggregation
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import set_tracer_provider
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from .utilities import get_config, validate_telemetry_config
from azure.monitor.opentelemetry.exporter import (
    AzureMonitorTraceExporter,
    AzureMonitorMetricExporter,
    AzureMonitorLogExporter,
    ApplicationInsightsSampler,
)

_logger = logging.getLogger("multi_ai.telemetry")
if not _logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    _logger.addHandler(_handler)
_logger.setLevel(logging.INFO)


def enable_genai_content_recording(enabled: bool = True, mode: str = "all") -> None:
    """
    Enable Azure GenAI content recording. Must be called BEFORE importing azure.ai.* clients
    or Semantic Kernel to ensure the SDK reads these environment variables.

    Args:
        enabled: True to enable content recording
        mode: "all" to include prompts and responses; "sanitized" to redact sensitive content
              Any other value may be ignored by the SDK.
    """
    os.environ["AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED"] = "true" if enabled else "false"
    # Normalize mode to accepted values
    mode_normalized = (mode or "").strip().lower()
    if mode_normalized in ("all", "sanitized", "sanitize", "redacted", "redact"):
        # standardize to values commonly recognized: "all" or "sanitized"
        if mode_normalized in ("sanitize", "redacted", "redact"):
            mode_normalized = "sanitized"
    else:
        # fallback to sanitized if given invalid input (e.g., "true")
        mode_normalized = "sanitized"
    os.environ["AZURE_TRACING_GEN_AI_CONTENT_RECORDING_MODE"] = mode_normalized
    # Optional toggle some customers use; harmless to set
    os.environ.setdefault("ENABLE_AZURE_MONITOR_TRACING", "true")

    _logger.info("GenAI content recording enabled=%s mode=%s", enabled, mode_normalized)


def enable_semantic_kernel_otel(enabled: bool = True) -> None:
    """
    Enable/disable Semantic Kernel OTEL emission (prompts/steps).
    Call BEFORE importing semantic_kernel.
    """
    os.environ["SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS"] = "true" if enabled else "false"
    os.environ["SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS_SENSITIVE"] = "true" if enabled else "false"


def build_default_resource(
    service_name: str,
    service_instance_id: str,
    service_version: Optional[str] = None,
    extra_attributes: Optional[Dict[str, str]] = None,
) -> Resource:
    attrs: Dict[str, str] = {
        "service.name": service_name,
        "service.instance.id": service_instance_id,
    }
    if service_version:
        attrs["service.version"] = service_version
    if extra_attributes:
        attrs.update(extra_attributes)
    return Resource.create(attrs)


def default_views() -> List[View]:
    # Drop everything by default, then allow specific namespaces.
    return [
        View(instrument_name="*", aggregation=DropAggregation()),
        View(instrument_name="semantic_kernel*"),
        View(instrument_name="azure.*"),
        View(instrument_name="http.*"),
        View(instrument_name="ai.*"),
    ]


def _attach_logging_handlers(
    logger_provider: LoggerProvider,
    logger_names: Optional[List[str]] = None
) -> None:
    """
    Attach unfiltered OpenTelemetry LoggingHandlers so logs from
    semantic_kernel, azure, azure.core, azure.ai, and azure.ai.projects are exported.
    No filtering is applied anywhere.
    """
    from opentelemetry._logs import set_logger_provider
    from opentelemetry.sdk._logs import LoggingHandler

    # Bind provider globally so no-arg LoggingHandler works
    set_logger_provider(logger_provider)

    # Default target loggers (you can override via logger_names)
    targets = logger_names or [
        "semantic_kernel",
        "azure",
        "azure.core",
        "azure.ai",
        "azure.ai.projects",
    ]

    def _has_otel_handler(lg: logging.Logger) -> bool:
        try:
            from opentelemetry.sdk._logs import LoggingHandler as RealLoggingHandler
            return any(isinstance(h, RealLoggingHandler) for h in lg.handlers)
        except ImportError:
            # If we can't import LoggingHandler, check by class name
            return any(h.__class__.__name__ == 'LoggingHandler' for h in lg.handlers)

    # 1) Root: unfiltered handler to catch everything
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    if not _has_otel_handler(root):
        root.addHandler(LoggingHandler())  # unfiltered

    # 2) Each target logger: add its own unfiltered handler and stop propagation
    #    This guarantees capture even if a library later sets propagate=False,
    #    and avoids duplicates (since we also have a root handler).
    for name in targets:
        lg = logging.getLogger(name)
        lg.setLevel(logging.INFO)
        if not _has_otel_handler(lg):
            lg.addHandler(LoggingHandler())  # unfiltered
        lg.propagate = False  # prevent duplicate records (logger + root)

            
def _install_instrumentations(enable_openai_instrumentation: bool = True) -> None:
    # Azure SDK (azure-core) tracing so Azure clients emit spans
    try:
        from azure.core.settings import settings
        from azure.core.tracing.ext.opentelemetry_span import OpenTelemetrySpan

        settings.tracing_implementation = OpenTelemetrySpan
        _logger.info("Enabled azure-core OpenTelemetry tracing")
    except Exception as ex:
        _logger.warning("azure-core tracing not enabled: %s", ex)

    # HTTP client instrumentations commonly used by Azure SDKs and apps
    try:
        from opentelemetry.instrumentation.requests import RequestsInstrumentor

        RequestsInstrumentor().instrument()
        _logger.info("Instrumented requests")
    except Exception as ex:
        _logger.warning("requests instrumentation failed: %s", ex)

    # Azure AI Foundry: instrument azure.ai.inference for GenAI spans with content
    try:
        from azure.ai.inference.tracing import AIInferenceInstrumentor  # type: ignore
        AIInferenceInstrumentor().instrument()
      
        from azure.ai.projects.telemetry.agents import (  # type: ignore
            AIAgentsInstrumentor as ProjectsAIAgentsInstrumentor,
        )
        ProjectsAIAgentsInstrumentor().instrument()
      
        _logger.info("Instrumented azure.ai.inference (GenAI)")
    except Exception as ex:
        _logger.info("azure.ai.inference instrumentor not available or failed: %s", ex)

    # Azure AI Foundry: instrument azure.ai.projects for GenAI spans with content
    try:
      
        from azure.ai.projects.telemetry.agents import (  # type: ignore
            AIAgentsInstrumentor as ProjectsAIAgentsInstrumentor,
        )
        ProjectsAIAgentsInstrumentor().instrument()
      
        _logger.info("Instrumented azure.ai.projects (GenAI)")
    except Exception as ex:
        _logger.info("azure.ai.projects instrumentor not available or failed: %s", ex)



    # Azure AI Agents (optional)
    try:
        from azure.ai.agents.telemetry import AIAgentsInstrumentor  # type: ignore
      
        AIAgentsInstrumentor().instrument()
        _logger.info("Instrumented azure.ai.agents")
    except Exception as ex:
        _logger.debug("azure.ai.agents instrumentor not available: %s", ex)

# Optional: If you are using the OpenAI python client (not azure.ai.inference), instrument it too.
    if enable_openai_instrumentation:
        try:
            # Correct class name for the OpenAI instrumentor
            from opentelemetry.instrumentation.openai import OpenAIIntegrationInstrumentor  # type: ignore
            OpenAIIntegrationInstrumentor().instrument()
            _logger.info("Instrumented OpenAI python client")
            from opentelemetry.instrumentation.openai import OpenAIInstrumentor  # type: ignore
            OpenAIInstrumentor().instrument()
        except ImportError as ex:
            _logger.debug("OpenAI instrumentation not available: %s", ex)
        except Exception as ex:
            _logger.warning("OpenAI instrumentation failed: %s", ex)
            


def configure_telemetry_azure_monitor(
    connection_strings: List[str],
    customer_name: Optional[str] = None,
    agent_name: Optional[str] = None,
    views: Optional[List[View]] = None,
    enable_live_metrics: bool = True,
    logger_names: Optional[List[str]] = None,
    disable_offline_storage: bool = False,
    metric_export_interval_millis: int = 15000,
    # New flags to avoid explicit helper calls:
    enable_genai_content: bool = True,
    genai_content_mode: str = "all",
    enable_semantic_kernel_diagnostics: bool = True
) -> None:
    """
    Configure OpenTelemetry providers with Azure Monitor exporters for multiple
    Application Insights connection strings.

    - All telemetry (traces, logs, metrics) will be sent to ALL destinations.
    - Must be called once at process start, BEFORE importing/initializing libraries that emit telemetry.

    Args:
        connection_strings: List of Application Insights connection strings.
        resource: OpenTelemetry Resource for service attributes.
        views: Metric Views to filter/aggregate metrics.
        enable_live_metrics: Enable Live Metrics (QuickPulse) for metrics exporter.
        logger_names: Extra logger names to attach OTEL LoggingHandler (e.g. ["semantic_kernel", "azure"]).
        disable_offline_storage: Disable local disk retry storage for exporters.
        metric_export_interval_millis: Export interval for metrics.
        enable_genai_content: If True (default), set AZURE_TRACING_GEN_AI_* env to capture prompts/responses.
        genai_content_mode: "all" (default) or "sanitized".
        enable_semantic_kernel_diagnostics: If True (default), enable SK OTEL diagnostics env.
    """
    if not connection_strings or not any(cs for cs in connection_strings):
        raise ValueError("At least one valid connection string is required")

    # Set env-based features FIRST (so subsequent imports/instrumentations see them)
    if enable_genai_content:
        enable_genai_content_recording(True, genai_content_mode)
    else:
        # Explicitly disable
        enable_genai_content_recording(False, "sanitized")
    if enable_semantic_kernel_diagnostics:
        enable_semantic_kernel_otel(True)
    else:
        enable_semantic_kernel_otel(False)

    config = get_config()   
    # Get from config if not provided
    customer = customer_name or config["customer_name"]
    agent = agent_name or config["agent_name"]
    
    # Validate customer and agent names - we don't validate connection strings here
    # since we have multiple connection strings
    if not customer:
        error_msg = "Customer name is required for service identification"
        logger.error(f"Configuration error: {error_msg}")
        raise ValueError(error_msg)
        
    if not agent:
        error_msg = "Agent name is required for instance identification"
        logger.error(f"Configuration error: {error_msg}")
        raise ValueError(error_msg)
    
    # Validate the format of customer and agent names
    from .utilities import validate_name_format
    validate_name_format(customer, agent)
    
    resource = build_default_resource(customer,agent)
    if views is None:
        views = default_views()
    if logger_names is None:
        logger_names = ["semantic_kernel", "azure", "azure.core"]

    common_exporter_kwargs = {
        "disable_offline_storage": disable_offline_storage,
    }

    # ---- Tracing ----
    tracer_provider = TracerProvider(
        sampler=ApplicationInsightsSampler(sampling_ratio=1.0),
        resource=resource,
    )
    configured_traces = 0
    for conn_str in connection_strings:
        if not conn_str:
            continue
        trace_exporter = AzureMonitorTraceExporter(connection_string=conn_str, **common_exporter_kwargs)
        tracer_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
        configured_traces += 1
    set_tracer_provider(tracer_provider)
    _logger.info("Tracing configured with %d exporters", configured_traces)

    # ---- Logging ----
    logger_provider = LoggerProvider(resource=resource)
    configured_logs = 0
    for conn_str in connection_strings:
        if not conn_str:
            continue
        log_exporter = AzureMonitorLogExporter(connection_string=conn_str, **common_exporter_kwargs)
        logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))
        configured_logs += 1
    _attach_logging_handlers(logger_provider, logger_names)
     
    _logger.info("Logging configured with %d exporters", configured_logs)

    # ---- Metrics ----
    readers = []
    configured_metrics = 0
    for conn_str in connection_strings:
        if not conn_str:
            continue
        metric_exporter = AzureMonitorMetricExporter(
            connection_string=conn_str,
            enable_live_metrics=enable_live_metrics,
            **common_exporter_kwargs,
        )
        readers.append(PeriodicExportingMetricReader(metric_exporter, export_interval_millis=metric_export_interval_millis))
        configured_metrics += 1

    meter_provider = MeterProvider(metric_readers=readers, resource=resource, views=views)
    set_meter_provider(meter_provider)
    _logger.info(
        "Metrics configured with %d exporters (live_metrics=%s, interval=%dms)",
        configured_metrics,
        enable_live_metrics,
        metric_export_interval_millis,
    )
   
    _install_instrumentations()

    _logger.info(
        "Azure Monitor multi-destination telemetry configured for %d connection strings "
        "(genai_content=%s, genai_mode=%s, sk_otel=%s)",
        len(connection_strings),
        enable_genai_content,
        genai_content_mode,
        enable_semantic_kernel_diagnostics,
    )

