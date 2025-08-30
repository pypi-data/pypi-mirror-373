"""
Data models for the Nebula Client SDK
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum


class RetrievalType(str, Enum):
    """Types of retrieval available"""
    BASIC = "basic"
    ADVANCED = "advanced"
    CUSTOM = "custom"


@dataclass
class MemoryResponse:
    """Read model returned by list/get operations.

    Notes:
    - Exactly one of `content` or `chunks` is typically present for text documents
    - `cluster_ids` reflects collections the document belongs to
    - Not used for writes; use `Memory` for store_memory/store_memories
    """

    id: str
    content: Optional[str] = None
    chunks: Optional[List[str]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    cluster_ids: List[str] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Memory":
        """Create a Memory from a dictionary"""
        created_at = None
        if data.get("created_at"):
            if isinstance(data["created_at"], str):
                created_at = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
            elif isinstance(data["created_at"], datetime):
                created_at = data["created_at"]

        updated_at = None
        if data.get("updated_at"):
            if isinstance(data["updated_at"], str):
                updated_at = datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
            elif isinstance(data["updated_at"], datetime):
                updated_at = data["updated_at"]

        # Handle chunk response format (API returns chunks, not memories)
        memory_id = str(data.get("id", ""))
        
        # Prefer explicit chunks if present; otherwise map 'text'/'content' → content
        content: Optional[str] = data.get("content") or data.get("text")
        chunks: Optional[List[str]] = None
        if "chunks" in data and isinstance(data["chunks"], list):
            if all(isinstance(x, str) for x in data["chunks"]):
                chunks = data["chunks"]
            else:
                # Some APIs may return list of objects with a 'text' field
                extracted: List[str] = []
                for item in data["chunks"]:
                    if isinstance(item, dict) and "text" in item:
                        extracted.append(item["text"])  # type: ignore[index]
                chunks = extracted or None
        
        # API returns 'collection_ids', store as cluster_ids for user consistency
        metadata = data.get("metadata", {})
        cluster_ids = data.get("collection_ids", [])
        if data.get("document_id"):
            metadata["document_id"] = data["document_id"]
        
        # Handle document-based approach - if this is a document response
        if data.get("document_id") and not memory_id:
            memory_id = data["document_id"]
        
        # If we have document metadata, merge it
        if data.get("document_metadata"):
            metadata.update(data["document_metadata"])

        return cls(
            id=memory_id,
            content=content,
            chunks=chunks,
            metadata=metadata,
            cluster_ids=cluster_ids,
            created_at=created_at,
            updated_at=updated_at
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Memory to dictionary"""
        result = {
            "id": self.id,
            "content": self.content,
            "chunks": self.chunks,
            "metadata": self.metadata,
            "cluster_ids": self.cluster_ids,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        return result


@dataclass
class Memory:
    """Unified input model for writing memories via store_memory/store_memories.

    Behavior:
    - role present → conversation message
      - parent_id used as conversation_id if provided; else a new conversation is created
      - content is sent as the message text; metadata is attached per message
      - store methods return the conversation_id
    - role absent → text/json document
      - content is stored as raw text; metadata is merged and augmented with a content hash
      - store methods return the document_id
    """

    cluster_id: str
    content: str
    role: Optional[str] = None  # user, assistant, or custom
    parent_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Cluster:
    """A cluster of memories in Nebula (alias for Collection)"""

    id: str
    name: str
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    memory_count: int = 0
    owner_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Cluster":
        """Create a Cluster from a dictionary"""
        created_at = None
        if data.get("created_at"):
            if isinstance(data["created_at"], str):
                created_at = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
            elif isinstance(data["created_at"], datetime):
                created_at = data["created_at"]

        updated_at = None
        if data.get("updated_at"):
            if isinstance(data["updated_at"], str):
                updated_at = datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
            elif isinstance(data["updated_at"], datetime):
                updated_at = data["updated_at"]

        # Handle different field mappings from API response
        cluster_id = str(data.get("id", ""))  # Convert UUID to string
        cluster_name = data.get("name", "")
        cluster_description = data.get("description")
        cluster_owner_id = str(data.get("owner_id", "")) if data.get("owner_id") else None
        
        # Map API fields to SDK fields
        # API has document_count, SDK expects memory_count
        memory_count = data.get("document_count", 0)
        
        # Create metadata from API-specific fields
        metadata = {
            "graph_cluster_status": data.get("graph_cluster_status", ""),
            "graph_sync_status": data.get("graph_sync_status", ""),
            "user_count": data.get("user_count", 0),
            "document_count": data.get("document_count", 0)
        }

        return cls(
            id=cluster_id,
            name=cluster_name,
            description=cluster_description,
            metadata=metadata,
            created_at=created_at,
            updated_at=updated_at,
            memory_count=memory_count,
            owner_id=cluster_owner_id
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Cluster to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "memory_count": self.memory_count,
            "owner_id": self.owner_id,
        }


class GraphSearchResultType(str, Enum):
    ENTITY = "entity"
    RELATIONSHIP = "relationship"
    COMMUNITY = "community"


@dataclass
class GraphEntityResult:
    id: Optional[str]
    name: str
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphRelationshipResult:
    id: Optional[str]
    subject: str
    predicate: str
    object: str
    subject_id: Optional[str] = None
    object_id: Optional[str] = None
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphCommunityResult:
    id: Optional[str]
    name: str
    summary: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchResult:
    """Unified search result from Nebula (chunk or graph).

    - For chunk results, `content` is populated and graph_* fields are None.
    - For graph results, one of graph_entity/graph_relationship/graph_community is populated,
      and `graph_result_type` indicates which. `content` may include a human-readable fallback.
    """

    id: str
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    source: Optional[str] = None

    # Chunk fields
    content: Optional[str] = None

    # Graph variant discriminator and payload
    graph_result_type: Optional[GraphSearchResultType] = None
    graph_entity: Optional[GraphEntityResult] = None
    graph_relationship: Optional[GraphRelationshipResult] = None
    graph_community: Optional[GraphCommunityResult] = None
    chunk_ids: Optional[List[str]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SearchResult":
        """Create a chunk-style SearchResult from a dictionary."""
        content = data.get("content") or data.get("text", "")
        result_id = data.get("id") or data.get("chunk_id", "")
        return cls(
            id=str(result_id),
            content=str(content),
            score=float(data.get("score", 0.0)),
            metadata=data.get("metadata", {}) or {},
            source=data.get("source"),
        )

    @classmethod
    def from_graph_dict(cls, data: Dict[str, Any]) -> "SearchResult":
        """Create a graph-style SearchResult (entity/relationship/community).

        Assumes server returns a valid result_type and well-formed content.
        """
        rid = str(data["id"]) if "id" in data else ""
        rtype = GraphSearchResultType(data["result_type"])  # strict
        content = data.get("content", {}) or {}
        score = float(data.get("score", 0.0)) if data.get("score") is not None else 0.0
        metadata = data.get("metadata", {}) or {}
        chunk_ids = data.get("chunk_ids") if isinstance(data.get("chunk_ids"), list) else None

        # Build typed content only (no text fallbacks for production cleanliness)
        entity: Optional[GraphEntityResult] = None
        rel: Optional[GraphRelationshipResult] = None
        comm: Optional[GraphCommunityResult] = None

        if rtype == GraphSearchResultType.ENTITY:
            entity = GraphEntityResult(
                id=str(content.get("id")) if content.get("id") else None,
                name=content.get("name", ""),
                description=content.get("description", ""),
                metadata=content.get("metadata", {}) or {},
            )
        elif rtype == GraphSearchResultType.RELATIONSHIP:
            rel = GraphRelationshipResult(
                id=str(content.get("id")) if content.get("id") else None,
                subject=content.get("subject", ""),
                predicate=content.get("predicate", ""),
                object=content.get("object", ""),
                subject_id=str(content.get("subject_id")) if content.get("subject_id") else None,
                object_id=str(content.get("object_id")) if content.get("object_id") else None,
                description=content.get("description"),
                metadata=content.get("metadata", {}) or {},
            )
        else:
            comm = GraphCommunityResult(
                id=str(content.get("id")) if content.get("id") else None,
                name=content.get("name", ""),
                summary=content.get("summary", ""),
                metadata=content.get("metadata", {}) or {},
            )

        return cls(
            id=rid,
            score=score,
            metadata=metadata,
            source="graph",
            content=None,
            graph_result_type=rtype,
            graph_entity=entity,
            graph_relationship=rel,
            graph_community=comm,
            chunk_ids=chunk_ids,
        )


@dataclass
class AgentResponse:
    """A response from an agent"""

    content: str
    agent_id: str
    conversation_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    citations: List[Dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentResponse":
        """Create an AgentResponse from a dictionary"""
        return cls(
            content=data["content"],
            agent_id=data["agent_id"],
            conversation_id=data.get("conversation_id"),
            metadata=data.get("metadata", {}),
            citations=data.get("citations", [])
        )


@dataclass
class SearchOptions:
    """Options for search operations"""

    limit: int = 10
    filters: Optional[Dict[str, Any]] = None
    retrieval_type: RetrievalType = RetrievalType.ADVANCED


# @dataclass
# class AgentOptions:
#     """Options for agent operations"""
# 
#     model: str = "gpt-4"
#     temperature: float = 0.7
#     max_tokens: Optional[int] = None
#     retrieval_type: RetrievalType = RetrievalType.SIMPLE 