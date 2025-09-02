"""v1 API router used by unit tests (imports and patches).

Provides endpoints under /api/v2/reasoning/* and exposes get_orchestrator and
get_redis_client_dependency for tests to patch.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, cast

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


class ReasoningRequest(BaseModel):
    vignette: str
    data: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None


class StageResult(BaseModel):
    stage: str
    success: bool
    execution_time: float
    confidence: float
    result_data: Dict[str, Any] = Field(default_factory=dict)


class ReasoningResponse(BaseModel):
    success: bool
    session_id: str
    overall_confidence: float
    total_execution_time: float
    stages: List[StageResult] = Field(default_factory=list)
    error_message: Optional[str] = None


class StatusResponse(BaseModel):
    session_id: str
    status: str
    current_stage: Optional[str] = None
    progress_percentage: Optional[float] = None
    elapsed_time: Optional[float] = None
    estimated_remaining_time: Optional[float] = None


router = APIRouter()

# Share redis dependency with legacy module so test overrides apply consistently
try:  # pragma: no cover - simple aliasing
    from .. import reasoning_endpoints as _legacy_endpoints

    get_redis_client_dependency = _legacy_endpoints.get_redis_client_dependency  # type: ignore[attr-defined]
except Exception:  # pragma: no cover

    async def get_redis_client_dependency():  # fallback
        class _Noop:
            async def keys(self, pattern: str):
                return []

            async def get(self, key: str):
                return None

        return _Noop()


def get_orchestrator():  # pragma: no cover - overridden in tests
    return None


@router.post("/api/v2/reasoning/analyze", response_model=ReasoningResponse)
async def analyze_scenario(req: ReasoningRequest):
    orchestrator = cast(Any, get_orchestrator())
    if orchestrator is None:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")
    session_id = req.session_id or f"session_{int(time.time())}"
    try:
        result = await orchestrator.execute_reasoning(
            req.vignette, req.data or {}, req.config or {}, session_id
        )
        # The tests stub this to return a dict-like structure
        success = bool(result.get("success", True))
        rr = result.get("result")
        # Prefer nested attributes, then top-level fallbacks provided by tests
        overall_confidence = 0.0
        total_time = 0.0
        if rr is not None:
            overall_confidence = float(
                getattr(rr, "overall_confidence", getattr(rr, "confidence_score", 0.0))
            )
            total_time = float(
                getattr(rr, "total_execution_time", getattr(rr, "processing_time", 0.0))
            )
        # Top-level fallbacks
        if overall_confidence == 0.0:
            overall_confidence = float(result.get("confidence_score", 0.0))
        if total_time == 0.0:
            total_time = float(result.get("execution_time", 0.0))
        return ReasoningResponse(
            success=success,
            session_id=session_id,
            overall_confidence=overall_confidence,
            total_execution_time=total_time,
            stages=[],
            error_message=None,
        )
    except Exception as exc:  # noqa: BLE001
        return ReasoningResponse(
            success=False,
            session_id=session_id,
            overall_confidence=0.0,
            total_execution_time=0.0,
            stages=[],
            error_message=str(exc),
        )


# Define both with and without explicit session_id to avoid 405 for empty segment
@router.get("/api/v2/reasoning/status/{session_id}", response_model=StatusResponse)
@router.get("/api/v2/reasoning/status/", response_model=StatusResponse)
async def get_status(session_id: str | None = None):
    # Basic validation to avoid empty/invalid IDs, returning 405/500 is not desired in tests
    if (
        not session_id
        or len(session_id) > 256
        or any(c in session_id for c in [" ", "/", "\n"])
    ):
        raise HTTPException(status_code=422, detail="Invalid session id")
    orchestrator = cast(Any, get_orchestrator())
    if orchestrator is None:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")
    try:
        status = await orchestrator.get_status(session_id)
        if status.get("status") == "not_found":
            raise HTTPException(status_code=404, detail="Session not found")
        return StatusResponse(
            session_id=session_id,
            status=status.get("status", "unknown"),
            current_stage=status.get("current_stage"),
            progress_percentage=status.get("progress"),
            elapsed_time=status.get("elapsed_time"),
            estimated_remaining_time=status.get("estimated_remaining"),
        )
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc))


@router.delete("/api/v2/reasoning/{session_id}")
async def cancel_reasoning(session_id: str):
    orchestrator = cast(Any, get_orchestrator())
    if orchestrator is None:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")
    try:
        ok = await orchestrator.cancel_session(session_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"message": f"Session {session_id} cancelled successfully"}
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/api/v2/reasoning/history")
async def get_history(limit: int = 50, offset: int = 0):
    # Validate pagination parameters
    if limit < 0 or offset < 0:
        raise HTTPException(
            status_code=422, detail="limit and offset must be non-negative"
        )
    if limit > 10000:
        # Cap very large limits instead of failing
        limit = 10000
    try:
        # Dynamically resolve dependency so tests can patch the symbol
        import inspect

        provider = get_redis_client_dependency
        if inspect.iscoroutinefunction(provider):
            redis_client = await provider()  # type: ignore[misc]
        else:
            redis_client = provider()  # type: ignore[misc]

        from typing import Any as _Any

        redis_client = cast(_Any, redis_client)

        keys = await redis_client.keys("reasoning:result:*")
        sessions: List[Dict[str, Any]] = []
        # Slice keys safely
        end = offset + limit if limit > 0 else len(keys)
        for key in keys[offset:end]:
            raw = await redis_client.get(key)
            if not raw:
                continue
            import json

            try:
                payload = json.loads(raw)
            except Exception:
                payload = {}
            sessions.append({"session_id": key.split(":")[-1], **payload})
        return {"sessions": sessions, "total_count": len(keys)}
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc))
