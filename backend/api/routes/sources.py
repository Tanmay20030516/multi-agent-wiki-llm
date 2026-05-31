"""
api/routes/sources.py

GET   /api/sources/list  — List raw source files
POST  /api/promote       — Promote a query result to an analysis page (single-shot)
POST  /api/promote/confirm — (legacy) Confirm a two-step promote session
"""

from __future__ import annotations

import re
import uuid
import asyncio

from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

from backend.agents.maintenance_agent import run_promote, continue_promote
from backend.core.wiki_manager import wm, RAW_SUBDIRS
from backend.core.logger import get_logger, append_activity

from backend.api.websocket import _sessions, _expire_session

log = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["sources"])


# ── Source listing ─────────────────────────────────────────────────────────────

class SourceEntry(BaseModel):
    path: str
    category: str
    filename: str
    size: int


class SourceListResponse(BaseModel):
    sources: list[SourceEntry]
    total: int


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


# ── Promote ────────────────────────────────────────────────────────────────────

class PromoteRequest(BaseModel):
    """
    Accepts both the chat-ui field names and the original API names so
    neither caller breaks.

    Chat-ui sends:   { title, content, source_question }
    Legacy API sends: { question, answer, slug }
    """
    # Chat-ui fields
    source_question: str | None = Field(default=None)
    content: str | None = Field(default=None)
    title: str | None = Field(default=None)
    # Legacy / API fields
    question: str | None = Field(default=None)
    answer: str | None = Field(default=None)
    slug: str | None = Field(default=None)

    @property
    def resolved_question(self) -> str:
        return (self.source_question or self.question or "").strip()

    @property
    def resolved_answer(self) -> str:
        return (self.content or self.answer or "").strip()

    @property
    def resolved_slug(self) -> str | None:
        if self.slug:
            return self.slug
        if self.title:
            return re.sub(r"[^a-z0-9]+", "-", self.title.lower()).strip("-")[:60]
        return None


class PromoteResultResponse(BaseModel):
    result: str
    iterations: int
    tool_calls_made: list[str]


@router.post("/promote", response_model=PromoteResultResponse)
async def promote(req: PromoteRequest) -> PromoteResultResponse:
    """
    Promote a query answer to a permanent analysis wiki page.

    Single-shot: the maintenance agent plans the page internally, then
    auto-confirms and executes the writes — no second round-trip required.
    Callers get back the agent's final summary and a list of tool calls made.
    """
    question = req.resolved_question
    answer = req.resolved_answer
    slug_hint = req.resolved_slug

    if not question or not answer:
        raise HTTPException(
            status_code=422,
            detail=(
                "Must supply either (source_question + content) "
                "or (question + answer)."
            ),
        )

    result = ""
    iterations = 0
    tools_used: list[str] = []
    saved_messages = None

    # Phase 1 — agent reads index, proposes the page structure, stops
    async for event in run_promote(
        question=question,
        answer=answer,
        suggested_slug=slug_hint,
    ):
        iterations = event.iteration
        if event.type == "tool_call":
            tools_used.append(event.tool_name)
        if event.type == "done":
            result = event.content
            saved_messages = event.messages

    # Phase 2 — auto-confirm so the agent executes without a second HTTP call
    if saved_messages is not None:
        async for event in continue_promote(
            messages=saved_messages,
            user_response="yes, proceed with all writes",
        ):
            iterations = event.iteration
            if event.type == "tool_call":
                tools_used.append(event.tool_name)
            if event.type == "done":
                result = event.content

    # Fallback log entry if the agent forgot to call append_log
    if "append_log" not in tools_used:
        append_activity(
            operation="query->promote",
            title=slug_hint or "analysis",
            summary=f"Promoted query answer to wiki. Question: {question[:120]}",
        )

    log.info("Promote complete — slug: %s, %d tool calls", slug_hint, len(tools_used))
    return PromoteResultResponse(
        result=result,
        iterations=iterations,
        tool_calls_made=tools_used,
    )


# ── Legacy confirm endpoint (kept for backwards compat / WebSocket flow) ───────

class PromoteConfirmRequest(BaseModel):
    session_id: str
    message: str = Field(default="yes")


class LegacyPromoteResultResponse(BaseModel):
    result: str
    iterations: int


@router.post("/promote/confirm", response_model=LegacyPromoteResultResponse)
async def promote_confirm(req: PromoteConfirmRequest) -> LegacyPromoteResultResponse:
    """(Legacy) Confirm and execute a two-step promote session."""
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

    return LegacyPromoteResultResponse(result=result, iterations=iterations)
