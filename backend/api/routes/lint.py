"""
api/routes/lint.py

POST /api/lint          — Run wiki health check (returns report + session_id)
POST /api/lint/confirm  — Approve fixes from the lint report
"""

from __future__ import annotations

import uuid
import asyncio

from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

from backend.agents.maintenance_agent import run_lint, continue_lint
from backend.core.logger import get_logger, append_activity

from backend.api.websocket import _sessions, _expire_session

log = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["lint"])


class LintReportResponse(BaseModel):
    session_id: str
    report: str
    iterations: int
    tool_calls_made: list[str]


class LintConfirmRequest(BaseModel):
    session_id: str = Field(..., description="Session ID from the lint report")
    message: str = Field(
        ...,
        description="Which fixes to apply, e.g. 'fix all', 'fix errors only', 'fix #1 and #3'",
    )


class LintResultResponse(BaseModel):
    result: str
    iterations: int
    tool_calls_made: list[str]


@router.post("/lint", response_model=LintReportResponse)
async def lint() -> LintReportResponse:
    """
    Run a wiki health check. Returns the lint report and a session_id.
    Call POST /api/lint/confirm with approved fixes.
    """
    report = ""
    iterations = 0
    tools_used: list[str] = []
    session_id: str | None = None

    async for event in run_lint():
        iterations = event.iteration
        if event.type == "tool_call":
            tools_used.append(event.tool_name)
        if event.type == "done":
            report = event.content
            if event.messages is not None:
                session_id = str(uuid.uuid4())[:8]
                _sessions[session_id] = {
                    "workflow": "lint",
                    "messages": event.messages,
                }
                asyncio.create_task(_expire_session(session_id))

    if session_id is None:
        raise HTTPException(
            status_code=500,
            detail="Lint did not produce a report. Check server logs.",
        )

    return LintReportResponse(
        session_id=session_id,
        report=report,
        iterations=iterations,
        tool_calls_made=tools_used,
    )


@router.post("/lint/confirm", response_model=LintResultResponse)
async def lint_confirm(req: LintConfirmRequest) -> LintResultResponse:
    """Approve and apply fixes from a lint report."""
    session = _sessions.pop(req.session_id, None)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found or expired.")

    result = ""
    iterations = 0
    tools_used: list[str] = []

    async for event in continue_lint(
        messages=session["messages"],
        user_response=req.message,
    ):
        iterations = event.iteration
        if event.type == "tool_call":
            tools_used.append(event.tool_name)
        if event.type == "done":
            result = event.content

    # Fallback log entry if agent forgot to call append_log
    if "append_log" not in tools_used:
        from datetime import date
        append_activity(
            operation="lint",
            title=f"health-check-{date.today().isoformat()}",
            summary=f"Lint fixes applied ({len(tools_used)} tool calls). User approved fixes.",
        )

    return LintResultResponse(
        result=result,
        iterations=iterations,
        tool_calls_made=tools_used,
    )
