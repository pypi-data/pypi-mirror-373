"""Tests for telemetry_multi module."""

import os
import pytest
from unittest.mock import Mock, patch, call, MagicMock
from ntt_ai_observability_exporter.telemetry_multi import (
    configure_telemetry_azure_monitor,
    enable_genai_content_recording,
    enable_semantic_kernel_otel,
    build_default_resource,
    default_views,
    _attach_logging_handlers,
    _install_instrumentations
)


class TestEnableGenAIContentRecording:
    """Test cases for enable_genai_content_recording function."""
    
    def setup_method(self):
        """Clean up environment variables before each test."""
        env_vars_to_clean = [
            "AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED",
            "AZURE_TRACING_GEN_AI_CONTENT_RECORDING_MODE",
            "ENABLE_AZURE_MONITOR_TRACING"
        ]
        for var in env_vars_to_clean:
            os.environ.pop(var, None)
    
    def test_enable_genai_content_recording_enabled_all_mode(self):
        """Test enabling GenAI content recording with 'all' mode."""
        enable_genai_content_recording(enabled=True, mode="all")
        
        assert os.environ["AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED"] == "true"
        assert os.environ["AZURE_TRACING_GEN_AI_CONTENT_RECORDING_MODE"] == "all"
        assert os.environ["ENABLE_AZURE_MONITOR_TRACING"] == "true"
    
    def test_enable_genai_content_recording_disabled(self):
        """Test disabling GenAI content recording."""
        enable_genai_content_recording(enabled=False, mode="all")
        
        assert os.environ["AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED"] == "false"
        assert os.environ["AZURE_TRACING_GEN_AI_CONTENT_RECORDING_MODE"] == "all"
    
    def test_enable_genai_content_recording_sanitized_mode(self):
        """Test enabling GenAI content recording with 'sanitized' mode."""
        enable_genai_content_recording(enabled=True, mode="sanitized")
        
        assert os.environ["AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED"] == "true"
        assert os.environ["AZURE_TRACING_GEN_AI_CONTENT_RECORDING_MODE"] == "sanitized"
    
    def test_enable_genai_content_recording_invalid_mode_normalized(self):
        """Test that invalid modes are normalized to 'sanitized'."""
        enable_genai_content_recording(enabled=True, mode="invalid_mode")
        
        assert os.environ["AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED"] == "true"
        assert os.environ["AZURE_TRACING_GEN_AI_CONTENT_RECORDING_MODE"] == "sanitized"
    
    def test_enable_genai_content_recording_redact_mode_normalized(self):
        """Test that 'redact' mode is normalized to 'sanitized'."""
        enable_genai_content_recording(enabled=True, mode="redact")
        
        assert os.environ["AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED"] == "true"
        assert os.environ["AZURE_TRACING_GEN_AI_CONTENT_RECORDING_MODE"] == "sanitized"


class TestEnableSemanticKernelOTEL:
    """Test cases for enable_semantic_kernel_otel function."""
    
    def setup_method(self):
        """Clean up environment variables before each test."""
        env_vars_to_clean = [
            "SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS",
            "SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS_SENSITIVE"
        ]
        for var in env_vars_to_clean:
            os.environ.pop(var, None)
    
    def test_enable_semantic_kernel_otel_enabled(self):
        """Test enabling Semantic Kernel OTEL diagnostics."""
        enable_semantic_kernel_otel(enabled=True)
        
        assert os.environ["SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS"] == "true"
        assert os.environ["SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS_SENSITIVE"] == "true"
    
    def test_enable_semantic_kernel_otel_disabled(self):
        """Test disabling Semantic Kernel OTEL diagnostics."""
        enable_semantic_kernel_otel(enabled=False)
        
        assert os.environ["SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS"] == "false"
        assert os.environ["SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS_SENSITIVE"] == "false"


class TestBuildDefaultResource:
    """Test cases for build_default_resource function."""
    
    def test_build_default_resource_minimal(self):
        """Test building resource with minimal parameters."""
        resource = build_default_resource(
            service_name="test-service",
            service_instance_id="test-instance"
        )
        
        attributes = resource.attributes
        assert attributes["service.name"] == "test-service"
        assert attributes["service.instance.id"] == "test-instance"
        assert "service.version" not in attributes
    
    def test_build_default_resource_with_version(self):
        """Test building resource with version."""
        resource = build_default_resource(
            service_name="test-service",
            service_instance_id="test-instance",
            service_version="1.0.0"
        )
        
        attributes = resource.attributes
        assert attributes["service.name"] == "test-service"
        assert attributes["service.instance.id"] == "test-instance"
        assert attributes["service.version"] == "1.0.0"
    
    def test_build_default_resource_with_extra_attributes(self):
        """Test building resource with extra attributes."""
        extra_attrs = {
            "environment": "test",
            "region": "us-east-1"
        }
        
        resource = build_default_resource(
            service_name="test-service",
            service_instance_id="test-instance",
            extra_attributes=extra_attrs
        )
        
        attributes = resource.attributes
        assert attributes["service.name"] == "test-service"
        assert attributes["service.instance.id"] == "test-instance"
        assert attributes["environment"] == "test"
        assert attributes["region"] == "us-east-1"


class TestDefaultViews:
    """Test cases for default_views function."""
    
    def test_default_views_structure(self):
        """Test that default views are properly structured."""
        views = default_views()
        
        assert len(views) >= 5  # Should have drop all + allow specific patterns
        
        # First view should drop everything
        drop_view = views[0]
        assert hasattr(drop_view, '_instrument_name') or hasattr(drop_view, 'instrument_name')
        
        # Check that specific patterns are allowed
        view_patterns = []
        for view in views[1:]:
            if hasattr(view, '_instrument_name'):
                view_patterns.append(view._instrument_name)
            elif hasattr(view, 'instrument_name'):
                view_patterns.append(view.instrument_name)
        
        assert "semantic_kernel*" in view_patterns
        assert "azure.*" in view_patterns
        assert "http.*" in view_patterns
        assert "ai.*" in view_patterns


class TestConfigureTelemetryAzureMonitor:
    """Test cases for configure_telemetry_azure_monitor function."""
    
    def setup_method(self):
        """Set up test environment."""
        # Clean up environment variables
        env_vars_to_clean = [
            "AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED",
            "AZURE_TRACING_GEN_AI_CONTENT_RECORDING_MODE",
            "ENABLE_AZURE_MONITOR_TRACING",
            "SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS",
            "SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS_SENSITIVE",
            "AZURE_MONITOR_CONNECTION_STRING",
            "CUSTOMER_NAME",
            "AGENT_NAME"
        ]
        for var in env_vars_to_clean:
            os.environ.pop(var, None)
    
    @patch('ntt_ai_observability_exporter.telemetry_multi.get_config')
    @patch('ntt_ai_observability_exporter.telemetry_multi.validate_telemetry_config')
    @patch('ntt_ai_observability_exporter.telemetry_multi._install_instrumentations')
    @patch('ntt_ai_observability_exporter.telemetry_multi.set_tracer_provider')
    @patch('ntt_ai_observability_exporter.telemetry_multi.set_meter_provider')
    @patch('ntt_ai_observability_exporter.telemetry_multi._attach_logging_handlers')
    @patch('ntt_ai_observability_exporter.telemetry_multi.AzureMonitorTraceExporter')
    @patch('ntt_ai_observability_exporter.telemetry_multi.AzureMonitorMetricExporter')
    @patch('ntt_ai_observability_exporter.telemetry_multi.AzureMonitorLogExporter')
    def test_configure_telemetry_azure_monitor_success(
        self, 
        mock_log_exporter,
        mock_metric_exporter,
        mock_trace_exporter,
        mock_attach_logging,
        mock_set_meter_provider,
        mock_set_tracer_provider,
        mock_install_instrumentations,
        mock_validate_config,
        mock_get_config
    ):
        """Test successful multi-destination telemetry configuration."""
        # Arrange
        connection_strings = [
            "InstrumentationKey=key1;IngestionEndpoint=https://endpoint1/",
            "InstrumentationKey=key2;IngestionEndpoint=https://endpoint2/"
        ]
        
        mock_get_config.return_value = {
            "customer_name": "test-customer",
            "agent_name": "test-agent"
        }
        mock_validate_config.return_value = ("test-customer", "test-agent")
        
        # Act
        configure_telemetry_azure_monitor(
            connection_strings=connection_strings,
            customer_name="test-customer",
            agent_name="test-agent"
        )
        
        # Assert
        mock_set_tracer_provider.assert_called_once()
        mock_set_meter_provider.assert_called_once()
        mock_attach_logging.assert_called_once()
        mock_install_instrumentations.assert_called_once()
        
        # Verify environment variables are set correctly
        assert os.environ["AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED"] == "true"
        assert os.environ["AZURE_TRACING_GEN_AI_CONTENT_RECORDING_MODE"] == "all"
        assert os.environ["SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS"] == "true"
        assert os.environ["SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS_SENSITIVE"] == "true"
    
    @patch('ntt_ai_observability_exporter.telemetry_multi.get_config')
    @patch('ntt_ai_observability_exporter.telemetry_multi.validate_telemetry_config')
    def test_configure_telemetry_azure_monitor_empty_connection_strings(
        self, 
        mock_validate_config,
        mock_get_config
    ):
        """Test configuration with empty connection strings raises ValueError."""
        with pytest.raises(ValueError, match="At least one valid connection string is required"):
            configure_telemetry_azure_monitor(connection_strings=[])
    
    @patch('ntt_ai_observability_exporter.telemetry_multi.get_config')
    @patch('ntt_ai_observability_exporter.telemetry_multi.validate_telemetry_config')
    def test_configure_telemetry_azure_monitor_none_connection_strings(
        self, 
        mock_validate_config,
        mock_get_config
    ):
        """Test configuration with None connection strings raises ValueError."""
        with pytest.raises(ValueError, match="At least one valid connection string is required"):
            configure_telemetry_azure_monitor(connection_strings=[None, "", None])
    
    @patch('ntt_ai_observability_exporter.telemetry_multi.get_config')
    @patch('ntt_ai_observability_exporter.telemetry_multi.validate_telemetry_config')
    @patch('ntt_ai_observability_exporter.telemetry_multi._install_instrumentations')
    @patch('ntt_ai_observability_exporter.telemetry_multi.set_tracer_provider')
    @patch('ntt_ai_observability_exporter.telemetry_multi.set_meter_provider')
    @patch('ntt_ai_observability_exporter.telemetry_multi._attach_logging_handlers')
    @patch('ntt_ai_observability_exporter.telemetry_multi.AzureMonitorTraceExporter')
    @patch('ntt_ai_observability_exporter.telemetry_multi.AzureMonitorMetricExporter')
    @patch('ntt_ai_observability_exporter.telemetry_multi.AzureMonitorLogExporter')
    def test_configure_telemetry_azure_monitor_with_disabled_features(
        self, 
        mock_log_exporter,
        mock_metric_exporter,
        mock_trace_exporter,
        mock_attach_logging,
        mock_set_meter_provider,
        mock_set_tracer_provider,
        mock_install_instrumentations,
        mock_validate_config,
        mock_get_config
    ):
        """Test configuration with disabled GenAI and SK features."""
        # Arrange
        connection_strings = ["InstrumentationKey=key1;IngestionEndpoint=https://endpoint1/"]
        
        mock_get_config.return_value = {
            "customer_name": "test-customer",
            "agent_name": "test-agent"
        }
        mock_validate_config.return_value = ("test-customer", "test-agent")
        
        # Act
        configure_telemetry_azure_monitor(
            connection_strings=connection_strings,
            customer_name="test-customer",
            agent_name="test-agent",
            enable_genai_content=False,
            enable_semantic_kernel_diagnostics=False
        )
        
        # Assert
        assert os.environ["AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED"] == "false"
        assert os.environ["SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS"] == "false"
        assert os.environ["SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS_SENSITIVE"] == "false"


class TestAttachLoggingHandlers:
    """Test cases for _attach_logging_handlers function."""
    
    def test_attach_logging_handlers_default_loggers(self):
        """Test attaching logging handlers to default loggers."""
        from opentelemetry.sdk._logs import LoggerProvider
        from opentelemetry.sdk.resources import Resource
        
        # Arrange
        resource = Resource.create({"service.name": "test"})
        logger_provider = LoggerProvider(resource=resource)
        
        # Act - Should not raise any exception
        try:
            _attach_logging_handlers(logger_provider)
            test_passed = True
        except Exception as e:
            test_passed = False
            print(f"Error: {e}")
        
        # Assert - The function should complete without error
        assert test_passed, "Function should complete without raising an exception"
    
    def test_attach_logging_handlers_custom_loggers(self):
        """Test attaching logging handlers to custom logger names."""
        from opentelemetry.sdk._logs import LoggerProvider
        from opentelemetry.sdk.resources import Resource
        
        # Arrange
        resource = Resource.create({"service.name": "test"})
        logger_provider = LoggerProvider(resource=resource)
        custom_loggers = ["custom.logger1", "custom.logger2"]
        
        # Act - Should not raise any exception
        try:
            _attach_logging_handlers(logger_provider, custom_loggers)
            test_passed = True
        except Exception as e:
            test_passed = False
            print(f"Error: {e}")
        
        # Assert - The function should complete without error
        assert test_passed, "Function should complete without raising an exception"


class TestInstallInstrumentations:
    """Test cases for _install_instrumentations function."""
    
    @patch('azure.core.settings.settings')
    @patch('opentelemetry.instrumentation.requests.RequestsInstrumentor')
    def test_install_instrumentations_basic(self, mock_requests_instrumentor, mock_azure_settings):
        """Test basic instrumentations installation."""
        # Arrange
        mock_instrumentor_instance = Mock()
        mock_requests_instrumentor.return_value = mock_instrumentor_instance
        
        # Act
        _install_instrumentations(enable_openai_instrumentation=False)
        
        # Assert
        mock_instrumentor_instance.instrument.assert_called_once()
    
    @patch('azure.core.settings.settings')
    @patch('opentelemetry.instrumentation.requests.RequestsInstrumentor')
    def test_install_instrumentations_with_openai(
        self, 
        mock_requests_instrumentor, 
        mock_azure_settings
    ):
        """Test instrumentations installation with OpenAI enabled."""
        # Arrange
        mock_requests_instance = Mock()
        mock_requests_instrumentor.return_value = mock_requests_instance
        
        # Act - call with OpenAI instrumentation enabled
        _install_instrumentations(enable_openai_instrumentation=True)
        
        # Assert - requests instrumentation should be called
        mock_requests_instance.instrument.assert_called_once()
        
        # Note: OpenAI instrumentation may not be available in test environment
        # but the function should handle this gracefully without failing
    
    @patch('azure.core.settings.settings')
    @patch('opentelemetry.instrumentation.requests.RequestsInstrumentor')
    def test_install_instrumentations_with_exceptions(self, mock_requests_instrumentor, mock_azure_settings):
        """Test instrumentations installation handles exceptions gracefully."""
        # Arrange
        mock_instrumentor_instance = Mock()
        mock_instrumentor_instance.instrument.side_effect = Exception("Instrumentation failed")
        mock_requests_instrumentor.return_value = mock_instrumentor_instance
        
        # Act & Assert - Should not raise exception
        _install_instrumentations()
        
        # Verify it attempted to instrument despite the exception
        mock_instrumentor_instance.instrument.assert_called_once()
