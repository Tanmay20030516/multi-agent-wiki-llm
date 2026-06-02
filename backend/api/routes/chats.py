"""
api/routes/chats.py

CRUD endpoints for chat threads (SQLite-backed).

GET    /api/chats             — list all threads (newest first)
POST   /api/chats             — create a new thread
GET    /api/chats/{id}        — get thread + messages
PATCH  /api/chats/{id}        — update title
DELETE /api/chats/{id}        — delete thread
PUT    /api/chats/{id}/messages — replace all messages (sync after response)
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.core import chat_store
from backend.core.logger import get_logger

log = get_logger(__name__)
router = APIRouter(prefix="/api/chats", tags=["chats"])


class CreateThreadRequest(BaseModel):
    id: str
    title: str = "New thread"


class PatchThreadRequest(BaseModel):
    title: str


class ReplaceMessagesRequest(BaseModel):
    messages: list[dict]


@router.get("")
async def list_threads():
    return await chat_store.list_threads()


@router.post("", status_code=201)
async def create_thread(body: CreateThreadRequest):
    return await chat_store.create_thread(body.id, body.title)


@router.get("/{thread_id}")
async def get_thread(thread_id: str):
    thread = await chat_store.get_thread(thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    return thread


@router.patch("/{thread_id}")
async def patch_thread(thread_id: str, body: PatchThreadRequest):
    ok = await chat_store.update_thread_title(thread_id, body.title)
    if not ok:
        raise HTTPException(status_code=404, detail="Thread not found")
    return {"ok": True}


@router.delete("/{thread_id}", status_code=204)
async def delete_thread(thread_id: str):
    ok = await chat_store.delete_thread(thread_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Thread not found")


@router.put("/{thread_id}/messages")
async def replace_messages(thread_id: str, body: ReplaceMessagesRequest):
    # create_thread uses INSERT OR IGNORE so it's safe to call unconditionally
    # — no check-then-act race condition.
    await chat_store.create_thread(thread_id)
    await chat_store.replace_messages(thread_id, body.messages)
    return {"ok": True}
