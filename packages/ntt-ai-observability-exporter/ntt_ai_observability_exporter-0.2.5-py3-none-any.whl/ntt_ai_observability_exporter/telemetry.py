"""Azure Telemetry Wrapper for NTT AI Observability."""

import logging
import os
import sys
from typing import Any, Dict, Optional

from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry.sdk.resources import Resource

from .utilities import get_config, validate_telemetry_config

# Configure package logger
logger = logging.getLogger("ntt_ai_observability")

# Don't add handlers if they're already configured to avoid duplicates
if not logger.handlers:
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    # Set propagate to True to ensure logs propagate to parent loggers
    logger.propagate = True


def configure_telemetry(
    connection_string: Optional[str] = None,
    customer_name: Optional[str] = None,
    agent_name: Optional[str] = None,
    enable_content_recording: bool = True,
    content_recording_mode: str = "all",
    enable_azure_monitor_tracing: bool = True
) -> bool:
    """
    Configure Azure Monitor OpenTelemetry for AI observability.
    Args:
        connection_string: Azure Monitor connection string
        customer_name: Customer identifier for service.name
        agent_name: Agent identifier for service.instance.id
        enable_content_recording: Enable AI content recording (default: True)
        content_recording_mode: Content recording mode - "all" or "sanitized" (default: "all")
        enable_azure_monitor_tracing: Enable Azure Monitor tracing (default: True)
    Returns:
        bool: True if configuration successful, False otherwise
    """
    try:
        # Force the logger to at least INFO level
        logger.setLevel(logging.INFO)
            
        # Set tracing environment variables based on parameters
        os.environ["AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED"] = str(enable_content_recording).lower()
        os.environ["AZURE_TRACING_GEN_AI_CONTENT_RECORDING_MODE"] = content_recording_mode
        os.environ["ENABLE_AZURE_MONITOR_TRACING"] = str(enable_azure_monitor_tracing).lower()
        

        logger.info("Set environment variables for AI telemetry")
        logger.info(f"  AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED={os.environ['AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED']}")
        logger.info(f"  AZURE_TRACING_GEN_AI_CONTENT_RECORDING_MODE={os.environ['AZURE_TRACING_GEN_AI_CONTENT_RECORDING_MODE']}")
        logger.info(f"  ENABLE_AZURE_MONITOR_TRACING={os.environ['ENABLE_AZURE_MONITOR_TRACING']}")
        
        # Get config with priority: args > env > constants
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
        logger.info(f"Configuring telemetry for customer '{customer}' with agent '{agent}'")

        # Create resource with custom attributes
        resource = Resource.create({
            "service.name": customer,
            "service.instance.id": agent,
            "service.version": "0.1.0"
        })
        # Configure Azure Monitor
        configure_azure_monitor(
            connection_string=conn_str,
            resource=resource,
            enable_live_metrics=True
        )
        logger.info("Azure Monitor telemetry configured successfully")
        return True
    except ValueError as e:
        # Log the error but re-raise it to stop client execution
        logger.error(f"Failed to configure Semantic Kernel telemetry: {e}")
        raise  # Re-raise the same exception
    except Exception as e:
        logger.error(f"Azure Monitor telemetry configuration failed: {e}")
        return False

