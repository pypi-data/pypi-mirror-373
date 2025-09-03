"""Tests for coalex.approve functionality."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
import requests

from coalex import approve, ApprovalRequest, ApprovalResponse


def test_approval_request_creation():
    """Test ApprovalRequest object creation."""
    req = ApprovalRequest(
        request_id="test_req_123",
        input_data={"query": "test"},
        output_data={"response": "test response"},
        version="1.0.0",
        sla_seconds=1800,
        agent_id="test_agent",
        url_params={"param1": "value1"}
    )
    
    assert req.request_id == "test_req_123"
    assert req.input_data == {"query": "test"}
    assert req.output_data == {"response": "test response"}
    assert req.version == "1.0.0"
    assert req.sla_seconds == 1800
    assert req.agent_id == "test_agent"
    assert req.url_params == {"param1": "value1"}


def test_approval_response_creation():
    """Test ApprovalResponse object creation."""
    sla_time = datetime.now()
    resp = ApprovalResponse(
        task_id="task_123",
        request_id="req_123",
        status="PENDING",
        sla_timestamp=sla_time
    )
    
    assert resp.task_id == "task_123"
    assert resp.request_id == "req_123"
    assert resp.status == "PENDING"
    assert resp.sla_timestamp == sla_time


def test_approve_missing_request_id():
    """Test that approve raises ValueError when request_id is missing."""
    with pytest.raises(ValueError, match="request_id is required"):
        approve("", agent_id="test_agent")


def test_approve_missing_agent_id():
    """Test that approve raises ValueError when agent_id is missing and not in tracer."""
    with patch('coalex.approve._get_agent_id_from_tracer', return_value=None):
        with pytest.raises(ValueError, match="agent_id is required"):
            approve("test_req_123")


@patch('requests.post')
@patch('coalex.approve._get_agent_id_from_tracer')
def test_approve_success(mock_get_agent, mock_post):
    """Test successful approve call."""
    # Mock agent_id from tracer
    mock_get_agent.return_value = "test_agent_123"
    
    # Mock successful HTTP response
    mock_response = Mock()
    mock_response.json.return_value = {
        "task_id": "task_456",
        "request_id": "req_123",
        "status": "PENDING",
        "sla_timestamp": "2024-01-01T12:00:00Z"
    }
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response
    
    # Call approve function
    result = approve(
        request_id="req_123",
        input_data={"query": "test"},
        output_data={"response": "test response"},
        version="1.0.0"
    )
    
    # Verify request was made correctly
    mock_post.assert_called_once()
    call_args = mock_post.call_args
    
    assert call_args[1]['json']['request_id'] == "req_123"
    assert call_args[1]['json']['agent_id'] == "test_agent_123"
    assert call_args[1]['json']['input_data'] == {"query": "test"}
    assert call_args[1]['json']['output_data'] == {"response": "test response"}
    assert call_args[1]['json']['version'] == "1.0.0"
    assert call_args[1]['headers']['Authorization'] == "Bearer test_agent_123"
    assert call_args[1]['headers']['Content-Type'] == "application/json"
    
    # Verify response
    assert isinstance(result, ApprovalResponse)
    assert result.task_id == "task_456"
    assert result.request_id == "req_123"
    assert result.status == "PENDING"


@patch('requests.post')
def test_approve_with_explicit_agent_id(mock_post):
    """Test approve with explicitly provided agent_id."""
    # Mock successful HTTP response
    mock_response = Mock()
    mock_response.json.return_value = {
        "task_id": "task_456",
        "request_id": "req_123", 
        "status": "PENDING",
        "sla_timestamp": "2024-01-01T12:00:00Z"
    }
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response
    
    # Call approve with explicit agent_id
    approve(
        request_id="req_123",
        agent_id="explicit_agent_456"
    )
    
    # Verify agent_id was used correctly
    call_args = mock_post.call_args
    assert call_args[1]['json']['agent_id'] == "explicit_agent_456"
    assert call_args[1]['headers']['Authorization'] == "Bearer explicit_agent_456"


@patch('requests.post')
def test_approve_http_error(mock_post):
    """Test approve handles HTTP errors correctly."""
    # Mock HTTP error
    mock_post.side_effect = requests.RequestException("Connection failed")
    
    with pytest.raises(requests.RequestException):
        approve("req_123", agent_id="test_agent")


@patch('requests.post')
def test_approve_invalid_response(mock_post):
    """Test approve handles invalid response format."""
    # Mock response with missing fields
    mock_response = Mock()
    mock_response.json.return_value = {"incomplete": "response"}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response
    
    with pytest.raises(ValueError, match="Invalid response from approval service"):
        approve("req_123", agent_id="test_agent")


@patch('requests.post')
def test_approve_custom_endpoint(mock_post):
    """Test approve with custom endpoint."""
    # Mock successful HTTP response
    mock_response = Mock()
    mock_response.json.return_value = {
        "task_id": "task_456",
        "request_id": "req_123",
        "status": "PENDING", 
        "sla_timestamp": "2024-01-01T12:00:00Z"
    }
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response
    
    custom_endpoint = "https://custom.coalex.ai"
    
    approve(
        request_id="req_123",
        agent_id="test_agent",
        endpoint=custom_endpoint
    )
    
    # Verify custom endpoint was used
    call_args = mock_post.call_args
    assert call_args[0][0] == f"{custom_endpoint}/approve"


def test_approve_defaults():
    """Test approve function with default values."""
    with patch('requests.post') as mock_post:
        # Mock successful HTTP response
        mock_response = Mock()
        mock_response.json.return_value = {
            "task_id": "task_456", 
            "request_id": "req_123",
            "status": "PENDING",
            "sla_timestamp": "2024-01-01T12:00:00Z"
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        approve("req_123", agent_id="test_agent")
        
        # Verify defaults were applied
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        
        assert payload['input_data'] == {}
        assert payload['output_data'] == {}
        assert payload['version'] == "1.0.0"
        assert payload['sla_seconds'] == 3600
        assert payload['url_params'] == {}