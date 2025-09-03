"""Semantic Kernel telemetry integration for Azure Monitor."""

import logging
import os
from typing import Any, Dict, Optional

from azure.monitor.opentelemetry.exporter import (AzureMonitorLogExporter,
                                                  AzureMonitorMetricExporter,
                                                  AzureMonitorTraceExporter)
from opentelemetry._logs import set_logger_provider
from opentelemetry.metrics import set_meter_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.metrics.view import DropAggregation, View
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import set_tracer_provider

from .utilities import get_config, validate_telemetry_config

logger = logging.getLogger("ntt_ai_observability")
    
def configure_semantic_kernel_telemetry(
    connection_string: Optional[str] = None,
    customer_name: Optional[str] = None,
    agent_name: Optional[str] = None,
    enable_content_recording: bool = True,
    metric_export_interval_ms: int = 5000
) -> bool:
    """
    Configure Azure Monitor OpenTelemetry specifically for Semantic Kernel.
    
    This method should be called BEFORE creating any Semantic Kernel instances.
    
    Args:
        connection_string: Azure Monitor connection string
        customer_name: Customer identifier for service.name
        agent_name: Agent identifier for service.instance.id
        enable_content_recording: Enable sensitive content recording (default: True)
        metric_export_interval_ms: Metric export interval in milliseconds (default: 5000)
        
    Returns:
        bool: True if configuration successful, False otherwise
    """
    try:
        logger.setLevel(logging.INFO)
        logger.info("Configuring Semantic Kernel telemetry...")
        
        # Set environment variables specific to Semantic Kernel
        os.environ["SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS"] = "true"
        os.environ["SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS_SENSITIVE"] = str(enable_content_recording).lower()
        
        # Get configuration with priority: args > env
        config = get_config()
        conn_str = connection_string or config["connection_string"]
        customer = customer_name or config["customer_name"]
        agent = agent_name or config["agent_name"]
        
        # Validate required parameters
        conn_str, customer, agent = validate_telemetry_config(
            connection_string, 
            customer_name, 
            agent_name, 
            config
        )
            
        # Create resource with custom attributes
        resource = Resource.create({
            "service.name": customer,
            "service.instance.id": agent,
            "service.version": "0.1.0"
        })
        
        # 1. Set up logging with Azure Monitor
        def set_up_logging():
            exporter = AzureMonitorLogExporter.from_connection_string(conn_str)
            
            logger_provider = LoggerProvider(resource=resource)
            logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
            set_logger_provider(logger_provider)
            
            # Create handler with filter for semantic_kernel logs
            handler = LoggingHandler()
            handler.addFilter(logging.Filter("semantic_kernel"))
            
            # Configure root logger
            root_logger = logging.getLogger()
            root_logger.addHandler(handler)
            root_logger.setLevel(logging.INFO)
            
        # 2. Set up tracing with Azure Monitor
        def set_up_tracing():
            exporter = AzureMonitorTraceExporter.from_connection_string(conn_str)
            
            tracer_provider = TracerProvider(resource=resource)
            tracer_provider.add_span_processor(BatchSpanProcessor(exporter))
            set_tracer_provider(tracer_provider)
        
        # 3. Set up metrics with Azure Monitor
        def set_up_metrics():
            exporter = AzureMonitorMetricExporter.from_connection_string(conn_str)
            
            meter_provider = MeterProvider(
                metric_readers=[
                    PeriodicExportingMetricReader(
                        exporter, 
                        export_interval_millis=metric_export_interval_ms
                    )
                ],
                resource=resource,
                views=[
                    # Drop all metrics except those from Semantic Kernel
                    View(instrument_name="*", aggregation=DropAggregation()),
                    View(instrument_name="semantic_kernel*"),
                ],
            )
            set_meter_provider(meter_provider)
        
        # Execute the setup functions in the correct order
        set_up_logging()
        set_up_tracing()
        set_up_metrics()
        
        logger.info(f"Semantic Kernel telemetry configured successfully for '{customer}'")
        return True
    except ValueError as e:
        # Log the error but re-raise it to stop client execution
        logger.error(f"Failed to configure Semantic Kernel telemetry: {e}")
        raise  # Re-raise the same exception    
    except Exception as e:
        logger.error(f"Failed to configure Semantic Kernel telemetry: {e}")
        return False