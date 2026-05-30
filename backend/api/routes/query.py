"""
api/routes/query.py

POST /api/query — Ask a question against the wiki.

For streaming responses, use the WebSocket endpoint instead.
This HTTP endpoint collects all agent events and returns the final
answer as a JSON response — simpler but no live progress.
"""

from __future__ import annotations

from pydantic import BaseModel, Field
from fastapi import APIRouter

from backend.agents.query_agent import run_query
from backend.core.logger import get_logger

log = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["query"])


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, description="The question to ask")
    conversation_history: list[dict] | None = Field(
        default=None,
        description="Optional prior turns for multi-turn conversations",
    )


class QueryResponse(BaseModel):
    answer: str
    iterations: int
    tool_calls_made: list[str]


@router.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest) -> QueryResponse:
    """
    Run the query agent and return the final answer.
    For live streaming, connect to the WebSocket at /ws and send
    {"type": "query", "question": "..."}.
    """
    answer = ""
    iterations = 0
    tools_used: list[str] = []

    async for event in run_query(
        question=req.question,
        conversation_history=req.conversation_history,
    ):
        iterations = event.iteration
        if event.type == "tool_call":
            tools_used.append(event.tool_name)
        if event.type == "done":
            answer = event.content

    return QueryResponse(
        answer=answer,
        iterations=iterations,
        tool_calls_made=tools_used,
    )
