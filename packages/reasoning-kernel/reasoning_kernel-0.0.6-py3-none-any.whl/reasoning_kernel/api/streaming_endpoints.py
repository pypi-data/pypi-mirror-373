from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..core import lifespan as lifespan_mod

router = APIRouter()


class StreamManager:
    async def send_stage_update(self, session_id: str, data: Dict[str, Any]):
        return None

    async def send_thinking_update(self, session_id: str, data: Dict[str, Any]):
        return None

    async def send_sandbox_update(self, session_id: str, data: Dict[str, Any]):
        return None


async def stream_reasoning_process(
    session_id: str, vignette: str, config: Dict[str, Any], manager: StreamManager
):
    kernel = getattr(lifespan_mod, "reasoning_kernel", None)
    if kernel is None:
        return

    async def on_stage_start(stage: str):
        await manager.send_stage_update(
            session_id, {"stage": stage, "status": "running"}
        )

    async def on_stage_complete(stage: str, result: Dict[str, Any]):
        await manager.send_stage_update(
            session_id, {"stage": stage, "status": "completed", **result}
        )

    async def on_thinking_sentence(sentence: str):
        await manager.send_thinking_update(session_id, {"sentence": sentence})

    async def on_sandbox_event(event: Dict[str, Any]):
        await manager.send_sandbox_update(session_id, event)

    res = await kernel.reason_with_streaming(
        vignette,
        session_id=session_id,
        config=config,
        on_stage_start=on_stage_start,
        on_stage_complete=on_stage_complete,
        on_thinking_sentence=on_thinking_sentence,
        on_sandbox_event=on_sandbox_event,
    )
    # Signal completion
    await manager.send_stage_update(
        session_id,
        {
            "stage": "complete",
            "status": "completed",
            "overall_confidence": getattr(res, "overall_confidence", 0.0),
        },
    )


@router.websocket("/api/v2/ws/reasoning/stream/{session_id}")
async def websocket_stream(ws: WebSocket, session_id: str):
    await ws.accept()

    class WSManager(StreamManager):
        async def send_stage_update(self, session_id: str, data: Dict[str, Any]):
            await ws.send_json({"type": "stage", **data})

        async def send_thinking_update(self, session_id: str, data: Dict[str, Any]):
            await ws.send_json({"type": "thinking", **data})

        async def send_sandbox_update(self, session_id: str, data: Dict[str, Any]):
            await ws.send_json({"type": "sandbox", **data})

    try:
        while True:
            msg = await ws.receive_json()
            if msg.get("type") == "ping":
                await ws.send_json({"type": "pong"})
            elif msg.get("type") == "start":
                vignette = msg.get("vignette", "")
                config = msg.get("config", {})
                await stream_reasoning_process(
                    session_id, vignette, config, WSManager()
                )
    except WebSocketDisconnect:
        return
