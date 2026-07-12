from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from ..config import Config
from ..observability.logging import configure_logging
from ..observability.metrics import start_metrics_server
from .routes import router
from .websocket import ws_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    cfg = Config()
    configure_logging(cfg.log_level)
    start_metrics_server(9090)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Coding Agent API",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.include_router(router)
    app.include_router(ws_router)
    return app
