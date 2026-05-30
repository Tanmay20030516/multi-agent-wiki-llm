"""
llm/base_client.py

The LLM provider abstraction layer.

Defines two things:

1. Data models — ToolCall and LLMResponse normalise the output from
   every provider into one consistent shape. The agent loop works with
   these models and never touches provider-specific response objects.

2. LLMClient Protocol — the interface both GeminiClient and GroqClient
   implement. One method: chat(). Swap providers by swapping the client.
   The agent loop never knows which provider it is talking to.

Why a Protocol instead of an ABC?
   Protocols enable structural subtyping — a class satisfies the Protocol
   if it has the right methods, without inheriting from it. This keeps
   the provider clients clean and avoids import coupling.

Message format (used by all callers):
   Messages follow the OpenAI role/content convention:

   {"role": "system",    "content": "You are a wiki maintenance agent..."}
   {"role": "user",      "content": "Ingest this paper: ..."}
   {"role": "assistant", "content": "...", "tool_calls": [...]}
   {"role": "tool",      "tool_call_id": "...", "content": "..."}

   Both Gemini and Groq clients translate this into their own format internally.
   The agent loop always works in this format.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


# Data models
@dataclass
class ToolCall:
    """
    One tool call requested by the LLM in a single response.

    The LLM can request multiple tool calls in one response.
    Each gets its own ToolCall instance with a unique id.

    Fields:
        id:        Provider-assigned unique ID for this call.
                   Fed back to the LLM when returning the tool result,
                   so it can match result to call.
        name:      The tool name, e.g. "read_file", "write_file".
                   Must match a key in the registry dispatch table.
        arguments: Parsed dict of arguments for the tool function.
                   The client is responsible for JSON-parsing this from
                   the raw LLM response before constructing the object.
    """

    id: str
    name: str
    arguments: dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMResponse:
    """
    Normalised response from any LLM provider.

    The agent loop inspects this object to decide what to do next:
      - tool_calls is non-empty  -> execute tools, add results, call again
      - tool_calls is empty      -> text is the final answer, loop ends

    Fields:
        text:        Text content of the response. May be an empty string
                     when the LLM only returns tool calls (common with Groq).
                     May contain a partial explanation alongside tool calls
                     (common with Gemini). Always a string, never None.
        tool_calls:  List of tool calls the LLM wants to make, in order.
                     Empty list means the LLM is done with tool use.
        stop_reason: Why the LLM stopped generating. Normalised values:
                       "tool_use"   — stopped to make tool calls
                       "end_turn"   — finished, no more tool calls
                       "max_tokens" — hit token limit (treat as end_turn)
                       "error"      — something went wrong upstream
        raw:         The original provider response object, kept for
                     debugging. Not used by the agent loop.
    """

    text: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    stop_reason: str = "end_turn"
    raw: Any = field(default=None, repr=False)

    @property
    def has_tool_calls(self) -> bool:
        return len(self.tool_calls) > 0

    @property
    def is_final(self) -> bool:
        """True when the LLM has no more tool calls and the loop should end."""
        return not self.has_tool_calls


# Protocol
@runtime_checkable
class LLMClient(Protocol):
    """
    Interface every LLM provider client must satisfy.

    One method: chat(). Takes messages and optional tools, returns
    a normalised LLMResponse.

    @runtime_checkable allows isinstance(client, LLMClient) checks,
    which the router uses to validate returned clients at startup.
    """

    async def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        temperature: float | None = None,
    ) -> LLMResponse:
        """
        Send a message list to the LLM and return a normalised response.

        Args:
            messages:    Conversation history in OpenAI role/content format.
                         The last message is the most recent user or tool turn.
            tools:       Tool schema list from registry.query_registry() or
                         registry.maintenance_registry(). Pass None for
                         conversations that don't need tool use.
            temperature: Sampling temperature. If None, the client uses
                         its configured default from settings.

        Returns:
            LLMResponse with text and/or tool_calls populated.

        Raises:
            This method should NOT raise on API errors. Instead, return an
            LLMResponse with stop_reason="error" and the error message in
            the text field. The agent loop handles this gracefully.
        """
        ...


# ── Message builder helpers ────────────────────────────────────────────────────
# Small helpers for constructing the message dicts the agent loop sends.
# Import these in base_agent.py to keep message construction consistent.
# ──────────────────────────────────────────────────────────────────────────────


def system_message(content: str) -> dict[str, Any]:
    return {"role": "system", "content": content}


def user_message(content: str) -> dict[str, Any]:
    return {"role": "user", "content": content}


def assistant_message(
    content: str,
    tool_calls: list[ToolCall] | None = None,
) -> dict[str, Any]:
    """
    Build an assistant message, optionally including tool call records.
    When the agent loop appends an LLM response that contained tool calls,
    it uses this to add the assistant turn to the history before adding
    tool results — the LLM needs to see its own tool calls in context.
    """
    msg: dict[str, Any] = {"role": "assistant", "content": content}
    if tool_calls:
        msg["tool_calls"] = [
            {
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.name,
                    "arguments": tc.arguments,
                },
            }
            for tc in tool_calls
        ]
    return msg


def tool_result_message(tool_call_id: str, content: str) -> dict[str, Any]:
    """
    Build a tool result message to feed back after executing a tool call.
    The tool_call_id links this result to the specific call that produced it.
    """
    return {
        "role": "tool",
        "tool_call_id": tool_call_id,
        "content": content,
    }