"""
Nebula Client SDK - A clean, intuitive SDK for Nebula Cloud API

This SDK provides a simplified interface to Nebula's memory and retrieval capabilities,
focusing on chunks and hiding the complexity of the underlying Nebula system.
"""

from .client import NebulaClient
from .async_client import AsyncNebulaClient
from .exceptions import (
    NebulaException, 
    NebulaClientException,
    NebulaAuthenticationException,
    NebulaRateLimitException,
    NebulaValidationException,
    NebulaClusterNotFoundException,
)
from .models import Memory, MemoryResponse, Cluster, SearchResult, RetrievalType, AgentResponse

__version__ = "0.1.4"
__all__ = [
    "NebulaClient",
    "AsyncNebulaClient",
    "NebulaException", 
    "NebulaClientException",
    "NebulaAuthenticationException",
    "NebulaRateLimitException",
    "NebulaValidationException",
    "NebulaClusterNotFoundException",
    "Memory",
    "MemoryResponse",
    "Cluster",
    "SearchResult", 
    "RetrievalType",
    "AgentResponse",
] 