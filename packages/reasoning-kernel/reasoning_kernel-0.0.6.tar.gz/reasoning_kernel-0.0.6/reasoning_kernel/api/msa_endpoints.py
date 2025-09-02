from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class MSAReasonRequest(BaseModel):
    scenario: str
    config: Optional[Dict[str, Any]] = None


def get_msa_kernel():  # pragma: no cover - patched in tests
    class _Kernel:
        plugins = {}

        async def run_pipeline(
            self, scenario: str, config: Optional[Dict[str, Any]] = None
        ):
            return {
                "comprehension": {},
                "search_results": [],
                "dependency_graph": {},
                "numpyro_program": {},
                "status": "completed",
                "note": "mock pipeline",
            }

    return _Kernel()


@router.post("/api/v1/msa/reason")
async def run_msa_reasoning(req: MSAReasonRequest):
    kernel = get_msa_kernel()
    try:
        result = await kernel.run_pipeline(req.scenario, req.config)
        return result
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/api/v1/msa/health")
async def msa_health():
    try:
        kernel = get_msa_kernel()
        plugins = getattr(kernel, "plugins", {})
        return {
            "status": "healthy",
            "kernel_initialized": True,
            "plugins_available": list(plugins.keys())
            if isinstance(plugins, dict)
            else [],
        }
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"MSA health check failed: {exc}")
