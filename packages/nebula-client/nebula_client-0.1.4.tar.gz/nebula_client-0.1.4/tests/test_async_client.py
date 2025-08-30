import asyncio
import os
import sys
from typing import Any, Dict, List, Optional

import pytest

# Ensure the package root (sdk/nebula_client) is importable when running from py/
_THIS_DIR = os.path.dirname(__file__)
_PKG_ROOT = os.path.abspath(os.path.join(_THIS_DIR, ".."))
if _PKG_ROOT not in sys.path:
    sys.path.insert(0, _PKG_ROOT)

from nebula_client.async_client import AsyncNebulaClient
from nebula_client.models import Memory


class _DummyResponse:
    def __init__(self, status_code: int, payload: Dict[str, Any]):
        self.status_code = status_code
        self._payload = payload

    def json(self) -> Dict[str, Any]:
        return self._payload


class _DummyHttpClient:
    def __init__(self):
        self.posts: List[Dict[str, Any]] = []

    async def post(self, url: str, data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None):
        self.posts.append({"url": url, "data": data, "headers": headers})
        # Default successful create with document id
        return _DummyResponse(200, {"results": {"document_id": "doc_123"}})

    async def aclose(self) -> None:
        return None


def run(coro):
    return asyncio.run(coro)


def test_store_memory_conversation_creates_and_posts(monkeypatch):
    client = AsyncNebulaClient(api_key="key_public.raw", base_url="https://example.com")

    # Inject dummy HTTP client
    dummy = _DummyHttpClient()
    client._client = dummy  # type: ignore[attr-defined]

    # Track calls to _make_request_async
    calls: List[Dict[str, Any]] = []

    async def _fake_request(method: str, endpoint: str, json_data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None):
        calls.append({"method": method, "endpoint": endpoint, "json": json_data, "params": params})
        if endpoint == "/v3/conversations" and method == "POST":
            return {"results": {"id": "conv_abc"}}
        if endpoint.startswith("/v3/conversations/") and endpoint.endswith("/messages"):
            return {"ok": True}
        raise AssertionError(f"Unexpected call: {method} {endpoint}")

    client._make_request_async = _fake_request  # type: ignore[assignment]

    mem = Memory(cluster_id="cluster_1", content="hello", role="user", metadata={"x": 1})
    conv_id = run(client.store_memory(mem))

    assert conv_id == "conv_abc"
    # Ensure messages endpoint was hit once
    assert any(c["endpoint"].endswith("/messages") for c in calls)


def test_store_memory_text_document_posts(monkeypatch):
    client = AsyncNebulaClient(api_key="key_public.raw", base_url="https://example.com")
    dummy = _DummyHttpClient()
    client._client = dummy  # type: ignore[attr-defined]

    # No _make_request_async used in document path
    mem = Memory(cluster_id="cluster_1", content="some text", metadata={"foo": "bar"})
    doc_id = run(client.store_memory(mem))

    assert doc_id == "doc_123"
    # Verify it posted to documents endpoint
    assert any(p["url"].endswith("/v3/documents") for p in dummy.posts)


def test_store_memories_mixed_batch(monkeypatch):
    client = AsyncNebulaClient(api_key="key_public.raw", base_url="https://example.com")
    dummy = _DummyHttpClient()
    client._client = dummy  # type: ignore[attr-defined]

    calls: List[Dict[str, Any]] = []

    async def _fake_request(method: str, endpoint: str, json_data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None):
        calls.append({"method": method, "endpoint": endpoint, "json": json_data, "params": params})
        if endpoint == "/v3/conversations" and method == "POST":
            return {"results": {"id": "conv_new"}}
        if endpoint.startswith("/v3/conversations/") and endpoint.endswith("/messages"):
            return {"ok": True}
        raise AssertionError(f"Unexpected call: {method} {endpoint}")

    client._make_request_async = _fake_request  # type: ignore[assignment]

    memories = [
        Memory(cluster_id="c1", content="hi", role="user"),  # conversation (new)
        Memory(cluster_id="c1", content="there"),              # document
        Memory(cluster_id="c1", content="again", role="assistant", parent_id="conv_existing"),  # conversation (existing)
    ]

    results = run(client.store_memories(memories))

    # We expect 3 ids back containing both conversation ids and one document id
    assert len(results) == 3
    assert "conv_new" in results
    assert "conv_existing" in results
    assert any(r.startswith("doc_") or r == "doc_123" for r in results)
    # Messages endpoint should be called twice (two conversation groups)
    msg_calls = [c for c in calls if c["endpoint"].endswith("/messages")]
    assert len(msg_calls) == 2

