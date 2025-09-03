"""Coalex approval functionality for human-in-the-loop workflows."""

import logging
import requests
from typing import Dict, Any, Optional, Union
from datetime import datetime
from opentelemetry import trace

logger = logging.getLogger(__name__)

DEFAULT_CREATOR_ENDPOINT = "https://creator.coalex.ai"

class ApprovalRequest:
    """Request object for approval tasks."""
    
    def __init__(
        self,
        request_id: str,
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
        version: str = "1.0.0",
        sla_seconds: int = 3600,
        agent_id: Optional[str] = None,
        url_params: Optional[Dict[str, Any]] = None,
        eval: Optional[Union[str, bool]] = None
    ):
        self.request_id = request_id
        self.input_data = input_data or {}
        self.output_data = output_data or {}
        self.version = version
        self.sla_seconds = sla_seconds
        self.agent_id = agent_id
        self.url_params = url_params or {}
        self.eval = eval

class ApprovalResponse:
    """Response object for approval requests."""
    
    def __init__(
        self, 
        task_id: str, 
        request_id: str, 
        status: str, 
        sla_timestamp: datetime, 
        eval_id: Optional[str] = None,
        tuned_output_data: Optional[Dict[str, Any]] = None
    ):
        self.task_id = task_id
        self.request_id = request_id
        self.status = status
        self.sla_timestamp = sla_timestamp
        self.eval_id = eval_id
        self.tuned_output_data = tuned_output_data  # Auto-approved output data
        
    @property
    def is_auto_approved(self) -> bool:
        """Check if this request was auto-approved."""
        return self.status == "auto_approved"
        
    @property
    def needs_human_review(self) -> bool:
        """Check if this request needs human review."""
        return self.status == "pending"

def _get_agent_id_from_tracer() -> Optional[str]:
    """Extract agent_id from the current tracer provider's resource."""
    try:
        tracer_provider = trace.get_tracer_provider()
        if hasattr(tracer_provider, 'resource'):
            return tracer_provider.resource.attributes.get('coalex.agent_id')
    except Exception as e:
        logger.warning(f"Failed to get agent_id from tracer: {e}")
    return None

def approve(
    request_id: str,
    input_data: Optional[Dict[str, Any]] = None,
    output_data: Optional[Dict[str, Any]] = None,
    version: str = "1.0.0",
    sla_seconds: int = 3600,
    agent_id: Optional[str] = None,
    url_params: Optional[Dict[str, Any]] = None,
    eval: Optional[Union[str, bool]] = None,
    endpoint: Optional[str] = None
) -> ApprovalResponse:
    """
    Submit an approval request for human-in-the-loop review.
    
    This function sends a request to the coalex-ai-creator service to create
    an approval task that will be handled by a human reviewer.
    
    Args:
        request_id: Unique identifier for this approval request
        input_data: Input data that was provided to your AI system
        output_data: Output data that your AI system generated
        version: Version of your prompt/model (for tracking)
        sla_seconds: SLA in seconds for human review (default: 1 hour)
        agent_id: Agent ID for authentication (auto-detected if None)
        url_params: Additional URL parameters for the review interface
        eval: Evaluation control - str (use provided eval_id), True (generate eval_id), False/None (skip eval)
        endpoint: Creator service endpoint (defaults to https://creator.coalex.ai)
        
    Returns:
        ApprovalResponse containing task_id, request_id, status, and sla_timestamp
        
    Raises:
        ValueError: If required parameters are missing or invalid
        requests.RequestException: If the HTTP request fails
        
    Example:
        import coalex
        
        # Register coalex first
        coalex.register(agent_id="your-agent-id")
        
        # Submit approval request
        response = coalex.approve(
            request_id="req_12345",
            input_data={"user_query": "What is the weather?"},
            output_data={"response": "It's sunny today"},
            version="v1.2.0"
        )
        
        print(f"Approval task created: {response.task_id}")
    """
    if not request_id:
        raise ValueError("request_id is required")
    
    # Auto-detect agent_id from tracer if not provided
    if not agent_id:
        agent_id = _get_agent_id_from_tracer()
        if not agent_id:
            raise ValueError("agent_id is required. Either pass it explicitly or ensure coalex.register() was called first.")
    
    # Use default endpoint if not provided
    if not endpoint:
        endpoint = DEFAULT_CREATOR_ENDPOINT
    
    # Create approval request
    approval_request = ApprovalRequest(
        request_id=request_id,
        input_data=input_data,
        output_data=output_data,
        version=version,
        sla_seconds=sla_seconds,
        agent_id=agent_id,
        url_params=url_params,
        eval=eval
    )
    
    # Prepare request payload
    payload = {
        "request_id": approval_request.request_id,
        "input_data": approval_request.input_data,
        "output_data": approval_request.output_data,
        "version": approval_request.version,
        "sla_seconds": approval_request.sla_seconds,
        "agent_id": approval_request.agent_id,
        "url_params": approval_request.url_params,
        "eval": approval_request.eval
    }
    
    # Prepare headers for authentication
    headers = {
        "Authorization": f"Bearer {agent_id}",
        "Content-Type": "application/json"
    }
    
    # Build URL
    url = f"{endpoint}/approve"
    
    logger.info(f"Submitting approval request {request_id} for agent {agent_id}")
    
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
        
        # Convert sla_timestamp string back to datetime
        sla_timestamp = datetime.fromisoformat(response_data["sla_timestamp"].replace('Z', '+00:00'))
        
        approval_response = ApprovalResponse(
            task_id=response_data["task_id"],
            request_id=response_data["request_id"],
            status=response_data["status"],
            sla_timestamp=sla_timestamp,
            eval_id=response_data.get("eval_id"),
            tuned_output_data=response_data.get("tuned_output_data")
        )
        
        logger.info(f"Approval request {request_id} submitted successfully. Task ID: {approval_response.task_id}")
        
        return approval_response
        
    except requests.RequestException as e:
        logger.error(f"Failed to submit approval request {request_id}: {e}")
        raise
    except (KeyError, ValueError) as e:
        logger.error(f"Invalid response format for approval request {request_id}: {e}")
        raise ValueError(f"Invalid response from approval service: {e}")