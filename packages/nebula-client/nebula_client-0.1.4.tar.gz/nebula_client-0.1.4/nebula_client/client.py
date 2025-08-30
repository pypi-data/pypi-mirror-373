"""
Main client for the Nebula Client SDK
"""

import os
import json
import hashlib
import uuid
from typing import Any, Dict, List, Optional, Union
import httpx
from urllib.parse import urljoin

from .exceptions import (
    NebulaException,
    NebulaClientException,
    NebulaAuthenticationException,
    NebulaRateLimitException,
    NebulaValidationException,
    NebulaClusterNotFoundException,
)
from .models import MemoryResponse, Memory, Cluster, SearchResult, RetrievalType


class NebulaClient:
    """
    Simple client for interacting with Nebula Cloud API
    
    This client provides a clean interface to Nebula's memory and retrieval capabilities,
    focusing on the core functionality without the complexity of the underlying Nebula system.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.nebulacloud.app",
        timeout: float = 30.0,
    ):
        """
        Initialize the Nebula client
        
        Args:
            api_key: Your Nebula API key. If not provided, will look for NEBULA_API_KEY env var
            base_url: Base URL for the Nebula API
            timeout: Request timeout in seconds
        """
        self.api_key = api_key or os.getenv("NEBULA_API_KEY")
        if not self.api_key:
            raise NebulaClientException(
                "API key is required. Pass it to the constructor or set NEBULA_API_KEY environment variable."
            )
        
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client = httpx.Client(timeout=timeout)
        # Lazily initialized tokenizer encoder for token counting
        self._token_encoder = None  # type: ignore[var-annotated]
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def close(self):
        """Close the HTTP client"""
        self._client.close()
    
    
    
    def _is_nebula_api_key(self, token: Optional[str] = None) -> bool:
        """Detect if a token looks like an Nebula API key (public.raw).
        
        Heuristic:
        - Exactly one dot
        - Public part starts with "key_"
        """
        candidate = token or self.api_key
        if not candidate:
            return False
        if candidate.count(".") != 1:
            return False
        public_part, raw_part = candidate.split(".", 1)
        return public_part.startswith("key_") and len(raw_part) > 0

    def _build_auth_headers(self, include_content_type: bool = True) -> Dict[str, str]:
        """Build authentication headers.
        
        - If the provided credential looks like an Nebula API key, send it via X-API-Key
          to avoid JWT parsing on Supabase-auth deployments.
        - Otherwise, send it as a Bearer token.
        - Optionally include Content-Type: application/json for JSON requests.
        """
        headers: Dict[str, str] = {}
        if self._is_nebula_api_key():
            headers["X-API-Key"] = self.api_key  # type: ignore[arg-type]
        else:
            headers["Authorization"] = f"Bearer {self.api_key}"
        if include_content_type:
            headers["Content-Type"] = "application/json"
        return headers
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the Nebula API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., "/v3/documents")
            json_data: JSON data to send in request body
            params: Query parameters
            
        Returns:
            Response data as dictionary
            
        Raises:
            NebulaException: For API errors
            NebulaClientException: For client errors
        """
        url = urljoin(self.base_url, endpoint)
        headers = self._build_auth_headers(include_content_type=True)
        
        try:
            response = self._client.request(
                method=method,
                url=url,
                headers=headers,
                json=json_data,
                params=params,
            )
            
            # Handle different response status codes
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise NebulaAuthenticationException("Invalid API key")
            elif response.status_code == 429:
                raise NebulaRateLimitException("Rate limit exceeded")
            elif response.status_code == 400:
                error_data = response.json() if response.content else {}
                raise NebulaValidationException(
                    error_data.get("message", "Validation error"),
                    error_data.get("details")
                )
            else:
                error_data = response.json() if response.content else {}
                raise NebulaException(
                    error_data.get("message", f"API error: {response.status_code}"),
                    response.status_code,
                    error_data
                )
                
        except httpx.ConnectError as e:
            raise NebulaClientException(
                f"Failed to connect to {self.base_url}. Check your internet connection.",
                e
            )
        except httpx.TimeoutException as e:
            raise NebulaClientException(
                f"Request timed out after {self.timeout} seconds",
                e
            )
        except httpx.RequestError as e:
            raise NebulaClientException(f"Request failed: {str(e)}", e)
    
    # Cluster Management Methods
    
    def create_cluster(
        self,
        name: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Cluster:
        """
        Create a new cluster
        """
        data = {
            "name": name,
        }
        if description:
            data["description"] = description
        if metadata:
            data["metadata"] = metadata
        
        response = self._make_request("POST", "/v3/collections", json_data=data)
        # Unwrap 'results' if present
        if isinstance(response, dict) and "results" in response:
            response = response["results"]
        return Cluster.from_dict(response)
    
    def get_cluster(self, cluster_id: str) -> Cluster:
        """
        Get a specific cluster by ID
        
        Args:
            cluster_id: ID of the cluster to retrieve
            
        Returns:
            Cluster object
        """
        response = self._make_request("GET", f"/v3/collections/{cluster_id}")
        # Unwrap 'results' if present
        if isinstance(response, dict) and "results" in response:
            response = response["results"]
        return Cluster.from_dict(response)
    
    def get_cluster_by_name(self, name: str) -> Cluster:
        """
        Get a specific cluster by name using the dedicated endpoint.
        """
        response = self._make_request("GET", f"/v3/collections/name/{name}")
        if isinstance(response, dict) and "results" in response:
            response = response["results"]
        return Cluster.from_dict(response)
    
    def list_clusters(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Cluster]:
        """
        Get all clusters
        
        Args:
            limit: Maximum number of clusters to return
            offset: Number of clusters to skip
            
        Returns:
            List of Cluster objects
        """
        params = {
            "limit": limit,
            "offset": offset,
        }
        
        response = self._make_request("GET", "/v3/collections", params=params)
        
        if isinstance(response, dict) and "results" in response:
            clusters = response["results"]
        elif isinstance(response, list):
            clusters = response
        else:
            clusters = [response]
        
        return [Cluster.from_dict(cluster) for cluster in clusters]
    
    def update_cluster(
        self,
        cluster_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Cluster:
        """
        Update a cluster
        
        Args:
            cluster_id: ID of the cluster to update
            name: New name for the cluster
            description: New description for the cluster
            metadata: New metadata for the cluster
            
        Returns:
            Updated Cluster object
        """
        # Existence validated server-side
        
        data = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if metadata is not None:
            data["metadata"] = metadata
        
        response = self._make_request("POST", f"/v3/collections/{cluster_id}", json_data=data)
        # Unwrap 'results' if present
        if isinstance(response, dict) and "results" in response:
            response = response["results"]
        return Cluster.from_dict(response)
    
    def delete_cluster(self, cluster_id: str) -> bool:
        """
        Delete a cluster
        
        Args:
            cluster_id: ID of the cluster to delete
            
        Returns:
            True if successful
        """
        # Existence validated server-side
        
        self._make_request("DELETE", f"/v3/collections/{cluster_id}")
        return True

    # MemoryResponse Management Methods
    
    # def store(
    #     self,
    #     content: str,
    #     cluster_id: str,
    #     metadata: Optional[Dict[str, Any]] = None,
    #     *,
    #     chunks: Optional[List[str]] = None,
    #     memory_type: str = "text",
    #     conversation_id: Optional[str] = None,
    #     role: str = "user",
    # ) -> str:
    #     """
    #     Store a memory.

    #     Exactly one of `content` or `chunks` must be provided and each must be
    #     under the 8,192 token limit. If both or neither are provided, a
    #     validation error is raised. To signify "no content" when passing
    #     `chunks`, pass an empty string for `content`.

    #     Notes for text mode:
    #     - There is a maximum of 100 chunks allowed per document when using this SDK.
    #       If you need to exceed this, prefer sending `raw_text` and letting the server
    #       chunk, or batch your chunks across multiple documents.

    #     Notes for conversation mode:
    #     - cluster_id is required and will be sent as collection_id so the backend assigns the conversation to the desired collection.

    #     Args:
    #         content: Raw text to store. Must be <= 8192 tokens if provided.
    #         cluster_id: Cluster ID to store the memory in (required)
    #         metadata: Additional metadata for the memory
    #         chunks: Pre-chunked text segments. Each must be <= 8192 tokens.

    #     Returns:
    #         MemoryResponse object
    #     """
    #     if memory_type == "conversation":
    #         conv_id = conversation_id
    #         if not conv_id:
    #             create_payload: Dict[str, Any] = {}
    #             response = self._make_request("POST", "/v3/conversations", json_data=create_payload)
    #             conv = response["results"] if isinstance(response, dict) and "results" in response else response
    #             conv_id = conv.get("id") if isinstance(conv, dict) else None
    #             if not conv_id:
    #                 raise NebulaClientException("Failed to create conversation: no id returned")

    #         add_msg_payload = {
    #             "messages": [
    #                 {
    #                     "content": content,
    #                     "role": role,
    #                     "metadata": metadata or {},
    #                 }
    #             ],
    #             "collection_id": cluster_id,
    #         }
    #         _ = self._make_request("POST", f"/v3/conversations/{conv_id}/messages", json_data=add_msg_payload)
    #         return str(conv_id)

    #     # Existence validated server-side

    #     MAX_TOKENS_PER_FIELD = 8192

    #     def _get_encoder():
    #         # Lazy import to avoid hard dependency during import time
    #         if self._token_encoder is None:
    #             try:
    #                 import tiktoken  # type: ignore
    #             except Exception as e:  # pragma: no cover
    #                 raise NebulaClientException(
    #                     "tiktoken is required for token counting. Please install it with `pip install tiktoken`.",
    #                     e,
    #                 )
    #             # Use cl100k_base which matches GPT-3.5/4 family and text-embedding-3 models
    #             self._token_encoder = tiktoken.get_encoding("cl100k_base")
    #         return self._token_encoder

    #     # Validate exclusivity
    #     has_content = content is not None and content != ""
    #     has_chunks = chunks is not None and len(chunks) > 0
    #     if has_content and has_chunks:
    #         raise NebulaValidationException(
    #             "Provide either 'content' or 'chunks', not both.")
    #     if not has_content and not has_chunks:
    #         raise NebulaValidationException(
    #             "Either 'content' or 'chunks' must be provided.")

    #     # Token checks
    #     encoder = _get_encoder()
    #     if has_content:
    #         content_tokens = len(encoder.encode(content or ""))
    #         if content_tokens > MAX_TOKENS_PER_FIELD:
    #             raise NebulaValidationException(
    #                 f"Content is too long: {content_tokens} tokens. Max allowed is {MAX_TOKENS_PER_FIELD} tokens.")
    #     if has_chunks:
    #         for idx, ch in enumerate(chunks or []):
    #             ch_tokens = len(encoder.encode(ch))
    #             if ch_tokens > MAX_TOKENS_PER_FIELD:
    #                 raise NebulaValidationException(
    #                     f"Chunk {idx + 1} is too long: {ch_tokens} tokens. Max allowed is {MAX_TOKENS_PER_FIELD} tokens.")

    #     # Prepare metadata
    #     doc_metadata = metadata or {}
    #     doc_metadata["memory_type"] = "memory"
        
    #     # Generate deterministic document ID for deduplication
    #     if has_content:
    #         content_text_for_hash = content or ""
    #     else:
    #         # Hash joined chunks when provided
    #         content_text_for_hash = "\n".join(chunks or [])
    #     content_hash = hashlib.sha256(content_text_for_hash.encode("utf-8")).hexdigest()
    #     deterministic_doc_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, content_hash))
        
    #     # Use form data for document creation (like the original Nebula SDK)
    #     # Prefer sending explicit chunks when provided to avoid server-side partitioning
    #     data: Dict[str, Any] = {
    #         "metadata": json.dumps({**doc_metadata, "content_hash": content_hash}),
    #         "ingestion_mode": "fast",
    #         "collection_ids": json.dumps([cluster_id]),
    #     }
    #     if has_chunks:
    #         data["chunks"] = json.dumps(chunks)
    #     else:
    #         data["raw_text"] = content or ""
        
    #     # Create document using the documents endpoint with form data
    #     url = f"{self.base_url}/v3/documents"
    #     # For form-data, let httpx set the Content-Type; just add auth header
    #     headers = self._build_auth_headers(include_content_type=False)
        
    #     try:
    #         response = self._client.post(url, data=data, headers=headers)
            
    #         if response.status_code not in (200, 202):
    #             error_data = response.json() if response.content else {}
    #             raise NebulaException(
    #                 error_data.get("message", f"Failed to create document: {response.status_code}"),
    #                 response.status_code,
    #                 error_data
    #             )
            
    #         response_data = response.json()
            
    #         # Extract document ID from response
    #         if isinstance(response_data, dict) and "results" in response_data:
    #             # Try to get the actual document ID from the response
    #             if "document_id" in response_data["results"]:
    #                 doc_id = response_data["results"]["document_id"]
    #             elif "id" in response_data["results"]:
    #                 doc_id = response_data["results"]["id"]
    #             else:
    #                 doc_id = deterministic_doc_id
    #         else:
    #             doc_id = deterministic_doc_id
                
    #     except Exception as e:
    #         # If duplicate (HTTP 409 or similar) just skip
    #         err_msg = str(e).lower()
    #         if any(token in err_msg for token in ["conflict", "already exists", "duplicate"]):
    #             # Return a memory object for the existing document
    #             memory_data = {
    #                 "id": deterministic_doc_id,
    #                 "content": content if has_content else None,
    #                 "chunks": chunks if has_chunks else None,
    #                 "metadata": doc_metadata,
    #                 "collection_ids": [cluster_id]
    #             }
    #             return MemoryResponse.from_dict(memory_data)
    #         # For other errors, re-raise
    #         raise
        
    #     # Return a memory object
    #     memory_data = {
    #         "id": doc_id,
    #         "content": content if has_content else None,
    #         "chunks": chunks if has_chunks else None,
    #         "metadata": doc_metadata,
    #         "collection_ids": [cluster_id]
    #     }
    #     return str(doc_id)

    # New unified write APIs
    def store_memory(self, memory: Union[Memory, Dict[str, Any]] = None, **kwargs) -> str:
        """Store a single memory.

        Accepts either a `Memory` object or equivalent keyword arguments:
        - cluster_id: str
        - content: str
        - role: Optional[str]
        - parent_id: Optional[str]
        - metadata: Optional[dict]

        Returns: parent_id (conversation_id for conversations; document_id for text/json)
        """
        # Allow either Memory object or equivalent keyword params
        if memory is None:
            # Build from kwargs
            memory = Memory(
                cluster_id=kwargs["cluster_id"],
                content=kwargs["content"],
                role=kwargs.get("role"),
                parent_id=kwargs.get("parent_id"),
                metadata=kwargs.get("metadata", {}),
            )
        elif isinstance(memory, dict):
            memory = Memory(
                cluster_id=memory["cluster_id"],
                content=memory["content"],
                role=memory.get("role"),
                parent_id=memory.get("parent_id"),
                metadata=memory.get("metadata", {}),
            )

        # Conversation
        if memory.role:
            conv_id = memory.parent_id
            if not conv_id:
                created = self._make_request("POST", "/v3/conversations", json_data={})
                conv = created["results"] if isinstance(created, dict) and "results" in created else created
                conv_id = conv.get("id") if isinstance(conv, dict) else None
                if not conv_id:
                    raise NebulaClientException("Failed to create conversation: no id returned")
            payload = {
                "messages": [
                    {"content": str(memory.content), "role": memory.role, "metadata": memory.metadata}
                ],
                "collection_id": memory.cluster_id,
            }
            _ = self._make_request("POST", f"/v3/conversations/{conv_id}/messages", json_data=payload)
            return str(conv_id)

        # Process text/json memory
        content_text = str(memory.content or "")
        content_hash = hashlib.sha256(content_text.encode("utf-8")).hexdigest()
        doc_metadata = dict(memory.metadata or {})
        doc_metadata["memory_type"] = "memory"
        doc_metadata["content_hash"] = content_hash
        data = {
            "metadata": json.dumps(doc_metadata),
            "ingestion_mode": "fast",
            "collection_ids": json.dumps([memory.cluster_id]),
            "raw_text": content_text,
        }

        url = f"{self.base_url}/v3/documents"
        headers = self._build_auth_headers(include_content_type=False)
        resp = self._client.post(url, data=data, headers=headers)
        if resp.status_code not in (200, 202):
            error_data = resp.json() if resp.content else {}
            raise NebulaException(error_data.get("message", f"Failed to create document: {resp.status_code}"), resp.status_code, error_data)
        resp_data = resp.json()
        if isinstance(resp_data, dict) and "results" in resp_data:
            if "document_id" in resp_data["results"]:
                return str(resp_data["results"]["document_id"])
            if "id" in resp_data["results"]:
                return str(resp_data["results"]["id"])
        return ""

    def store_memories(self, memories: List[Memory]) -> List[str]:
        """Store multiple memories.

        All items are processed identically to `store_memory`:
        - Conversations are grouped by conversation parent_id and sent in batches
        - Text/JSON memories are stored individually with consistent metadata generation

        Returns: list of parent_ids in the same order as input memories
        """
        # Group by conversation parent_id for batching
        results: List[str] = []
        conv_groups: Dict[str, List[Memory]] = {}
        others: List[Memory] = []

        for m in memories:
            if m.role:
                key = m.parent_id or f"__new__::{m.cluster_id}"
                conv_groups.setdefault(key, []).append(m)
            else:
                others.append(m)

        # Process conversation groups (batched) and others identically in terms of metadata generation
        for key, group in conv_groups.items():
            # Ensure conversation id
            cluster_id = group[0].cluster_id
            if key.startswith("__new__::"):
                created = self._make_request("POST", "/v3/conversations", json_data={})
                conv = created["results"] if isinstance(created, dict) and "results" in created else created
                conv_id = conv.get("id") if isinstance(conv, dict) else None
                if not conv_id:
                    raise NebulaClientException("Failed to create conversation: no id returned")
            else:
                conv_id = key

            messages = []
            for m in group:
                text = str(m.content or "")
                # mirror legacy store metadata handling for conversation messages
                msg_meta = dict(m.metadata or {})
                messages.append({"content": text, "role": m.role, "metadata": msg_meta})
            payload = {"messages": messages, "collection_id": cluster_id}
            _ = self._make_request("POST", f"/v3/conversations/{conv_id}/messages", json_data=payload)
            results.extend([str(conv_id)] * len(group))

        # Process others (text/json) individually with same metadata generation as store()
        for m in others:
            results.append(self.store_memory(m))
        return results
    
    def delete(self, memory_id: str) -> bool:
        """
        Delete a specific memory (document)
        
        Returns True if successful, raises exception otherwise.
        """
        try:
            self._make_request("DELETE", f"/v3/documents/{memory_id}")
            return True
        except Exception as e:
            raise
        
    def list_memories(
        self,
        *,
        cluster_ids: List[str],
        limit: int = 100,
        offset: int = 0,
    ) -> List[MemoryResponse]:
        """
        Get all memories from a specific cluster
        
        Args:
            cluster_ids: One or more cluster IDs to retrieve memories from
            limit: Maximum number of memories to return
            offset: Number of memories to skip
            
        Returns:
            List of MemoryResponse objects
        """
        # Cluster existence is validated by the backend when filtering by collection
        
        if not cluster_ids:
            raise NebulaClientException("cluster_ids must be provided to list_memories().")

        params = {
            "limit": limit,
            "offset": offset,
            "collection_ids": cluster_ids,
        }
        
        response = self._make_request("GET", "/v3/documents", params=params)
        
        if isinstance(response, dict) and "results" in response:
            documents = response["results"]
        elif isinstance(response, list):
            documents = response
        else:
            documents = [response]
        
        # Convert all documents to memories (handle text or chunks)
        memories: List[MemoryResponse] = []
        for doc in documents:
            content = doc.get("text") or doc.get("content")
            chunks = doc.get("chunks") if isinstance(doc.get("chunks"), list) else None
            memory_data = {
                "id": doc.get("id"),
                "content": content,
                "chunks": chunks,
                "metadata": doc.get("metadata", {}),
                # Prefer backend-provided collection_ids; fallback to the requested identifiers
                "collection_ids": doc.get("collection_ids", cluster_ids),
            }
            memories.append(MemoryResponse.from_dict(memory_data))
        
        return memories

    def get_memory(self, memory_id: str) -> MemoryResponse:
        """
        Get a specific memory by ID
        
        Args:
            memory_id: ID of the memory to retrieve
            
        Returns:
            MemoryResponse object
        """
        response = self._make_request("GET", f"/v3/documents/{memory_id}")
        
        # Handle either a single text or chunks array from the backend
        content = response.get("text") or response.get("content")
        chunks = response.get("chunks") if isinstance(response.get("chunks"), list) else None
        memory_data = {
            "id": response.get("id"),
            "content": content,
            "chunks": chunks,
            "metadata": response.get("metadata", {}),
            "collection_ids": response.get("collection_ids", []),
        }
        return MemoryResponse.from_dict(memory_data)
        
    def search(
        self,
        query: str,
        *,
        cluster_ids: List[str],
        limit: int = 10,
        retrieval_type: Union[RetrievalType, str] = RetrievalType.ADVANCED,
        filters: Optional[Dict[str, Any]] = None,
        search_settings: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """
        Search within a specific cluster
        
        Args:
            query: Search query string
            cluster_ids: One or more cluster IDs to search within
            limit: Maximum number of results to return
            retrieval_type: Type of retrieval strategy (simple, reasoning, planning)
            filters: Optional filters to apply to the search
            
        Returns:
            List of SearchResult objects
        """
        # Cluster existence is validated by the backend when applying collection filters
        
        # Convert string to enum if needed
        if isinstance(retrieval_type, str):
            retrieval_type = RetrievalType(retrieval_type)
        
        # Build effective search settings (allow caller overrides) with optimal defaults
        effective_settings: Dict[str, Any] = dict(search_settings or {})

        # Limit
        effective_settings["limit"] = limit

        # Graph-only evaluation: disable chunk retrieval paths by default
        effective_settings.setdefault("use_semantic_search", False)
        effective_settings.setdefault("use_fulltext_search", False)
        effective_settings.setdefault("use_hybrid_search", False)
        # Universal strategy: use rag_fusion by default for better recall/fusion
        effective_settings.setdefault("search_strategy", "rag_fusion")
        effective_settings.setdefault("num_sub_queries", 3)

        # Graph defaults (BFS on)
        gs = dict(effective_settings.get("graph_settings", {}) or {})
        gs.setdefault("enabled", True)
        gs.setdefault("bfs_enabled", True)
        gs.setdefault("bfs_max_depth", 2)
        effective_settings["graph_settings"] = gs

        # Optionally include retrieval_type for compatibility (server ignores it)
        if retrieval_type != RetrievalType.ADVANCED:
            effective_settings["retrieval_type"] = retrieval_type.value

        # Merge filters: caller-provided search_settings.filters first, then explicit filters arg
        user_filters: Dict[str, Any] = dict(effective_settings.get("filters", {}))
        if filters:
            user_filters.update(filters)

        if not cluster_ids:
            raise NebulaClientException("cluster_ids must be provided to search().")

        # Always add cluster filter using collection_ids only
        user_filters["collection_ids"] = {"$overlap": cluster_ids}

        effective_settings["filters"] = user_filters
        
        data = {
            "query": query,
            # Use custom mode and send explicit search_settings
            "search_mode": "custom",
            "search_settings": effective_settings,
        }
        
        response = self._make_request("POST", "/v3/retrieval/search", json_data=data)

        # Extract aggregated results from the response
        if isinstance(response, dict) and "results" in response:
            agg = response["results"]
            chunk_results = agg.get("chunk_search_results", [])
            graph_results = agg.get("graph_search_results", [])
        else:
            chunk_results = []
            graph_results = []

        out: List[SearchResult] = []
        # 1) Vector chunk results
        out.extend(SearchResult.from_dict(result) for result in chunk_results)

        # 2) Graph results mapped to unified SearchResult with typed graph payloads (no legacy fallback)
        for g in graph_results:
            out.append(SearchResult.from_graph_dict(g))

        return out
    
    # def chat(
    #     self,
    #     agent_id: str,
    #     message: str,
    #     conversation_id: Optional[str] = None,
    #     model: str = "gpt-4",
    #     temperature: float = 0.7,
    #     max_tokens: Optional[int] = None,
    #     retrieval_type: Union[RetrievalType, str] = RetrievalType.SIMPLE,
    #     cluster_id: Optional[str] = None,
    #     stream: bool = False,
    # ) -> AgentResponse:
    #     """
    #     Chat with an agent using its memories for context
    #     
    #     Args:
    #         agent_id: Unique identifier for the agent
    #         message: User message to send to the agent
    #         conversation_id: Optional conversation ID for multi-turn conversations
    #         model: LLM model to use for generation
    #         temperature: Sampling temperature for generation
    #         max_tokens: Maximum tokens to generate
    #         retrieval_type: Type of retrieval to use for context
    #         cluster_id: Optional cluster ID to search within
    #         stream: Whether to enable streaming response
    #         
    #     Returns:
    #         AgentResponse object with the agent's response
    #     """
    #     # Convert string to enum if needed
    #     if isinstance(retrieval_type, str):
    #         retrieval_type = RetrievalType(retrieval_type)
    #     
    #     data = {
    #         "query": message,
    #         "rag_generation_config": {
    #             "model": model,
    #             "temperature": temperature,
    #             "stream": stream,
    #         }
    #     }
    #     
    #     if max_tokens:
    #         data["rag_generation_config"]["max_tokens"] = max_tokens
    #     
    #     if conversation_id:
    #         data["conversation_id"] = conversation_id
    #     
    #     # Note: Skipping collection_id filter for now due to API issue
    #     
    #     if stream:
    #         # For streaming, we need to handle the response differently
    #         return self._make_streaming_generator("POST", "/v3/retrieval/rag", json_data=data, agent_id=agent_id, conversation_id=conversation_id)
    #     else:
    #         response = self._make_request("POST", "/v3/retrieval/rag", json_data=data)
    #     
    #     # Extract the response from the API format
    #     if isinstance(response, dict) and "results" in response:
    #         # The RAG endpoint returns the answer in "generated_answer" field
    #         generated_answer = response["results"].get("generated_answer", "")
    #         if generated_answer:
    #                 return AgentResponse(
    #                     content=generated_answer,
    #                     agent_id=agent_id,
    #                     conversation_id=conversation_id,
    #                     metadata={},
    #                     citations=[]
    #                 )
    #         
    #         # Fallback to completion format if generated_answer is not available
    #         completion = response["results"].get("completion", {})
    #         if completion and "choices" in completion:
    #             content = completion["choices"][0].get("message", {}).get("content", "")
    #             return AgentResponse(
    #                 content=content,
    #                 agent_id=agent_id,
    #                 conversation_id=conversation_id,
    #                 metadata={},
    #                 citations=[]
    #             )
    #     
    #     # Fallback
    #     return AgentResponse(
    #         content="No response received",
    #         agent_id=agent_id,
    #         conversation_id=conversation_id,
    #         metadata={},
    #         citations=[]
    #     )
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check the health of the Nebula API
        
        Returns:
            Health status information
        """
        return self._make_request("GET", "/health") 
