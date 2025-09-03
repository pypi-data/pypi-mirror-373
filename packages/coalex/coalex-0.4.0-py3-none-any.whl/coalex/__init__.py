"""Coalex SDK for observability and monitoring."""

from .otel.register import register, add_request_context, coalex_context
from .approve import approve, ApprovalRequest, ApprovalResponse
from .metrics import submit_metric, MetricRequest, MetricResponse

__version__ = "0.4.0"

# Expose main functions
__all__ = [
    "register", 
    "add_request_context", 
    "coalex_context",
    "approve",
    "ApprovalRequest",
    "ApprovalResponse",
    "submit_metric",
    "MetricRequest",
    "MetricResponse"
]