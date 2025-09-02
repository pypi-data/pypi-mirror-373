"""Tests for Coalex registration and utilities."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

from coalex.otel.register import register, add_request_context, coalex_context


class TestRegister:
    """Test cases for Coalex registration."""
    
    @patch('coalex.otel.register.OTLPSpanExporter')
    @patch('coalex.otel.register.BatchSpanProcessor')
    @patch('coalex.otel.register.TracerProvider')
    @patch('coalex.otel.register.trace.set_tracer_provider')
    def test_register_basic(self, mock_set_provider, mock_provider_class, mock_processor_class, mock_exporter_class):
        """Test basic registration functionality."""
        # Setup mocks
        mock_provider = Mock(spec=TracerProvider)
        mock_provider_class.return_value = mock_provider
        
        mock_exporter = Mock()
        mock_exporter_class.return_value = mock_exporter
        
        mock_processor = Mock()
        mock_processor_class.return_value = mock_processor
        
        # Call register
        result = register(agent_id="test-agent")
        
        # Verify exporter creation with correct headers
        mock_exporter_class.assert_called_once()
        call_args = mock_exporter_class.call_args
        assert call_args[1]['endpoint'] == "https://traces.coalex.ai/v1/traces"
        assert call_args[1]['headers']['Authorization'] == "Bearer test-agent"
        assert call_args[1]['headers']['X-Agent-ID'] == "test-agent"
        
        # Verify provider setup
        mock_provider.add_span_processor.assert_called_once_with(mock_processor)
        mock_set_provider.assert_called_once_with(mock_provider)
        
        assert result == mock_provider
    
    @patch('coalex.otel.register.OTLPSpanExporter')
    @patch('coalex.otel.register.BatchSpanProcessor')
    @patch('coalex.otel.register.TracerProvider')
    @patch('coalex.otel.register.trace.set_tracer_provider')
    def test_register_custom_endpoint(self, mock_set_provider, mock_provider_class, mock_processor_class, mock_exporter_class):
        """Test registration with custom endpoint."""
        register(agent_id="test-agent", endpoint="https://custom.endpoint.com/traces")
        
        call_args = mock_exporter_class.call_args
        assert call_args[1]['endpoint'] == "https://custom.endpoint.com/traces"


class TestAddRequestContext:
    """Test cases for add_request_context function."""
    
    @patch('opentelemetry.trace.get_current_span')
    def test_add_request_context_with_active_span(self, mock_get_span):
        """Test adding context to active span."""
        mock_span = Mock()
        mock_span.is_recording.return_value = True
        mock_get_span.return_value = mock_span
        
        add_request_context("req_123", "v1.0.0")
        
        mock_span.set_attribute.assert_any_call("session.id", "req_123")
        mock_span.set_attribute.assert_any_call("prompt.version", "v1.0.0")
    
    @patch('opentelemetry.trace.get_current_span')
    @patch('coalex.otel.register.logger')
    def test_add_request_context_without_active_span(self, mock_logger, mock_get_span):
        """Test adding context without active span."""
        mock_get_span.return_value = None
        
        add_request_context("req_123", "v1.0.0")
        
        mock_logger.warning.assert_called_once()


class TestCoalexContext:
    """Test cases for coalex_context context manager."""
    
    @patch('coalex.otel.register.trace.get_tracer')
    @patch('coalex.otel.register.trace.get_tracer_provider')
    def test_coalex_context(self, mock_get_provider, mock_get_tracer):
        """Test context manager functionality."""
        # Setup mocks
        mock_span = Mock()
        mock_tracer = Mock()
        mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
        mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
        mock_get_tracer.return_value = mock_tracer
        
        mock_provider = Mock()
        mock_provider.resource.attributes = {'coalex.agent_id': 'test-agent'}
        mock_get_provider.return_value = mock_provider
        
        # Use context manager
        with coalex_context("req_123", "v1.0.0", "test_operation"):
            pass
        
        # Verify span creation
        mock_tracer.start_as_current_span.assert_called_once_with("test_operation")
        
        # Verify attributes were set (via the mock span)
        mock_span.set_attribute.assert_any_call("account_id", "test-agent")
        mock_span.set_attribute.assert_any_call("session.id", "req_123")
        mock_span.set_attribute.assert_any_call("prompt.version", "v1.0.0")