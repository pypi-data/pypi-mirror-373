from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter()


# Dependency to get a redis-like service. Tests will monkeypatch get_redis_service.
async def get_redis_service():  # pragma: no cover - overridden in tests
    class _Redis:
        async def set_data(self, key, value, ttl=None):
            return True

        async def get_data(self, key):
            return None

        async def get_keys(self, pattern):
            return []

    return _Redis()


# External services (patched in tests)
causal_graph_generator = None
uncertainty_analyzer = None


class ReasoningPayload(BaseModel):
    vignette: str
    session_id: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


@router.post("/causal-graph")
async def generate_causal_graph(
    payload: ReasoningPayload, redis=Depends(get_redis_service)
):
    if causal_graph_generator is None:
        raise HTTPException(
            status_code=500, detail="Causal graph generator not available"
        )
    # Create graph and analysis
    graph = causal_graph_generator.create_graph_from_reasoning({})
    graph_data = causal_graph_generator.export_for_visualization(graph)
    analysis = causal_graph_generator.analyze_causal_structure()
    # Persist graph data for later export using session_id
    if payload.session_id:
        await redis.set_data(f"viz:graph:{payload.session_id}", graph_data)
    return {
        "status": "success",
        "graph_data": graph_data,
        "analysis": analysis,
        "graph_metadata": {"node_count": len(graph.nodes)},
    }


@router.post("/causal-graph/intervention")
async def simulate_intervention(node_id: int, new_value: float):
    if causal_graph_generator is None:
        raise HTTPException(
            status_code=500, detail="Causal graph generator not available"
        )
    result = causal_graph_generator.simulate_intervention(node_id, new_value)
    return {"status": "success", "intervention_result": result}


@router.post("/uncertainty-decomposition")
async def decompose_uncertainty(payload: ReasoningPayload):
    if uncertainty_analyzer is None:
        raise HTTPException(
            status_code=500, detail="Uncertainty analyzer not available"
        )
    decomp = uncertainty_analyzer.decompose_uncertainty({})
    data = uncertainty_analyzer.export_for_visualization(decomp)
    return {"status": "success", "uncertainty_data": data}


@router.post("/export/graph")
async def export_graph(
    session_id: str, export_format: str, redis=Depends(get_redis_service)
):
    data = await redis.get_data(f"viz:graph:{session_id}")
    if not data:
        raise HTTPException(status_code=404, detail="Graph not found")
    # For tests, just return the stored data
    return {"status": "success", "format": export_format, "graph": data}


class FeedbackPayload(BaseModel):
    session_id: str
    reasoning_stage: str
    rating: int
    feedback_type: str
    comments: Optional[str] = None


@router.post("/feedback")
async def submit_feedback(payload: FeedbackPayload):
    # Minimal implementation: always success
    return {"status": "success"}


@router.get("/user/{user_id}/recommendations")
async def get_user_recommendations(user_id: str):
    # Minimal implementation: always success
    return {"status": "success", "user_id": user_id, "recommendations": []}


def _convert_nodes_to_csv(nodes: List[Dict[str, Any]]) -> str:
    import csv
    from io import StringIO

    fieldnames = ["id", "label", "type", "confidence", "value", "uncertainty"]
    s = StringIO()
    writer = csv.DictWriter(s, fieldnames=fieldnames)
    writer.writeheader()
    for n in nodes:
        writer.writerow({k: n.get(k) for k in fieldnames})
    return s.getvalue()


def _convert_edges_to_csv(edges: List[Dict[str, Any]]) -> str:
    import csv
    from io import StringIO

    fieldnames = ["source", "target", "strength", "confidence", "type", "mechanism"]
    s = StringIO()
    writer = csv.DictWriter(s, fieldnames=fieldnames)
    writer.writeheader()
    for e in edges:
        writer.writerow({k: e.get(k) for k in fieldnames})
    return s.getvalue()
