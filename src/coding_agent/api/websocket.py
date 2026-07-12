from __future__ import annotations

import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..config import Config
from ..orchestrator import CodeOrchestrator
from ..schemas import GenerationRequest

ws_router = APIRouter()

_orchestrator = None


def get_orchestrator():
    global _orchestrator
    if _orchestrator is None:
        cfg = Config()
        _orchestrator = CodeOrchestrator(cfg)
    return _orchestrator


@ws_router.websocket("/ws/generate")
async def websocket_generate(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_text()
        request = GenerationRequest(**json.loads(data))
        orchestrator = get_orchestrator()
        async for update in orchestrator.generate_code_streaming(request):
            await websocket.send_text(json.dumps(update))
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_text(json.dumps({"error": str(e)}))
