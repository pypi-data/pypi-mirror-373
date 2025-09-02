"""
World model vector helpers for RedisStore.

Encapsulates embedding generation and upsert of world model vector records.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class WorldModelVectorRecord:
    id: str
    model_type: str
    state_data: str
    confidence: float
    context_keys: str
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    embedding: list[float] = field(default_factory=list)


async def upsert_world_model_vector(
    *,
    store: Any,
    collections: dict[str, Any],
    embedding_generator: Any,
    model_type: str,
    state_data: Dict[str, Any],
    confidence: float = 0.0,
    context_keys: Optional[list[str]] = None,
) -> str:
    """Generate embedding and upsert a world model vector record, returning its ID."""
    # Serialize
    state_str = json.dumps(state_data, sort_keys=True)
    context_keys_str = json.dumps(context_keys or [], sort_keys=True)

    # Generate embedding text
    combined_text = f"{model_type} {state_str}"
    embedding_list = await embedding_generator.generate_embeddings([combined_text])
    emb = embedding_list[0] if embedding_list else []

    # Build record
    import uuid

    record = WorldModelVectorRecord(
        id=str(uuid.uuid4()),
        model_type=model_type,
        state_data=state_str,
        confidence=confidence,
        context_keys=context_keys_str,
        embedding=emb,
    )

    # Upsert via collection
    from .redis_vectors import get_or_create_collection

    collection = await get_or_create_collection(
        store, collections, "world_models", WorldModelVectorRecord
    )
    await collection.upsert(record)

    return record.id


class RedisWorldModelService:
    """Thin adapter exposing world model APIs used by tests.

    Stores models as JSON by ID and supports versioning and simple searches.
    """

    def __init__(
        self,
        redis_client: Optional[Any] = None,
        namespace_prefix: str = "reasoning_kernel",
    ):
        if redis_client is None:
            try:
                from .redis_connection import get_redis_client as _factory

                redis_client = _factory()
            except Exception:
                redis_client = None
        self.redis = redis_client
        self.ns = namespace_prefix

    def _key(self, model_id: str) -> str:
        return f"{self.ns}:world_model:{model_id}"

    def _ver_key(self, model_id: str, version: int) -> str:
        return f"{self.ns}:world_model:{model_id}:v:{version}"

    async def store_world_model(self, model_id: str, model: Dict[str, Any]) -> bool:
        if self.redis is None:
            raise RuntimeError("Redis client not available")
        import json as _json

        return await self.redis.set(self._key(model_id), _json.dumps(model))

    async def get_world_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        if self.redis is None:
            raise RuntimeError("Redis client not available")
        import json as _json

        data = await self.redis.get(self._key(model_id))
        return _json.loads(data) if data else None

    async def store_world_model_version(
        self, model_id: str, version: int, model: Dict[str, Any]
    ) -> bool:
        if self.redis is None:
            raise RuntimeError("Redis client not available")
        import json as _json

        return await self.redis.set(
            self._ver_key(model_id, version), _json.dumps(model)
        )

    async def get_world_model_version(
        self, model_id: str, version: int
    ) -> Optional[Dict[str, Any]]:
        if self.redis is None:
            raise RuntimeError("Redis client not available")
        import json as _json

        data = await self.redis.get(self._ver_key(model_id, version))
        return _json.loads(data) if data else None

    async def get_latest_world_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        if self.redis is None:
            raise RuntimeError("Redis client not available")
        import json as _json
        import re as _re

        # Find highest version by scanning keys
        try:
            keys = await self.redis.keys(f"{self.ns}:world_model:{model_id}:v:*")
        except Exception:
            keys = []
        max_v = -1
        latest_key = None
        for k in keys:
            m = _re.search(r":v:(\d+)$", k)
            if m:
                v = int(m.group(1))
                if v > max_v:
                    max_v = v
                    latest_key = k
        if not latest_key:
            return None
        data = await self.redis.get(latest_key)
        return _json.loads(data) if data else None

    async def search_by_context(self, context: str) -> List[Dict[str, Any]]:
        if self.redis is None:
            raise RuntimeError("Redis client not available")
        import json as _json

        out: List[Dict[str, Any]] = []
        try:
            keys = await self.redis.keys(f"{self.ns}:world_model:*")
        except Exception:
            keys = []
        for k in keys:
            # skip version keys for context search; they may contain same data
            if ":v:" in k:
                continue
            data = await self.redis.get(k)
            if not data:
                continue
            obj = _json.loads(data)
            if obj.get("context") == context:
                out.append(obj)
        return out
