"""Coalex OpenTelemetry registration and setup."""

import logging
import subprocess
from typing import Optional, Dict, Any
from contextlib import contextmanager
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
# Auto-instrumentation import removed - not working correctly

logger = logging.getLogger(__name__)

def get_gcp_token() -> Optional[str]:
    """Get GCP access token for temporary testing."""
    try:
        result = subprocess.run(
            ["gcloud", "auth", "print-access-token"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception as e:
        logger.warning(f"Failed to get GCP token: {e}")
    return None

DEFAULT_COALEX_ENDPOINT = "https://traces.coalex.ai/v1/traces"


def register(
    agent_id: str,
    endpoint: Optional[str] = None,
    auto_instrument: bool = False,
    service_name: str = "coalex-service",
    additional_attributes: Optional[Dict[str, Any]] = None,
) -> TracerProvider:
    """Register Coalex OpenTelemetry tracing with Coalex OTLP endpoint.
    
    Args:
        agent_id: Agent ID for authentication and identification
        endpoint: OTLP endpoint (defaults to Coalex traces endpoint)
        auto_instrument: Whether to enable auto-instrumentation
        service_name: Name of the service
        additional_attributes: Additional resource attributes
        
    Returns:
        Configured TracerProvider instance
    """
    if endpoint is None:
        endpoint = DEFAULT_COALEX_ENDPOINT
    
    # Create resource with service information
    resource_attributes = {
        "service.name": service_name,
        "service.version": "0.1.0",
        "coalex.agent_id": agent_id,
    }
    
    if additional_attributes:
        resource_attributes.update(additional_attributes)
    
    resource = Resource.create(resource_attributes)
    
    # Create tracer provider
    tracer_provider = TracerProvider(resource=resource)
    
    # Create OTLP exporter with agent_id in headers for auth
    headers = {
        "Authorization": f"Bearer {agent_id}",
        "X-Agent-ID": agent_id,
    }
    print(f"DEBUG: Using agent_id {agent_id} for authentication")
    
    exporter = OTLPSpanExporter(
        endpoint=endpoint,
        headers=headers,
    )
    
    # Create batch span processor
    span_processor = BatchSpanProcessor(exporter)
    tracer_provider.add_span_processor(span_processor)
    
    # Set as global tracer provider
    trace.set_tracer_provider(tracer_provider)
    
    # Auto-instrumentation note
    if auto_instrument:
        logger.info("Auto-instrumentation requested - please use specific instrumentors like VertexAIInstrumentor().instrument(tracer_provider=tracer_provider)")
    
    logger.info(f"Coalex tracing registered for agent {agent_id} -> {endpoint}")
    
    return tracer_provider


def add_request_context(request_id: str, prompt_version: str) -> None:
    """Add request context that will be available to all child spans.
    
    This creates a context span that ensures the attributes are properly
    propagated to any child spans (like LLM calls).
    
    Args:
        request_id: Unique request identifier
        prompt_version: Version of the prompt being used
    """
    from opentelemetry.trace import get_current_span
    
    # Try to add to current span first
    span = get_current_span()
    if span and span.is_recording():
        span.set_attribute("session.id", request_id)
        span.set_attribute("prompt.version", prompt_version)
        return
    
    # If no current span, we need to create a context span
    # This is handled by the context manager approach in user code
    logger.warning("add_request_context called without an active span. "
                  "Consider using coalex_context() context manager for better attribute propagation.")


@contextmanager
def coalex_context(request_id: str, prompt_version: str, span_name: str = "coalex_operation"):
    """Context manager that ensures Coalex attributes are propagated to child spans.
    
    Args:
        request_id: Unique request identifier
        prompt_version: Version of the prompt being used
        span_name: Name for the context span (optional)
        
    Example:
        with coalex_context("req_001", "v1.0.0"):
            # Any LLM calls here will inherit the attributes
            response = model.generate_content("Hello")
    """
    tracer = trace.get_tracer(__name__)
    
    # Get agent_id from the current tracer provider's resource
    agent_id = None
    tracer_provider = trace.get_tracer_provider()
    if hasattr(tracer_provider, 'resource'):
        agent_id = tracer_provider.resource.attributes.get('coalex.agent_id')
    
    with tracer.start_as_current_span(span_name) as span:
        # Set Coalex attributes (now in standard format)
        if agent_id:
            span.set_attribute("account_id", agent_id)
        span.set_attribute("session.id", request_id)
        span.set_attribute("prompt.version", prompt_version)
        
        yield span