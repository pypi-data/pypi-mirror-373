"""Validation utilities for Azure Monitor telemetry configuration."""

import logging
import os
import re
from typing import Dict, Optional, Tuple

logger = logging.getLogger("ntt_ai_observability")

def validate_telemetry_config(
    connection_string: Optional[str],
    customer_name: Optional[str], 
    agent_name: Optional[str],
    config: Dict[str, str]
) -> Tuple[str, str, str]:
    """
    Validate required telemetry configuration parameters.
    
    Args:
        connection_string: Azure Monitor connection string
        customer_name: Customer identifier for service.name
        agent_name: Agent identifier for service.instance.id
        config: Dictionary containing fallback values from environment variables
        
    Returns:
        Tuple[str, str, str]: Validated connection string, customer name, and agent name
        
    Raises:
        ValueError: If any required parameter is missing
    """
    # Get configuration with priority: args > env
    conn_str = connection_string or config.get("connection_string")
    customer = customer_name or config.get("customer_name")
    agent = agent_name or config.get("agent_name")
    
    # Validate required parameters
    if not conn_str:
        error_msg = "Azure Monitor connection string is required"
        logger.error(f"Configuration error: {error_msg}")
        raise ValueError(error_msg)
        
    if not customer:
        error_msg = "Customer name is required for service identification"
        logger.error(f"Configuration error: {error_msg}")
        raise ValueError(error_msg)
        
    if not agent:
        error_msg = "Agent name is required for instance identification"
        logger.error(f"Configuration error: {error_msg}")
        raise ValueError(error_msg)
       
    validate_name_format(customer, agent)

    # Log successful validation
    logger.info(f"Validated telemetry configuration for customer '{customer}', agent '{agent}'")
    
    return conn_str, customer, agent

def get_config() -> Dict[str, str]:
    """Get configuration from environment variables."""
    return {
        "connection_string": os.environ.get("AZURE_MONITOR_CONNECTION_STRING", ""),
        "customer_name": os.environ.get("CUSTOMER_NAME", ""),
        "agent_name": os.environ.get("AGENT_NAME", ""),
    }
        
def validate_name_format(customer_name: str, agent_name: str) -> None:
    """
    Validate customer and agent names according to Azure Monitor naming requirements.
    
    Args:
        customer_name: Customer identifier for service.name
        agent_name: Agent identifier for service.instance.id
        
    Raises:
        ValueError: If the test name does not meet the requirements
    """
    # Construct test name pattern
    test_name = f"{customer_name}_{agent_name}_liveness_test"
    
    # Check 1: Max length 260 characters
    if len(test_name) > 260:
        max_combined_length = 260 - len("__liveness_test")
        error_msg = f"Combined customer and agent name too long (max {max_combined_length} characters)"
        logger.error(f"Validation error: {error_msg}")
        raise ValueError(error_msg)

    # Check 2: No double hyphens
    if "--" in test_name:
        error_msg = "Customer and agent names cannot form a string with double hyphens"
        logger.error(f"Validation error: {error_msg}")
        raise ValueError(error_msg)
    
    # Check 3: Match regex pattern
    pattern = r"^[a-zA-Z0-9_-]+$"
    if not re.match(pattern, test_name):
        error_msg = "Combination of customer name and agent name must be less than 260 characters and should not use spaces or special characters like @, #, $, %,-- etc. Alphanumeric characters, double hyphens (--) and underscores (_) are allowed"
        logger.error(f"Validation error: {error_msg}")
        raise ValueError(error_msg)