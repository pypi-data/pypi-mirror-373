"""Unit tests for Semantic Kernel telemetry configuration."""

import logging
import os
import unittest
from unittest.mock import MagicMock, Mock, patch

from ntt_ai_observability_exporter.semantic_kernel_telemetry import \
    configure_semantic_kernel_telemetry


class TestSemanticKernelTelemetry(unittest.TestCase):
    """Test cases for Semantic Kernel telemetry configuration."""

    def setUp(self):
        """Set up test environment."""
        # Clean up environment variables before each test
        env_vars_to_clean = [
            "AZURE_MONITOR_CONNECTION_STRING",
            "CUSTOMER_NAME", 
            "AGENT_NAME",
            "SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS",
            "SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS_SENSITIVE"
        ]
        for var in env_vars_to_clean:
            if var in os.environ:
                del os.environ[var]

    def tearDown(self):
        """Clean up after each test."""
        # Clean up environment variables after each test
        env_vars_to_clean = [
            "AZURE_MONITOR_CONNECTION_STRING",
            "CUSTOMER_NAME",
            "AGENT_NAME", 
            "SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS",
            "SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS_SENSITIVE"
        ]
        for var in env_vars_to_clean:
            if var in os.environ:
                del os.environ[var]

    @patch("ntt_ai_observability_exporter.semantic_kernel_telemetry.set_meter_provider")
    @patch("ntt_ai_observability_exporter.semantic_kernel_telemetry.set_tracer_provider")
    @patch("ntt_ai_observability_exporter.semantic_kernel_telemetry.set_logger_provider")
    @patch("ntt_ai_observability_exporter.semantic_kernel_telemetry.AzureMonitorLogExporter")
    @patch("ntt_ai_observability_exporter.semantic_kernel_telemetry.AzureMonitorTraceExporter")
    @patch("ntt_ai_observability_exporter.semantic_kernel_telemetry.AzureMonitorMetricExporter")
    def test_configure_semantic_kernel_telemetry_with_params(
        self, 
        mock_metric_exporter,
        mock_trace_exporter, 
        mock_log_exporter,
        mock_set_logger_provider,
        mock_set_tracer_provider,
        mock_set_meter_provider
    ):
        """Test configuring semantic kernel telemetry with parameters."""
        # Arrange
        mock_log_exporter.from_connection_string.return_value = MagicMock()
        mock_trace_exporter.from_connection_string.return_value = MagicMock()
        mock_metric_exporter.from_connection_string.return_value = MagicMock()
        
        # Act
        result = configure_semantic_kernel_telemetry(
            connection_string="InstrumentationKey=test-key",
            customer_name="test-customer",
            agent_name="test-agent"
        )
        
        # Assert
        self.assertTrue(result)
        
        # Check Semantic Kernel environment variables are set
        self.assertEqual(
            os.environ["SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS"], 
            "true"
        )
        self.assertEqual(
            os.environ["SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS_SENSITIVE"], 
            "true"
        )
        
        # Verify exporters were created with connection string
        mock_log_exporter.from_connection_string.assert_called_once_with("InstrumentationKey=test-key")
        mock_trace_exporter.from_connection_string.assert_called_once_with("InstrumentationKey=test-key")
        mock_metric_exporter.from_connection_string.assert_called_once_with("InstrumentationKey=test-key")
        
        # Verify providers were set
        mock_set_logger_provider.assert_called_once()
        mock_set_tracer_provider.assert_called_once()
        mock_set_meter_provider.assert_called_once()

    @patch("ntt_ai_observability_exporter.semantic_kernel_telemetry.set_meter_provider")
    @patch("ntt_ai_observability_exporter.semantic_kernel_telemetry.set_tracer_provider")
    @patch("ntt_ai_observability_exporter.semantic_kernel_telemetry.set_logger_provider")
    @patch("ntt_ai_observability_exporter.semantic_kernel_telemetry.AzureMonitorLogExporter")
    @patch("ntt_ai_observability_exporter.semantic_kernel_telemetry.AzureMonitorTraceExporter")
    @patch("ntt_ai_observability_exporter.semantic_kernel_telemetry.AzureMonitorMetricExporter")
    def test_configure_semantic_kernel_telemetry_with_env_vars(
        self,
        mock_metric_exporter,
        mock_trace_exporter,
        mock_log_exporter,
        mock_set_logger_provider,
        mock_set_tracer_provider,
        mock_set_meter_provider
    ):
        """Test configuring semantic kernel telemetry with environment variables."""
        # Arrange
        mock_log_exporter.from_connection_string.return_value = MagicMock()
        mock_trace_exporter.from_connection_string.return_value = MagicMock()
        mock_metric_exporter.from_connection_string.return_value = MagicMock()
        
        os.environ["AZURE_MONITOR_CONNECTION_STRING"] = "InstrumentationKey=env-test-key"
        os.environ["CUSTOMER_NAME"] = "env-customer"
        os.environ["AGENT_NAME"] = "env-agent"
        
        try:
            # Act
            result = configure_semantic_kernel_telemetry()
            
            # Assert
            self.assertTrue(result)
            mock_log_exporter.from_connection_string.assert_called_once_with("InstrumentationKey=env-test-key")
            mock_trace_exporter.from_connection_string.assert_called_once_with("InstrumentationKey=env-test-key")
            mock_metric_exporter.from_connection_string.assert_called_once_with("InstrumentationKey=env-test-key")
        finally:
            # Clean up is handled by tearDown
            pass

    @patch("ntt_ai_observability_exporter.semantic_kernel_telemetry.set_meter_provider")
    @patch("ntt_ai_observability_exporter.semantic_kernel_telemetry.set_tracer_provider")
    @patch("ntt_ai_observability_exporter.semantic_kernel_telemetry.set_logger_provider")
    @patch("ntt_ai_observability_exporter.semantic_kernel_telemetry.AzureMonitorLogExporter")
    @patch("ntt_ai_observability_exporter.semantic_kernel_telemetry.AzureMonitorTraceExporter")
    @patch("ntt_ai_observability_exporter.semantic_kernel_telemetry.AzureMonitorMetricExporter")
    def test_configure_semantic_kernel_telemetry_content_recording_disabled(
        self,
        mock_metric_exporter,
        mock_trace_exporter,
        mock_log_exporter,
        mock_set_logger_provider,
        mock_set_tracer_provider,
        mock_set_meter_provider
    ):
        """Test configuring semantic kernel telemetry with content recording disabled."""
        # Arrange
        mock_log_exporter.from_connection_string.return_value = MagicMock()
        mock_trace_exporter.from_connection_string.return_value = MagicMock()
        mock_metric_exporter.from_connection_string.return_value = MagicMock()
        
        # Act
        result = configure_semantic_kernel_telemetry(
            connection_string="InstrumentationKey=test-key",
            customer_name="test-customer",
            agent_name="test-agent",
            enable_content_recording=False
        )
        
        # Assert
        self.assertTrue(result)
        self.assertEqual(
            os.environ["SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS_SENSITIVE"], 
            "false"
        )

    @patch("ntt_ai_observability_exporter.semantic_kernel_telemetry.set_meter_provider")
    @patch("ntt_ai_observability_exporter.semantic_kernel_telemetry.set_tracer_provider")
    @patch("ntt_ai_observability_exporter.semantic_kernel_telemetry.set_logger_provider")
    @patch("ntt_ai_observability_exporter.semantic_kernel_telemetry.AzureMonitorLogExporter")
    @patch("ntt_ai_observability_exporter.semantic_kernel_telemetry.AzureMonitorTraceExporter")
    @patch("ntt_ai_observability_exporter.semantic_kernel_telemetry.AzureMonitorMetricExporter")
    def test_configure_semantic_kernel_telemetry_custom_metric_interval(
        self,
        mock_metric_exporter,
        mock_trace_exporter,
        mock_log_exporter,
        mock_set_logger_provider,
        mock_set_tracer_provider,
        mock_set_meter_provider
    ):
        """Test configuring semantic kernel telemetry with custom metric export interval."""
        # Arrange
        mock_log_exporter.from_connection_string.return_value = MagicMock()
        mock_trace_exporter.from_connection_string.return_value = MagicMock()
        mock_metric_exporter.from_connection_string.return_value = MagicMock()
        
        # Act
        result = configure_semantic_kernel_telemetry(
            connection_string="InstrumentationKey=test-key",
            customer_name="test-customer",
            agent_name="test-agent",
            metric_export_interval_ms=10000
        )
        
        # Assert
        self.assertTrue(result)
        # Note: The metric interval is used internally in PeriodicExportingMetricReader
        # We can verify the providers were set up correctly
        mock_set_meter_provider.assert_called_once()

    def test_configure_semantic_kernel_telemetry_missing_connection_string(self):
        """Test that missing connection string raises ValueError."""
        with self.assertRaises(ValueError) as context:
            configure_semantic_kernel_telemetry(
                customer_name="test-customer",
                agent_name="test-agent"
            )
        
        self.assertIn("Azure Monitor connection string is required", str(context.exception))

    def test_configure_semantic_kernel_telemetry_missing_customer_name(self):
        """Test that missing customer name raises ValueError."""
        with self.assertRaises(ValueError) as context:
            configure_semantic_kernel_telemetry(
                connection_string="InstrumentationKey=test-key",
                agent_name="test-agent"
            )
        
        self.assertIn("Customer name is required for service identification", str(context.exception))

    def test_configure_semantic_kernel_telemetry_missing_agent_name(self):
        """Test that missing agent name raises ValueError."""
        with self.assertRaises(ValueError) as context:
            configure_semantic_kernel_telemetry(
                connection_string="InstrumentationKey=test-key",
                customer_name="test-customer"
            )
        
        self.assertIn("Agent name is required for instance identification", str(context.exception))

    def test_configure_semantic_kernel_telemetry_invalid_customer_name(self):
        """Test that invalid customer name raises ValueError."""
        with self.assertRaises(ValueError) as context:
            configure_semantic_kernel_telemetry(
                connection_string="InstrumentationKey=test-key",
                customer_name="invalid name with spaces",
                agent_name="test-agent"
            )
        
        self.assertIn("should not use spaces or special characters", str(context.exception))

    def test_configure_semantic_kernel_telemetry_invalid_agent_name(self):
        """Test that invalid agent name raises ValueError."""
        with self.assertRaises(ValueError) as context:
            configure_semantic_kernel_telemetry(
                connection_string="InstrumentationKey=test-key",
                customer_name="test-customer",
                agent_name="invalid@agent#name"
            )
        
        self.assertIn("should not use spaces or special characters", str(context.exception))

    @patch("ntt_ai_observability_exporter.semantic_kernel_telemetry.AzureMonitorLogExporter")
    def test_configure_semantic_kernel_telemetry_azure_monitor_exception(self, mock_log_exporter):
        """Test handling of Azure Monitor connection exceptions."""
        # Arrange
        mock_log_exporter.from_connection_string.side_effect = Exception("Azure Monitor connection failed")
        
        # Act
        result = configure_semantic_kernel_telemetry(
            connection_string="InstrumentationKey=test-key",
            customer_name="test-customer",
            agent_name="test-agent"
        )
        
        # Assert
        self.assertFalse(result)

    @patch("ntt_ai_observability_exporter.semantic_kernel_telemetry.set_meter_provider")
    @patch("ntt_ai_observability_exporter.semantic_kernel_telemetry.set_tracer_provider")
    @patch("ntt_ai_observability_exporter.semantic_kernel_telemetry.set_logger_provider")
    @patch("ntt_ai_observability_exporter.semantic_kernel_telemetry.AzureMonitorLogExporter")
    @patch("ntt_ai_observability_exporter.semantic_kernel_telemetry.AzureMonitorTraceExporter")
    @patch("ntt_ai_observability_exporter.semantic_kernel_telemetry.AzureMonitorMetricExporter")
    @patch("ntt_ai_observability_exporter.semantic_kernel_telemetry.Resource")
    def test_configure_semantic_kernel_telemetry_resource_creation(
        self,
        mock_resource,
        mock_metric_exporter,
        mock_trace_exporter,
        mock_log_exporter,
        mock_set_logger_provider,
        mock_set_tracer_provider,
        mock_set_meter_provider
    ):
        """Test that resource is created with correct attributes."""
        # Arrange
        mock_resource_instance = MagicMock()
        mock_resource.create.return_value = mock_resource_instance
        mock_log_exporter.from_connection_string.return_value = MagicMock()
        mock_trace_exporter.from_connection_string.return_value = MagicMock()
        mock_metric_exporter.from_connection_string.return_value = MagicMock()
        
        # Act
        result = configure_semantic_kernel_telemetry(
            connection_string="InstrumentationKey=test-key",
            customer_name="test-customer",
            agent_name="test-agent"
        )
        
        # Assert
        self.assertTrue(result)
        mock_resource.create.assert_called_once_with({
            "service.name": "test-customer",
            "service.instance.id": "test-agent",
            "service.version": "0.1.0"
        })

    @patch("ntt_ai_observability_exporter.semantic_kernel_telemetry.set_meter_provider")
    @patch("ntt_ai_observability_exporter.semantic_kernel_telemetry.set_tracer_provider")
    @patch("ntt_ai_observability_exporter.semantic_kernel_telemetry.set_logger_provider")
    @patch("ntt_ai_observability_exporter.semantic_kernel_telemetry.AzureMonitorLogExporter")
    @patch("ntt_ai_observability_exporter.semantic_kernel_telemetry.AzureMonitorTraceExporter")
    @patch("ntt_ai_observability_exporter.semantic_kernel_telemetry.AzureMonitorMetricExporter")
    def test_configure_semantic_kernel_telemetry_parameters_override_env(
        self,
        mock_metric_exporter,
        mock_trace_exporter,
        mock_log_exporter,
        mock_set_logger_provider,
        mock_set_tracer_provider,
        mock_set_meter_provider
    ):
        """Test that function parameters override environment variables."""
        # Arrange
        mock_log_exporter.from_connection_string.return_value = MagicMock()
        mock_trace_exporter.from_connection_string.return_value = MagicMock()
        mock_metric_exporter.from_connection_string.return_value = MagicMock()
        
        # Set environment variables
        os.environ["AZURE_MONITOR_CONNECTION_STRING"] = "InstrumentationKey=env-key"
        os.environ["CUSTOMER_NAME"] = "env-customer"
        os.environ["AGENT_NAME"] = "env-agent"
        
        try:
            # Act - parameters should override environment variables
            result = configure_semantic_kernel_telemetry(
                connection_string="InstrumentationKey=param-key",
                customer_name="param-customer",
                agent_name="param-agent"
            )
            
            # Assert
            self.assertTrue(result)
            # Verify that parameter values were used, not environment values
            mock_log_exporter.from_connection_string.assert_called_once_with("InstrumentationKey=param-key")
            mock_trace_exporter.from_connection_string.assert_called_once_with("InstrumentationKey=param-key")
            mock_metric_exporter.from_connection_string.assert_called_once_with("InstrumentationKey=param-key")
        finally:
            # Clean up is handled by tearDown
            pass

    @patch("ntt_ai_observability_exporter.semantic_kernel_telemetry.set_meter_provider")
    @patch("ntt_ai_observability_exporter.semantic_kernel_telemetry.set_tracer_provider")
    @patch("ntt_ai_observability_exporter.semantic_kernel_telemetry.set_logger_provider")
    @patch("ntt_ai_observability_exporter.semantic_kernel_telemetry.AzureMonitorLogExporter")
    @patch("ntt_ai_observability_exporter.semantic_kernel_telemetry.AzureMonitorTraceExporter")
    @patch("ntt_ai_observability_exporter.semantic_kernel_telemetry.AzureMonitorMetricExporter")
    def test_configure_semantic_kernel_telemetry_logging_configuration(
        self,
        mock_metric_exporter,
        mock_trace_exporter,
        mock_log_exporter,
        mock_set_logger_provider,
        mock_set_tracer_provider,
        mock_set_meter_provider
    ):
        """Test that logging is configured correctly."""
        # Arrange
        mock_log_exporter.from_connection_string.return_value = MagicMock()
        mock_trace_exporter.from_connection_string.return_value = MagicMock()
        mock_metric_exporter.from_connection_string.return_value = MagicMock()
        
        # Act
        result = configure_semantic_kernel_telemetry(
            connection_string="InstrumentationKey=test-key",
            customer_name="test-customer",
            agent_name="test-agent"
        )
        
        # Assert
        self.assertTrue(result)
        # Verify providers were set up correctly
        mock_set_logger_provider.assert_called_once()
        mock_set_tracer_provider.assert_called_once()
        mock_set_meter_provider.assert_called_once()


if __name__ == "__main__":
    unittest.main()
