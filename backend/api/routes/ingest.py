"""
api/routes/ingest.py

POST /api/ingest          — Start ingesting a source (returns plan + session_id)
POST /api/ingest/confirm  — Confirm the plan and execute writes
POST /api/ingest/upload   — Upload a file to raw/ then start ingest

For live streaming, use the WebSocket endpoint instead.
These HTTP endpoints support the two-step interactive flow:
  1. POST /api/ingest -> agent reads source, returns plan + session_id
  2. POST /api/ingest/confirm -> agent executes the approved plan
"""

from __future__ import annotations

import uuid
import shutil

from pydantic import BaseModel, Field
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from backend.agents.maintenance_agent import run_ingest, continue_ingest
from backend.core.logger import get_logger
from backend.core.wiki_manager import wm

# Shared session store with websocket.py — import from there
from backend.api.websocket import _sessions, _expire_session
import asyncio

log = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["ingest"])


class IngestRequest(BaseModel):
    source_path: str = Field(..., description="Path relative to data/raw/")
    source_text: str | None = Field(
        default=None,
        description="If pasting directly, the full source text",
    )


class IngestPlanResponse(BaseModel):
    session_id: str
    plan: str
    iterations: int
    tool_calls_made: list[str]


class IngestConfirmRequest(BaseModel):
    session_id: str = Field(..., description="Session ID from the plan response")
    message: str = Field(
        default="yes",
        description="User confirmation or modification request",
    )


class IngestResultResponse(BaseModel):
    result: str
    iterations: int
    tool_calls_made: list[str]


@router.post("/ingest", response_model=IngestPlanResponse)
async def ingest(req: IngestRequest) -> IngestPlanResponse:
    """
    Start ingesting a source. Returns the agent's plan and a session_id.
    Call POST /api/ingest/confirm with the session_id to execute.
    """
    plan = ""
    iterations = 0
    tools_used: list[str] = []
    session_id: str | None = None

    async for event in run_ingest(
        source_path=req.source_path,
        source_text=req.source_text,
    ):
        iterations = event.iteration
        if event.type == "tool_call":
            tools_used.append(event.tool_name)
        if event.type == "done":
            plan = event.content
            if event.messages is not None:
                session_id = str(uuid.uuid4())[:8]
                _sessions[session_id] = {
                    "workflow": "ingest",
                    "messages": event.messages,
                }
                asyncio.create_task(_expire_session(session_id))

    if session_id is None:
        raise HTTPException(
            status_code=500,
            detail="Ingest did not produce a plan. Check server logs.",
        )

    return IngestPlanResponse(
        session_id=session_id,
        plan=plan,
        iterations=iterations,
        tool_calls_made=tools_used,
    )


@router.post("/ingest/confirm", response_model=IngestResultResponse)
async def ingest_confirm(req: IngestConfirmRequest) -> IngestResultResponse:
    """
    Confirm an ingest plan and execute the writes.
    Pass the session_id from the plan response and the user's message.
    """
    session = _sessions.pop(req.session_id, None)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found or expired.")

    result = ""
    iterations = 0
    tools_used: list[str] = []

    async for event in continue_ingest(
        messages=session["messages"],
        user_response=req.message,
    ):
        iterations = event.iteration
        if event.type == "tool_call":
            tools_used.append(event.tool_name)
        if event.type == "done":
            result = event.content

    return IngestResultResponse(
        result=result,
        iterations=iterations,
        tool_calls_made=tools_used,
    )


class IngestTextRequest(BaseModel):
    text: str = Field(..., description="Full source text")
    filename: str = Field(default="pasted-note.md", description="Filename for the source")


@router.post("/ingest/text")
async def ingest_text(req: IngestTextRequest) -> dict:
    """
    Save pasted text as a raw source file and return its path.
    Call POST /api/ingest or use WebSocket to start processing.
    """
    safe_name = req.filename.replace("/", "-").replace("..", "")
    if not safe_name:
        safe_name = "pasted-note.md"
    if not safe_name.endswith((".md", ".txt")):
        safe_name += ".md"

    dest_dir = wm.raw_root / "notes"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / safe_name
    dest_path.write_text(req.text, encoding="utf-8")

    relative_path = f"notes/{safe_name}"
    log.info("Saved pasted text: %s (%d chars)", relative_path, len(req.text))

    return {
        "path": relative_path,
        "size": len(req.text),
        "message": f"Saved to raw/{relative_path}. Call POST /api/ingest to process.",
    }


@router.post("/ingest/upload")
async def ingest_upload(
    file: UploadFile = File(...),
    category: str = Form(default="articles"),
) -> dict:
    """
    Upload a file to data/raw/{category}/ and return its path.
    Call POST /api/ingest with the returned path to start processing.
    """
    valid_categories = ("articles", "papers", "notes")
    if category not in valid_categories:
        raise HTTPException(
            status_code=400,
            detail=f"Category must be one of: {', '.join(valid_categories)}",
        )

    if not file.filename:
        raise HTTPException(status_code=400, detail="File must have a name.")

    dest_dir = wm.raw_root / category
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / file.filename

    with open(dest_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    relative_path = f"{category}/{file.filename}"
    log.info("Uploaded source: %s", relative_path)

    # Auto-extract text for PDFs so read_source() can serve them to the agent
    extracted_pages = 0
    if dest_path.suffix.lower() == ".pdf":
        txt_path = dest_path.with_suffix(".txt")
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(dest_path))
            pages = [page.extract_text() or "" for page in reader.pages]
            txt_path.write_text("\n\n".join(pages), encoding="utf-8")
            extracted_pages = len(pages)
            log.info("Extracted %d pages from %s → %s", extracted_pages, dest_path.name, txt_path.name)
        except Exception as e:
            log.warning("PDF text extraction failed for %s: %s", dest_path.name, e)

    return {
        "path": relative_path,
        "size": dest_path.stat().st_size,
        "extracted_pages": extracted_pages,
        "message": f"Uploaded to raw/{relative_path}. Call POST /api/ingest to process.",
    }
