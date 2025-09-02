"""Tests for Coalex metrics functionality."""

import json
import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from requests.exceptions import RequestException

from coalex.metrics import MetricRequest, MetricResponse, submit_metric


class TestMetricRequest:
    """Test MetricRequest class."""
    
    def test_metric_request_creation(self):
        """Test creating a MetricRequest with all parameters."""
        req = MetricRequest(
            request_id="req_123",
            metric_id="precision",
            value=0.85,
            metric_type="quality",
            metadata={"model": "v1.0"},
            agent_id="agent_123",
            reviewing_agent_id="reviewer_456",
            task_id="task_789"
        )
        
        assert req.request_id == "req_123"
        assert req.metric_id == "precision"
        assert req.value == 0.85
        assert req.metric_type == "quality"
        assert req.metadata == {"model": "v1.0"}
        assert req.agent_id == "agent_123"
        assert req.reviewing_agent_id == "reviewer_456"
        assert req.task_id == "task_789"
    
    def test_metric_request_minimal(self):
        """Test creating a MetricRequest with minimal parameters."""
        req = MetricRequest(
            request_id="req_123",
            metric_id="precision",
            value=0.85
        )
        
        assert req.request_id == "req_123"
        assert req.metric_id == "precision"
        assert req.value == 0.85
        assert req.metric_type is None
        assert req.metadata == {}
        assert req.agent_id is None
        assert req.reviewing_agent_id is None
        assert req.task_id is None


class TestMetricResponse:
    """Test MetricResponse class."""
    
    def test_metric_response_creation(self):
        """Test creating a MetricResponse."""
        created_at = datetime.now()
        resp = MetricResponse(
            id=1,
            agent_id="agent_123",
            account_id="account_456",
            request_id="req_123",
            metric_id="precision",
            metric_type="quality",
            value=0.85,
            metadata={"model": "v1.0"},
            reviewing_agent_id="reviewer_456",
            task_id="task_789",
            created_at=created_at
        )
        
        assert resp.id == 1
        assert resp.agent_id == "agent_123"
        assert resp.account_id == "account_456"
        assert resp.request_id == "req_123"
        assert resp.metric_id == "precision"
        assert resp.metric_type == "quality"
        assert resp.value == 0.85
        assert resp.metadata == {"model": "v1.0"}
        assert resp.reviewing_agent_id == "reviewer_456"
        assert resp.task_id == "task_789"
        assert resp.created_at == created_at


class TestSubmitMetric:
    """Test submit_metric function."""
    
    def test_submit_metric_missing_request_id(self):
        """Test submit_metric with missing request_id."""
        with pytest.raises(ValueError, match="request_id is required"):
            submit_metric(
                request_id="",
                metric_id="precision",
                value=0.85
            )
    
    def test_submit_metric_missing_metric_id(self):
        """Test submit_metric with missing metric_id."""
        with pytest.raises(ValueError, match="metric_id is required"):
            submit_metric(
                request_id="req_123",
                metric_id="",
                value=0.85
            )
    
    def test_submit_metric_missing_value(self):
        """Test submit_metric with missing value."""
        with pytest.raises(ValueError, match="value is required"):
            submit_metric(
                request_id="req_123",
                metric_id="precision",
                value=None
            )
    
    def test_submit_metric_invalid_value(self):
        """Test submit_metric with invalid value type."""
        with pytest.raises(ValueError, match="value must be a numeric type"):
            submit_metric(
                request_id="req_123",
                metric_id="precision",
                value="not_a_number"
            )
    
    def test_submit_metric_missing_agent_id(self):
        """Test submit_metric with missing agent_id when not auto-detected."""
        with patch('coalex.metrics._get_agent_id_from_tracer', return_value=None):
            with pytest.raises(ValueError, match="agent_id is required"):
                submit_metric(
                    request_id="req_123",
                    metric_id="precision",
                    value=0.85
                )
    
    @patch('coalex.metrics.requests.post')
    def test_submit_metric_success(self, mock_post):
        """Test successful metric submission."""
        # Mock response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "id": 1,
            "agent_id": "agent_123",
            "account_id": "account_456",
            "request_id": "req_123",
            "metric_id": "precision",
            "metric_type": "quality",
            "value": 0.85,
            "metadata": {"model": "v1.0"},
            "reviewing_agent_id": "reviewer_456",
            "task_id": "task_789",
            "created_at": "2023-01-01T00:00:00+00:00"
        }
        mock_post.return_value = mock_response
        
        # Call submit_metric
        result = submit_metric(
            request_id="req_123",
            metric_id="precision",
            value=0.85,
            metric_type="quality",
            metadata={"model": "v1.0"},
            agent_id="agent_123",
            reviewing_agent_id="reviewer_456",
            task_id="task_789"
        )
        
        # Verify request was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://creator.coalex.ai/metrics"  # First positional arg is URL
        assert call_args[1]['headers']['Content-Type'] == "application/json"
        
        payload = call_args[1]['json']
        assert payload['request_id'] == "req_123"
        assert payload['metric_id'] == "precision"
        assert payload['value'] == 0.85
        assert payload['metric_type'] == "quality"
        assert payload['metadata'] == {"model": "v1.0"}
        assert payload['agent_id'] == "agent_123"
        assert payload['reviewing_agent_id'] == "reviewer_456"
        assert payload['task_id'] == "task_789"
        
        # Verify response object
        assert isinstance(result, MetricResponse)
        assert result.id == 1
        assert result.agent_id == "agent_123"
        assert result.request_id == "req_123"
        assert result.metric_id == "precision"
        assert result.value == 0.85
    
    @patch('coalex.metrics.requests.post')
    def test_submit_metric_with_explicit_agent_id(self, mock_post):
        """Test metric submission with explicitly provided agent_id."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "id": 1,
            "agent_id": "explicit_agent",
            "account_id": "account_456",
            "request_id": "req_123",
            "metric_id": "precision",
            "value": 0.85,
            "metadata": {},
            "created_at": "2023-01-01T00:00:00+00:00"
        }
        mock_post.return_value = mock_response
        
        result = submit_metric(
            request_id="req_123",
            metric_id="precision",
            value=0.85,
            agent_id="explicit_agent"
        )
        
        # Verify the explicit agent_id was used
        payload = mock_post.call_args[1]['json']
        assert payload['agent_id'] == "explicit_agent"
        assert result.agent_id == "explicit_agent"
    
    @patch('coalex.metrics.requests.post')
    def test_submit_metric_http_error(self, mock_post):
        """Test metric submission with HTTP error."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = RequestException("HTTP 500")
        mock_post.return_value = mock_response
        
        with pytest.raises(RequestException):
            submit_metric(
                request_id="req_123",
                metric_id="precision",
                value=0.85,
                agent_id="agent_123"
            )
    
    @patch('coalex.metrics.requests.post')
    def test_submit_metric_invalid_response(self, mock_post):
        """Test metric submission with invalid response format."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"invalid": "response"}
        mock_post.return_value = mock_response
        
        with pytest.raises(ValueError, match="Invalid response from metrics service"):
            submit_metric(
                request_id="req_123",
                metric_id="precision",
                value=0.85,
                agent_id="agent_123"
            )
    
    @patch('coalex.metrics.requests.post')
    def test_submit_metric_custom_endpoint(self, mock_post):
        """Test metric submission with custom endpoint."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "id": 1,
            "agent_id": "agent_123",
            "account_id": "account_456",
            "request_id": "req_123",
            "metric_id": "precision",
            "value": 0.85,
            "metadata": {},
            "created_at": "2023-01-01T00:00:00+00:00"
        }
        mock_post.return_value = mock_response
        
        submit_metric(
            request_id="req_123",
            metric_id="precision",
            value=0.85,
            agent_id="agent_123",
            endpoint="https://custom.example.com"
        )
        
        # Verify custom endpoint was used
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://custom.example.com/metrics"
    
    @patch('coalex.metrics.requests.post')
    def test_submit_metric_defaults(self, mock_post):
        """Test metric submission uses correct defaults."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "id": 1,
            "agent_id": "agent_123",
            "account_id": "account_456",
            "request_id": "req_123",
            "metric_id": "precision",
            "value": 0.85,
            "metadata": {},
            "created_at": "2023-01-01T00:00:00+00:00"
        }
        mock_post.return_value = mock_response
        
        submit_metric(
            request_id="req_123",
            metric_id="precision",
            value=0.85,
            agent_id="agent_123"
        )
        
        # Verify defaults
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://creator.coalex.ai/metrics"
        assert call_args[1]['timeout'] == 30
        
        payload = call_args[1]['json']
        # Check that optional fields are not included when None/empty
        assert 'metric_type' not in payload
        assert 'reviewing_agent_id' not in payload  
        assert 'task_id' not in payload
        assert 'metadata' not in payload  # Empty dict not included
    
    @patch('coalex.metrics._get_agent_id_from_tracer')
    @patch('coalex.metrics.requests.post')
    def test_submit_metric_auto_detect_agent_id(self, mock_post, mock_get_agent):
        """Test metric submission with auto-detected agent_id."""
        mock_get_agent.return_value = "auto_detected_agent"
        
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "id": 1,
            "agent_id": "auto_detected_agent",
            "account_id": "account_456",
            "request_id": "req_123",
            "metric_id": "precision",
            "value": 0.85,
            "metadata": {},
            "created_at": "2023-01-01T00:00:00+00:00"
        }
        mock_post.return_value = mock_response
        
        result = submit_metric(
            request_id="req_123",
            metric_id="precision",
            value=0.85
        )
        
        # Verify auto-detected agent_id was used
        payload = mock_post.call_args[1]['json']
        assert payload['agent_id'] == "auto_detected_agent"
        assert result.agent_id == "auto_detected_agent"