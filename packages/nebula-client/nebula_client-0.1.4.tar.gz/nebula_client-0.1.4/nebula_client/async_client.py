"""
Async client for the Nebula Client SDK
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
from .models import (
    MemoryResponse,
    Memory,
    Cluster,
    SearchResult,
    RetrievalType,
)


class AsyncNebulaClient:
    """
    Async client for interacting with Nebula Cloud API
    
    Mirrors the public API of `NebulaClient`, implemented using httpx.AsyncClient.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.nebulacloud.app",
        timeout: float = 30.0,
    ):
        """
        Initialize the async Nebula client
        
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
        self._client = httpx.AsyncClient(timeout=timeout)
        # Lazily initialized tokenizer encoder for token counting
        self._token_encoder = None  # type: ignore[var-annotated]
    
    async def __aenter__(self) -> "AsyncNebulaClient":
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.aclose()
    
    async def aclose(self) -> None:
        """Close the underlying async HTTP client"""
        await self._client.aclose()
    
    # Compatibility alias
    async def close(self) -> None:
        await self.aclose()
    
    def _is_nebula_api_key(self, token: Optional[str] = None) -> bool:
        """Detect if a token looks like a Nebula API key (public.raw)."""
        candidate = token or self.api_key
        if not candidate:
            return False
        if candidate.count(".") != 1:
            return False
        public_part, raw_part = candidate.split(".", 1)
        return public_part.startswith("key_") and len(raw_part) > 0
    
    def _build_auth_headers(self, include_content_type: bool = True) -> Dict[str, str]:
        """Build authentication headers.
        
        - If the provided credential looks like a Nebula API key, send it via X-API-Key
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
    
    async def _make_request_async(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make an async HTTP request to the Nebula API
        
        Returns response JSON on 200, maps error codes to SDK exceptions.
        """
        url = urljoin(self.base_url, endpoint)
        headers = self._build_auth_headers(include_content_type=True)
        
        try:
            response = await self._client.request(
                method=method,
                url=url,
                headers=headers,
                json=json_data,
                params=params,
            )
            
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
                    error_data.get("details"),
                )
            else:
                error_data = response.json() if response.content else {}
                raise NebulaException(
                    error_data.get("message", f"API error: {response.status_code}"),
                    response.status_code,
                    error_data,
                )
        except httpx.ConnectError as e:
            raise NebulaClientException(
                f"Failed to connect to {self.base_url}. Check your internet connection.",
                e,
            )
        except httpx.TimeoutException as e:
            raise NebulaClientException(
                f"Request timed out after {self.timeout} seconds",
                e,
            )
        except httpx.RequestError as e:
            raise NebulaClientException(f"Request failed: {str(e)}", e)
    
    # Cluster Management Methods
    
    async def create_cluster(
        self,
        name: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Cluster:
        data = {"name": name}
        if description:
            data["description"] = description
        if metadata:
            data["metadata"] = metadata
        
        response = await self._make_request_async("POST", "/v3/collections", json_data=data)
        if isinstance(response, dict) and "results" in response:
            response = response["results"]
        return Cluster.from_dict(response)
    
    async def get_cluster(self, cluster_id: str) -> Cluster:
        response = await self._make_request_async("GET", f"/v3/collections/{cluster_id}")
        if isinstance(response, dict) and "results" in response:
            response = response["results"]
        return Cluster.from_dict(response)
    
    async def get_cluster_by_name(self, name: str) -> Cluster:
        response = await self._make_request_async("GET", f"/v3/collections/name/{name}")
        if isinstance(response, dict) and "results" in response:
            response = response["results"]
        return Cluster.from_dict(response)
    
    async def list_clusters(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Cluster]:
        params = {"limit": limit, "offset": offset}
        response = await self._make_request_async("GET", "/v3/collections", params=params)
        if isinstance(response, dict) and "results" in response:
            clusters: List[Dict[str, Any]] = response["results"]
        elif isinstance(response, list):
            clusters = response
        else:
            clusters = [response]
        return [Cluster.from_dict(cluster) for cluster in clusters]
    
    async def update_cluster(
        self,
        cluster_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Cluster:
        data: Dict[str, Any] = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if metadata is not None:
            data["metadata"] = metadata
        response = await self._make_request_async("POST", f"/v3/collections/{cluster_id}", json_data=data)
        if isinstance(response, dict) and "results" in response:
            response = response["results"]
        return Cluster.from_dict(response)
    
    async def delete_cluster(self, cluster_id: str) -> bool:
        await self._make_request_async("DELETE", f"/v3/collections/{cluster_id}")
        return True
    
    # Unified write APIs (mirror sync client)
    
    async def store_memory(self, memory: Union[Memory, Dict[str, Any]] = None, **kwargs) -> str:
        """Store a single memory.

        Accepts either a `Memory` object or equivalent keyword arguments:
        - cluster_id: str
        - content: str
        - role: Optional[str]
        - parent_id: Optional[str]
        - metadata: Optional[dict]

        Returns: parent_id (conversation_id for conversations; document_id for text/json)
        """
        if memory is None:
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

        # Conversation message path
        if memory.role:
            conv_id = memory.parent_id
            if not conv_id:
                created = await self._make_request_async("POST", "/v3/conversations", json_data={})
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
            _ = await self._make_request_async("POST", f"/v3/conversations/{conv_id}/messages", json_data=payload)
            return str(conv_id)

        # Text/JSON document path
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
        response = await self._client.post(url, data=data, headers=headers)
        if response.status_code not in (200, 202):
            error_data = response.json() if response.content else {}
            raise NebulaException(
                error_data.get("message", f"Failed to create document: {response.status_code}"),
                response.status_code,
                error_data,
            )
        response_data = response.json()
        if isinstance(response_data, dict) and "results" in response_data:
            if "document_id" in response_data["results"]:
                return str(response_data["results"]["document_id"])
            if "id" in response_data["results"]:
                return str(response_data["results"]["id"])
        return ""

    async def store_memories(self, memories: List[Memory]) -> List[str]:
        """Store multiple memories.

        - Conversations are grouped by conversation parent_id and sent in batches
        - Text/JSON memories are stored individually with consistent metadata generation

        Returns: list of parent_ids in the same order as input memories
        """
        results: List[str] = []
        conv_groups: Dict[str, List[Memory]] = {}
        others: List[Memory] = []

        for m in memories:
            if m.role:
                key = m.parent_id or f"__new__::{m.cluster_id}"
                conv_groups.setdefault(key, []).append(m)
            else:
                others.append(m)

        # Process conversation groups
        for key, group in conv_groups.items():
            cluster_id = group[0].cluster_id
            if key.startswith("__new__::"):
                created = await self._make_request_async("POST", "/v3/conversations", json_data={})
                conv = created["results"] if isinstance(created, dict) and "results" in created else created
                conv_id = conv.get("id") if isinstance(conv, dict) else None
                if not conv_id:
                    raise NebulaClientException("Failed to create conversation: no id returned")
            else:
                conv_id = key

            messages = []
            for m in group:
                text = str(m.content or "")
                msg_meta = dict(m.metadata or {})
                messages.append({"content": text, "role": m.role, "metadata": msg_meta})
            payload = {"messages": messages, "collection_id": cluster_id}
            _ = await self._make_request_async("POST", f"/v3/conversations/{conv_id}/messages", json_data=payload)
            results.extend([str(conv_id)] * len(group))

        # Process text/json memories individually
        for m in others:
            results.append(await self.store_memory(m))
        return results
    
    async def delete(self, memory_id: str) -> bool:
        await self._make_request_async("DELETE", f"/v3/documents/{memory_id}")
        return True
    
    async def list_memories(
        self,
        *,
        cluster_ids: List[str],
        limit: int = 100,
        offset: int = 0,
    ) -> List[MemoryResponse]:
        if not cluster_ids:
            raise NebulaClientException("cluster_ids must be provided to list_memories().")
        params = {"limit": limit, "offset": offset, "collection_ids": cluster_ids}
        response = await self._make_request_async("GET", "/v3/documents", params=params)
        if isinstance(response, dict) and "results" in response:
            documents = response["results"]
        elif isinstance(response, list):
            documents = response
        else:
            documents = [response]
        memories: List[MemoryResponse] = []
        for doc in documents:
            # Let the model map fields appropriately
            memories.append(MemoryResponse.from_dict(doc))
        return memories
    
    async def get_memory(self, memory_id: str) -> MemoryResponse:
        response = await self._make_request_async("GET", f"/v3/documents/{memory_id}")
        return MemoryResponse.from_dict(response)
    
    async def search(
        self,
        query: str,
        *,
        cluster_ids: List[str],
        limit: int = 10,
        retrieval_type: Union[RetrievalType, str] = RetrievalType.ADVANCED,
        filters: Optional[Dict[str, Any]] = None,
        search_settings: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        if isinstance(retrieval_type, str):
            retrieval_type = RetrievalType(retrieval_type)
        effective_settings: Dict[str, Any] = dict(search_settings or {})
        effective_settings["limit"] = limit
        effective_settings.setdefault("use_semantic_search", True)
        effective_settings.setdefault("use_fulltext_search", True)
        effective_settings.setdefault("use_hybrid_search", True)
        # Universal strategy: use rag_fusion by default for better recall/fusion
        effective_settings.setdefault("search_strategy", "rag_fusion")
        effective_settings.setdefault("num_sub_queries", 3)
        gs = dict(effective_settings.get("graph_settings", {}) or {})
        gs.setdefault("enabled", True)
        gs.setdefault("bfs_enabled", True)
        gs.setdefault("bfs_max_depth", 2)
        effective_settings["graph_settings"] = gs
        if retrieval_type != RetrievalType.ADVANCED:
            effective_settings["retrieval_type"] = retrieval_type.value
        user_filters: Dict[str, Any] = dict(effective_settings.get("filters", {}))
        if filters:
            user_filters.update(filters)
        if not cluster_ids:
            raise NebulaClientException("cluster_ids must be provided to search().")
        user_filters["collection_ids"] = {"$overlap": cluster_ids}
        effective_settings["filters"] = user_filters
        data = {
            "query": query,
            "search_mode": "custom",
            "search_settings": effective_settings,
        }
        response = await self._make_request_async("POST", "/v3/retrieval/search", json_data=data)
        if isinstance(response, dict) and "results" in response:
            agg = response["results"]
            chunk_results = agg.get("chunk_search_results", [])
            graph_results = agg.get("graph_search_results", [])
        else:
            chunk_results = []
            graph_results = []
        out: List[SearchResult] = []
        out.extend(SearchResult.from_dict(result) for result in chunk_results)
        for g in graph_results:
            out.append(SearchResult.from_graph_dict(g))
        return out
    
    async def health_check(self) -> Dict[str, Any]:
        return await self._make_request_async("GET", "/health")