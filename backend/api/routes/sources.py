"""
api/routes/sources.py

GET   /api/sources/list  — List raw source files
POST  /api/promote       — Promote a query result to an analysis page
"""

from __future__ import annotations

import uuid
import asyncio

from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

from backend.agents.maintenance_agent import run_promote, continue_promote
from backend.core.wiki_manager import wm, RAW_SUBDIRS
from backend.core.logger import get_logger

from backend.api.websocket import _sessions, _expire_session

log = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["sources"])


class SourceEntry(BaseModel):
    path: str
    category: str
    filename: str
    size: int


class SourceListResponse(BaseModel):
    sources: list[SourceEntry]
    total: int


class PromoteRequest(BaseModel):
    question: str = Field(..., description="The original question")
    answer: str = Field(..., description="The answer text to promote")
    slug: str | None = Field(
        default=None, description="Suggested slug for the analysis page"
    )


class PromotePlanResponse(BaseModel):
    session_id: str
    plan: str


class PromoteConfirmRequest(BaseModel):
    session_id: str
    message: str = Field(default="yes")


class PromoteResultResponse(BaseModel):
    result: str
    iterations: int


@router.get("/sources/list", response_model=SourceListResponse)
async def list_sources() -> SourceListResponse:
    """List all raw source files across all categories."""
    entries: list[SourceEntry] = []

    for category in RAW_SUBDIRS:
        if category == "assets":
            continue  # skip assets — not ingestible sources
        for file_path in wm.list_raw_files(category):
            entries.append(
                SourceEntry(
                    path=str(file_path.relative_to(wm.raw_root)),
                    category=category,
                    filename=file_path.name,
                    size=file_path.stat().st_size,
                )
            )

    return SourceListResponse(sources=entries, total=len(entries))


@router.post("/promote", response_model=PromotePlanResponse)
async def promote(req: PromoteRequest) -> PromotePlanResponse:
    """
    Start promoting a query result to an analysis page.
    Returns the agent's plan and a session_id.
    Call POST /api/promote/confirm with the session_id to execute.
    """
    plan = ""
    session_id: str | None = None

    async for event in run_promote(
        question=req.question,
        answer=req.answer,
        suggested_slug=req.slug,
    ):
        if event.type == "done":
            plan = event.content
            if event.messages is not None:
                session_id = str(uuid.uuid4())[:8]
                _sessions[session_id] = {
                    "workflow": "promote",
                    "messages": event.messages,
                }
                asyncio.create_task(_expire_session(session_id))

    if session_id is None:
        raise HTTPException(
            status_code=500,
            detail="Promote did not produce a plan. Check server logs.",
        )

    return PromotePlanResponse(session_id=session_id, plan=plan)


@router.post("/promote/confirm", response_model=PromoteResultResponse)
async def promote_confirm(req: PromoteConfirmRequest) -> PromoteResultResponse:
    """Confirm and execute a promote operation."""
    session = _sessions.pop(req.session_id, None)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found or expired.")

    result = ""
    iterations = 0

    async for event in continue_promote(
        messages=session["messages"],
        user_response=req.message,
    ):
        iterations = event.iteration
        if event.type == "done":
            result = event.content

    return PromoteResultResponse(result=result, iterations=iterations)
