"""
api/websocket.py

WebSocket handler for streaming agent events to both UIs.

Protocol:
  Client -> Server (JSON):
    {"type": "query",    "question": "...", "history": [...]}
    {"type": "ingest",   "source_path": "...", "source_text": "..."}
    {"type": "lint"}
    {"type": "promote",  "question": "...", "answer": "...", "slug": "..."}
    {"type": "continue", "session_id": "...", "message": "..."}

  Server -> Client (JSON):
    {"type": "tool_call",      "iteration": N, "tool_name": "...", "tool_args": {...}}
    {"type": "tool_result",    "iteration": N, "tool_name": "...", "content": "..."}
    {"type": "llm_response",   "iteration": N, "content": "..."}
    {"type": "awaiting_input", "session_id": "...", "content": "..."}
    {"type": "done",           "content": "..."}
    {"type": "error",          "content": "..."}

Interactive flows (ingest, lint, promote):
  The agent pauses to present its plan. The "done" event carries the full
  message history. The server saves it, sends "awaiting_input" with a
  session_id, and waits. The client sends "continue" with that session_id
  and the user's response. The server resumes using continue_ingest/lint/promote.
"""

from __future__ import annotations

import uuid
import asyncio
from typing import Any, AsyncIterator

from fastapi import WebSocket, WebSocketDisconnect

from backend.agents.base_agent import AgentEvent
from backend.agents.query_agent import run_query
from backend.agents.maintenance_agent import (
    run_ingest,
    continue_ingest,
    run_lint,
    continue_lint,
    run_promote,
    continue_promote,
)
from backend.core.logger import get_logger

log = get_logger(__name__)

# In-memory session storage for interactive flows.
# Key: session_id -> {"messages": [...], "workflow": "ingest"|"lint"|"promote"}
_sessions: dict[str, dict[str, Any]] = {}

SESSION_TIMEOUT_SECS = 600  # 10 minutes


async def websocket_handler(ws: WebSocket) -> None:
    """
    Main WebSocket entry point. Registered in main.py.
    Loops receiving commands and streaming events for one client connection.
    """
    await ws.accept()
    log.info("WebSocket connected")

    try:
        while True:
            data = await ws.receive_json()
            msg_type = data.get("type", "")

            handler = _COMMAND_HANDLERS.get(msg_type)
            if handler:
                await handler(ws, data)
            else:
                await ws.send_json(
                    {
                        "type": "error",
                        "content": f"Unknown message type: '{msg_type}'",
                    }
                )

    except WebSocketDisconnect:
        log.info("WebSocket disconnected")
    except Exception as e:
        log.error("WebSocket error: %s", e, exc_info=True)
        try:
            await ws.send_json({"type": "error", "content": str(e)})
        except Exception:
            pass


# Command handlers
async def _handle_query(ws: WebSocket, data: dict[str, Any]) -> None:
    """Stream a query agent run. Non-interactive — runs to completion."""
    question = data.get("question", "")
    history = data.get("history")

    if not question:
        await ws.send_json({"type": "error", "content": "Missing 'question' field."})
        return

    async for event in run_query(question, conversation_history=history):
        await _send_event(ws, event)


async def _handle_ingest(ws: WebSocket, data: dict[str, Any]) -> None:
    """Start an ingest. Streams until agent pauses for confirmation."""
    source_path = data.get("source_path", "")
    source_text = data.get("source_text")

    if not source_path:
        await ws.send_json({"type": "error", "content": "Missing 'source_path' field."})
        return

    await _run_interactive(
        ws=ws,
        workflow="ingest",
        event_stream=run_ingest(source_path=source_path, source_text=source_text),
    )


async def _handle_lint(ws: WebSocket, data: dict[str, Any]) -> None:
    """Start a lint run. Interactive — agent presents report before fixing."""
    await _run_interactive(
        ws=ws,
        workflow="lint",
        event_stream=run_lint(),
    )


async def _handle_promote(ws: WebSocket, data: dict[str, Any]) -> None:
    """Start a promote workflow."""
    question = data.get("question", "")
    answer = data.get("answer", "")
    slug = data.get("slug")

    if not question or not answer:
        await ws.send_json(
            {
                "type": "error",
                "content": "Missing 'question' and/or 'answer' fields.",
            }
        )
        return

    await _run_interactive(
        ws=ws,
        workflow="promote",
        event_stream=run_promote(
            question=question,
            answer=answer,
            suggested_slug=slug,
        ),
    )


async def _handle_continue(ws: WebSocket, data: dict[str, Any]) -> None:
    """Resume a paused interactive workflow after user confirmation."""
    session_id = data.get("session_id", "")
    user_msg = data.get("message", "")

    session = _sessions.pop(session_id, None)
    if session is None:
        await ws.send_json(
            {
                "type": "error",
                "content": f"Session '{session_id}' not found or expired.",
            }
        )
        return

    if not user_msg:
        await ws.send_json({"type": "error", "content": "Missing 'message' field."})
        _sessions[session_id] = session  # restore — user can retry
        return

    workflow = session["workflow"]
    messages = session["messages"]

    continue_fn = _CONTINUE_FUNCTIONS.get(workflow)
    if not continue_fn:
        await ws.send_json(
            {"type": "error", "content": f"Unknown workflow: {workflow}"}
        )
        return

    # Continue might itself pause again (e.g. user says "change the slug")
    await _run_interactive(
        ws=ws,
        workflow=workflow,
        event_stream=continue_fn(messages=messages, user_response=user_msg),
    )


# Interactive flow runner
async def _run_interactive(
    ws: WebSocket,
    workflow: str,
    event_stream: AsyncIterator[AgentEvent],
) -> None:
    """
    Stream agent events to the client. Detect when the agent pauses
    (waiting for user input) vs. truly completes.

    Detection logic:
      The agent pauses when it finishes without having made any write
      tool calls — it read files and produced text (the plan/report)
      but didn't modify the wiki. In that case we save the conversation
      state and send "awaiting_input".

      The agent truly completes when it made write tool calls (wrote pages,
      updated index, appended log) — the operation is done.
    """
    made_writes = False
    done_event: AgentEvent | None = None

    async for event in event_stream:
        if event.type == "tool_call" and event.tool_name in (
            "write_file",
            "edit_file",
            "update_index",
            "append_log",
            "delete_file",
        ):
            made_writes = True

        if event.type == "done":
            done_event = event
        else:
            await _send_event(ws, event)

    if done_event is None:
        await ws.send_json(
            {"type": "error", "content": "Agent ended without done event."}
        )
        return

    # If no writes happened, the agent is pausing for user confirmation
    if not made_writes and workflow in ("ingest", "lint", "promote"):
        session_id = str(uuid.uuid4())[:8]

        if done_event.messages is None:
            await ws.send_json(
                {
                    "type": "error",
                    "content": "Internal error: agent did not return conversation state.",
                }
            )
            return

        _sessions[session_id] = {
            "workflow": workflow,
            "messages": done_event.messages,
        }
        asyncio.create_task(_expire_session(session_id))

        await ws.send_json(
            {
                "type": "awaiting_input",
                "session_id": session_id,
                "content": done_event.content,
            }
        )
    else:
        await ws.send_json(
            {
                "type": "done",
                "content": done_event.content,
            }
        )


# Session management
async def _expire_session(session_id: str) -> None:
    """Remove a session after timeout."""
    await asyncio.sleep(SESSION_TIMEOUT_SECS)
    removed = _sessions.pop(session_id, None)
    if removed:
        log.info("Session %s expired and removed", session_id)


# Event serialization
async def _send_event(ws: WebSocket, event: AgentEvent) -> None:
    """Serialize an AgentEvent and send it over the WebSocket."""
    payload: dict[str, Any] = {
        "type": event.type,
        "iteration": event.iteration,
    }
    if event.tool_name:
        payload["tool_name"] = event.tool_name
    if event.tool_args:
        payload["tool_args"] = event.tool_args
    if event.content:
        payload["content"] = event.content
    # Never send messages over the wire — they're internal state only

    await ws.send_json(payload)



# Dispatch tables
_COMMAND_HANDLERS = {
    "query": _handle_query,
    "ingest": _handle_ingest,
    "lint": _handle_lint,
    "promote": _handle_promote,
    "continue": _handle_continue,
}

_CONTINUE_FUNCTIONS = {
    "ingest": continue_ingest,
    "lint": continue_lint,
    "promote": continue_promote,
}
