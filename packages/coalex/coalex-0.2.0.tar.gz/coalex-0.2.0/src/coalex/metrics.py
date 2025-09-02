"""Coalex metrics functionality for performance tracking and monitoring."""

import logging
import requests
from typing import Dict, Any, Optional
from datetime import datetime
from opentelemetry import trace

logger = logging.getLogger(__name__)

DEFAULT_CREATOR_ENDPOINT = "https://creator.coalex.ai"

class MetricRequest:
    """Request object for metric submission."""
    
    def __init__(
        self,
        request_id: str,
        metric_id: str,
        value: float,
        metric_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        agent_id: Optional[str] = None,
        reviewing_agent_id: Optional[str] = None,
        task_id: Optional[str] = None
    ):
        self.request_id = request_id
        self.metric_id = metric_id
        self.value = value
        self.metric_type = metric_type
        self.metadata = metadata or {}
        self.agent_id = agent_id
        self.reviewing_agent_id = reviewing_agent_id
        self.task_id = task_id

class MetricResponse:
    """Response object for metric submissions."""
    
    def __init__(
        self, 
        id: int, 
        agent_id: str, 
        account_id: str,
        request_id: str,
        metric_id: str,
        metric_type: Optional[str],
        value: float,
        metadata: Dict[str, Any],
        reviewing_agent_id: Optional[str],
        task_id: Optional[str],
        created_at: datetime
    ):
        self.id = id
        self.agent_id = agent_id
        self.account_id = account_id
        self.request_id = request_id
        self.metric_id = metric_id
        self.metric_type = metric_type
        self.value = value
        self.metadata = metadata
        self.reviewing_agent_id = reviewing_agent_id
        self.task_id = task_id
        self.created_at = created_at

def _get_agent_id_from_tracer() -> Optional[str]:
    """Extract agent_id from the current tracer provider's resource."""
    try:
        tracer_provider = trace.get_tracer_provider()
        if hasattr(tracer_provider, 'resource'):
            return tracer_provider.resource.attributes.get('coalex.agent_id')
    except Exception as e:
        logger.warning(f"Failed to get agent_id from tracer: {e}")
    return None

def submit_metric(
    request_id: str,
    metric_id: str,
    value: float,
    metric_type: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    agent_id: Optional[str] = None,
    reviewing_agent_id: Optional[str] = None,
    task_id: Optional[str] = None,
    endpoint: Optional[str] = None
) -> MetricResponse:
    """
    Submit a metric for performance tracking and monitoring.
    
    This function sends a metric to the coalex-ai-creator service to be stored
    and made available for analysis and reporting.
    
    Args:
        request_id: Unique identifier for the request that generated this metric
        metric_id: Identifier for the type/name of metric being submitted
        value: Numeric value for the metric (typically a float/percentage)
        metric_type: Type category of the metric (e.g., "precision", "recall", "f1_score")
        metadata: Additional contextual data for the metric
        agent_id: Agent ID for authentication (auto-detected if None)
        reviewing_agent_id: ID of agent that reviewed/validated this metric
        task_id: Associated task identifier if applicable
        endpoint: Creator service endpoint (defaults to https://creator.coalex.ai)
        
    Returns:
        MetricResponse containing the stored metric data with server-generated fields
        
    Raises:
        ValueError: If required parameters are missing or invalid
        requests.RequestException: If the HTTP request fails
        
    Example:
        import coalex
        
        # Register coalex first
        coalex.register(agent_id="your-agent-id")
        
        # Submit a precision metric
        response = coalex.submit_metric(
            request_id="req_12345",
            metric_id="model_precision",
            value=0.92,
            metric_type="precision",
            metadata={"model_version": "v2.1.0", "dataset": "test_set_v1"}
        )
        
        print(f"Metric stored with ID: {response.id}")
    """
    if not request_id:
        raise ValueError("request_id is required")
    
    if not metric_id:
        raise ValueError("metric_id is required")
    
    if value is None:
        raise ValueError("value is required")
    
    try:
        # Ensure value is a float
        value = float(value)
    except (TypeError, ValueError):
        raise ValueError("value must be a numeric type convertible to float")
    
    # Auto-detect agent_id from tracer if not provided
    if not agent_id:
        agent_id = _get_agent_id_from_tracer()
        if not agent_id:
            raise ValueError("agent_id is required. Either pass it explicitly or ensure coalex.register() was called first.")
    
    # Use default endpoint if not provided
    if not endpoint:
        endpoint = DEFAULT_CREATOR_ENDPOINT
    
    # Create metric request
    metric_request = MetricRequest(
        request_id=request_id,
        metric_id=metric_id,
        value=value,
        metric_type=metric_type,
        metadata=metadata,
        agent_id=agent_id,
        reviewing_agent_id=reviewing_agent_id,
        task_id=task_id
    )
    
    # Prepare request payload
    payload = {
        "request_id": metric_request.request_id,
        "metric_id": metric_request.metric_id,
        "value": metric_request.value,
        "agent_id": metric_request.agent_id,
    }
    
    # Add optional fields if provided
    if metric_request.metric_type:
        payload["metric_type"] = metric_request.metric_type
    if metric_request.metadata:
        payload["metadata"] = metric_request.metadata
    if metric_request.reviewing_agent_id:
        payload["reviewing_agent_id"] = metric_request.reviewing_agent_id
    if metric_request.task_id:
        payload["task_id"] = metric_request.task_id
    
    # Prepare headers
    headers = {
        "Content-Type": "application/json"
    }
    
    # Build URL
    url = f"{endpoint}/metrics"
    
    logger.info(f"Submitting metric {metric_id} for request {request_id} (agent: {agent_id})")
    
    try:
        # Make HTTP request
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        # Check response status
        response.raise_for_status()
        
        # Parse response
        response_data = response.json()
        
        # Parse created_at timestamp
        created_at = datetime.fromisoformat(response_data["created_at"].replace('Z', '+00:00'))
        
        metric_response = MetricResponse(
            id=response_data["id"],
            agent_id=response_data["agent_id"],
            account_id=response_data["account_id"],
            request_id=response_data["request_id"],
            metric_id=response_data["metric_id"],
            metric_type=response_data.get("metric_type"),
            value=response_data["value"],
            metadata=response_data.get("metadata", {}),
            reviewing_agent_id=response_data.get("reviewing_agent_id"),
            task_id=response_data.get("task_id"),
            created_at=created_at
        )
        
        logger.info(f"Metric {metric_id} submitted successfully. ID: {metric_response.id}")
        
        return metric_response
        
    except requests.RequestException as e:
        logger.error(f"Failed to submit metric {metric_id} for request {request_id}: {e}")
        raise
    except (KeyError, ValueError) as e:
        logger.error(f"Invalid response format for metric {metric_id}: {e}")
        raise ValueError(f"Invalid response from metrics service: {e}")