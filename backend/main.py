"""
main.py

FastAPI application entry point.
Registers all HTTP routes and the WebSocket endpoint.

Run locally (from project root):
    uvicorn backend.main:app --reload --reload-dir backend --host 0.0.0.0 --port 8000

Run via Docker:
    docker compose up
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from backend.api import websocket
from backend.api.routes import wiki
from backend.api.routes import ingest, lint, query, sources, chats
from backend.core.config import settings
from backend.core.wiki_manager import wm
from backend.core.logger import get_logger

log = get_logger(__name__)


# Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Startup and shutdown logic.
    Runs before the first request and after the last.
    """
    # Startup
    log.info("Starting LLM Wiki backend")
    log.info("Data path: %s", settings.data_path)
    log.info("Maintenance model: %s", settings.maintenance_model)
    log.info("Query model: %s", settings.query_model)

    # Ensure wiki directories exist
    wm.ensure_dirs()

    if wm.is_initialised():
        counts = wm.page_count()
        log.info("Wiki initialised — %d pages total", counts["total"])
    else:
        log.warning("Wiki not fully initialised. Run: python scripts/init_wiki.py")

    yield

    # Shutdown
    log.info("LLM Wiki backend shutting down")


# App
app = FastAPI(
    title="LLM Wiki",
    description="AI/ML research knowledge base powered by LLM agents",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow both frontends to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # chat-ui
        "http://localhost:3001",  # admin-ui
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all HTTP routes
app.include_router(query.router)
app.include_router(ingest.router)
app.include_router(lint.router)
app.include_router(wiki.router)
app.include_router(sources.router)
app.include_router(chats.router)


# WebSocket endpoint — used by both UIs for streaming
@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket) -> None:
    await websocket.websocket_handler(ws)


@app.websocket("/ws/maintenance")
async def ws_maintenance(ws: WebSocket) -> None:
    await websocket.websocket_handler(ws)


@app.websocket("/ws/query")
async def ws_query(ws: WebSocket) -> None:
    await websocket.websocket_handler(ws)


# Health check
@app.get("/health")
async def health() -> dict:
    counts = wm.page_count() if wm.is_initialised() else {}
    return {
        "status": "ok",
        "wiki_initialised": wm.is_initialised(),
        "page_counts": counts,
    }
