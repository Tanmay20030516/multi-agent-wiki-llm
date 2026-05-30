"""
agents/base_agent.py

The agentic tool-calling loop. The single most important file in the project.

Every agent operation — query, ingest, lint, promote — runs through this loop.
It is intentionally generic: send messages to the LLM, execute any tool calls
that come back, feed the results in, repeat until the LLM is done or we hit
the iteration cap.

The loop:
  1. Send messages + tools to the LLM
  2. Get back an LLMResponse
  3. If response has tool_calls -> execute each one via registry.execute()
     -> append the assistant turn (with tool calls) to message history
     -> append each tool result to message history
     -> go to 1
  4. If response is final (no tool calls) -> return the text
  5. If iteration cap is hit -> return whatever we have + a warning

query_agent.py and maintenance_agent.py are thin wrappers that configure
this loop with the right system prompt, tool set, and LLM client.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, AsyncIterator

from backend.core.config import settings
from backend.core.logger import get_logger
from backend.llm.base_client import (
    LLMClient,
    LLMResponse,
    assistant_message,
    tool_result_message,
)
from backend.tools.registry import execute as execute_tool

log = get_logger(__name__)


# Progress events
@dataclass
class AgentEvent:
    """
    A progress event emitted during the agent loop.
    The WebSocket handler streams these to the UI for live updates.
    """

    type: str  # "tool_call" | "tool_result" | "llm_response" | "error" | "done"
    iteration: int  # which loop iteration produced this
    tool_name: str = ""
    tool_args: dict[str, Any] = field(default_factory=dict)
    content: str = ""  # tool result text, LLM text, or error message
    messages: list[dict[str, Any]] | None = field(
        default=None,
        repr=False,
    )  # attached to "done" events — the full conversation state for session resumption


# Agent loop
async def run_agent_loop(
    client: LLMClient,
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]],
    max_iterations: int | None = None,
) -> AsyncIterator[AgentEvent]:
    """
    Run the agentic tool-calling loop until the LLM stops or we hit the cap.

    This is an async generator — it yields AgentEvent objects as the loop
    progresses. The caller can stream these to a WebSocket for live UI
    updates, or collect them into a list for batch processing.

    Args:
        client:          An LLMClient (GeminiClient or GroqClient).
        messages:        Initial message list. Must include a system message
                         and at least one user message.
        tools:           Tool schema list from the registry.
        max_iterations:  Override the default cap from settings.

    Yields:
        AgentEvent objects for each tool call, tool result, LLM response,
        and the final "done" event.

    Usage:
        async for event in run_agent_loop(client, messages, tools):
            if event.type == "done":
                final_answer = event.content
            elif event.type == "tool_call":
                # show "Reading attention-mechanism.md..." in UI
            ...
    """
    cap = max_iterations or settings.max_agent_iterations
    iteration = 0

    while iteration < cap:
        iteration += 1
        log.info("Agent loop — iteration %d/%d", iteration, cap)

        # Call the LLM
        response: LLMResponse = await client.chat(
            messages=messages,
            tools=tools,
        )

        # Handle errors
        if response.stop_reason == "error":
            log.error("Agent loop — LLM error: %s", response.text)
            yield AgentEvent(
                type="error",
                iteration=iteration,
                content=response.text,
            )
            return

        # No tool calls -> final answer
        if response.is_final:
            log.info("Agent loop — complete at iteration %d", iteration)
            # Record the final assistant turn in the conversation
            messages.append(assistant_message(response.text))
            yield AgentEvent(
                type="llm_response",
                iteration=iteration,
                content=response.text,
            )
            yield AgentEvent(
                type="done",
                iteration=iteration,
                content=response.text,
                messages=messages,
            )
            return

        # Tool calls -> execute each one
        # First, append the assistant message (with tool calls) to history
        messages.append(assistant_message(response.text, response.tool_calls))

        # If the LLM also produced text alongside tool calls, emit it
        if response.text.strip():
            yield AgentEvent(
                type="llm_response",
                iteration=iteration,
                content=response.text,
            )

        # Execute each tool call and append results
        for tc in response.tool_calls:
            log.info("Tool call: %s(%s)", tc.name, _summarise_args(tc.arguments))

            yield AgentEvent(
                type="tool_call",
                iteration=iteration,
                tool_name=tc.name,
                tool_args=tc.arguments,
            )

            # Execute the tool
            result = execute_tool(tc.name, tc.arguments)

            # Append the tool result to the conversation
            messages.append(tool_result_message(tc.id, result))

            yield AgentEvent(
                type="tool_result",
                iteration=iteration,
                tool_name=tc.name,
                content=_truncate(result, 500),
            )

    # Hit the iteration cap
    log.warning("Agent loop — hit iteration cap (%d)", cap)
    yield AgentEvent(
        type="error",
        iteration=iteration,
        content=(
            f"Agent loop reached the maximum of {cap} iterations without "
            f"completing. The last response may be incomplete."
        ),
    )
    # Still emit done so the caller knows the loop ended
    yield AgentEvent(
        type="done",
        iteration=iteration,
        content=response.text if response else "", # type: ignore
        messages=messages,
    )


# Helpers
def _summarise_args(args: dict[str, Any], max_len: int = 80) -> str:
    """Short string summary of tool arguments for logging."""
    if not args:
        return ""
    pairs = ", ".join(f"{k}={repr(v)[:40]}" for k, v in args.items())
    return pairs[:max_len]


def _truncate(text: str, limit: int) -> str:
    """Truncate long tool results for event streaming (UI doesn't need full content)."""
    if len(text) <= limit:
        return text
    return text[:limit] + f"... ({len(text)} chars total)"
