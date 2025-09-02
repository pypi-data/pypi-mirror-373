from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/cache/langcache")


class WarmupRequest(BaseModel):
    patterns: List[str]


def _get_langcache(request: Request):
    lc = getattr(request.app.state, "langcache", None)
    if lc is None:
        raise HTTPException(status_code=500, detail="LangCache not configured")
    return lc


@router.get("/stats")
async def langcache_stats(request: Request):
    lc = _get_langcache(request)
    s = lc.stats
    return {
        "status": "ok",
        "stats": {
            "hits": getattr(s, "hits", 0),
            "misses": getattr(s, "misses", 0),
            "evictions": getattr(s, "evictions", 0),
            "sets": getattr(s, "sets", 0),
            "size_bytes": getattr(s, "size_bytes", 0),
            "warmup_operations": getattr(s, "warmup_operations", 0),
            "hit_ratio": getattr(s, "hit_ratio", 0.0),
        },
    }


@router.post("/warmup")
async def langcache_warmup(request: Request, payload: WarmupRequest):
    lc = _get_langcache(request)
    await lc.warmup_cache(payload.patterns)
    return {"status": "ok"}


@router.get("/response")
async def langcache_response(request: Request, prompt: str):
    lc = _get_langcache(request)
    result = await lc.get_cached_response(prompt)
    return {"status": "ok", "result": result}


@router.get("/embedding")
async def langcache_embedding(request: Request, text: str):
    lc = _get_langcache(request)
    result = await lc.get_cached_embedding(text)
    return {"status": "ok", "result": result}
