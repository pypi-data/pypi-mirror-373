"""Legacy reasoning API endpoints for tests that import this module directly."""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

# Global variable used by tests via patch
reasoning_kernel = None  # Patched in unit tests


class StageResult(BaseModel):
    stage: str
    success: bool
    execution_time: float
    confidence: float
    result_data: Dict[str, Any] = Field(default_factory=dict)


class ReasoningRequest(BaseModel):
    vignette: str
    data: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None


class ReasoningResponse(BaseModel):
    session_id: str
    success: bool
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


async def get_redis_client_dependency():  # pragma: no cover - stub for tests to override
    class _Noop:
        async def keys(self, pattern: str):
            return []

        async def get(self, key: str):
            return None

    return _Noop()


@router.post("/api/v2/reasoning/analyze", response_model=ReasoningResponse)
async def analyze_scenario(req: ReasoningRequest):
    if reasoning_kernel is None:
        raise HTTPException(status_code=500, detail="Reasoning kernel not initialized")
    session_id = req.session_id or f"session_{int(time.time())}"
    try:
        result = await reasoning_kernel.reason(
            vignette=req.vignette, session_id=session_id, config=req.config or {}
        )
        # Map minimal fields used by tests
        return ReasoningResponse(
            session_id=session_id,
            success=bool(getattr(result, "success", True)),
            overall_confidence=float(getattr(result, "overall_confidence", 0.0)),
            total_execution_time=float(getattr(result, "total_execution_time", 0.0)),
            stages=[],
            error_message=None,
        )
    except Exception as exc:  # noqa: BLE001
        return ReasoningResponse(
            session_id=session_id,
            success=False,
            overall_confidence=0.0,
            total_execution_time=0.0,
            stages=[],
            error_message=str(exc),
        )


@router.get("/api/v2/reasoning/status/{session_id}", response_model=StatusResponse)
async def get_status(session_id: str):
    try:
        status = await reasoning_kernel.get_reasoning_status(session_id)  # type: ignore[attr-defined]
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
    try:
        ok = await reasoning_kernel.cancel_reasoning(session_id)  # type: ignore[attr-defined]
        if not ok:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"message": f"Session {session_id} cancelled successfully"}
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/api/v2/reasoning/history")
async def get_history(
    limit: int = 50, offset: int = 0, redis=Depends(get_redis_client_dependency)
):
    try:
        keys = await redis.keys("reasoning:result:*")
        sessions: List[Dict[str, Any]] = []
        for key in keys[offset : offset + max(0, min(limit, 1000))]:
            raw = await redis.get(key)
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
