"""
llm/groq_client.py

Groq client using the groq SDK.
Used by the query agent for fast chat responses.

Model:   Llama 3.3 70B (free tier, ~30 RPM, 128K context window)
SDK:     groq >= 0.9  (pip install groq)

Groq is OpenAI-compatible, so this client is substantially simpler
than gemini_client.py — our canonical message format is already in
OpenAI format. The only translation needed is:
  - Arguments in tool_call records must be JSON strings (not dicts)
  - Response tool_call arguments arrive as JSON strings (parse to dicts)

Rate limiting: Groq free tier is ~30 RPM for Llama 3.3 70B.
On 429s we retry with exponential backoff, same pattern as GeminiClient.
On persistent failure we fall back to the configured fallback model.
"""

from __future__ import annotations

import asyncio
import json
import random
from typing import Any

from groq import Groq

from backend.core.config import settings
from backend.core.logger import get_logger
from backend.llm.base_client import LLMResponse, ToolCall

log = get_logger(__name__)

MAX_RETRIES = 4
BASE_BACKOFF_SECS = 3.0
MAX_BACKOFF_SECS = 30.0

_STOP_REASON_MAP = {
    "stop": "end_turn",
    "tool_calls": "tool_use",
    "length": "max_tokens",
    "end_turn": "end_turn",
}


class GroqClient:
    """
    Wraps the Groq SDK and translates to/from our LLMClient interface.
    Instantiated once by router.py and reused across all query operations.
    """

    def __init__(self) -> None:
        self._client = Groq(api_key=settings.groq_api_key)
        self._model = settings.query_model
        self._fallback = settings.query_model_fallback
        log.info("GroqClient initialised — model: %s", self._model)

    async def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        temperature: float | None = None,
    ) -> LLMResponse:
        """
        Send messages to Groq and return a normalised LLMResponse.
        Retries on rate-limit errors, falls back to fallback model on
        persistent failure. Never raises — errors become LLMResponse.
        """
        temp = temperature if temperature is not None else settings.query_temperature
        prepared = self._prepare_messages(messages)

        for attempt in range(1, MAX_RETRIES + 1):
            model = self._model if attempt <= MAX_RETRIES - 1 else self._fallback
            try:
                response = await asyncio.to_thread(
                    self._client.chat.completions.create,
                    model=model,
                    messages=prepared,
                    tools=tools or None,
                    temperature=temp,
                    max_tokens=settings.max_tokens,
                )
                return self._parse_response(response)

            except Exception as e:
                err_str = str(e)
                is_rate_limit = "429" in err_str or "rate_limit" in err_str.lower()
                is_transient = "503" in err_str or "500" in err_str

                if (is_rate_limit or is_transient) and attempt < MAX_RETRIES:
                    wait = min(
                        BASE_BACKOFF_SECS * (2 ** (attempt - 1)) + random.uniform(0, 1),
                        MAX_BACKOFF_SECS,
                    )
                    log.warning(
                        "GroqClient: %s on attempt %d/%d (model: %s) — retrying in %.1fs",
                        "rate limit" if is_rate_limit else "transient error",
                        attempt,
                        MAX_RETRIES,
                        model,
                        wait,
                    )
                    await asyncio.sleep(wait)
                    continue

                log.error("GroqClient: API error (model: %s): %s", model, e)
                return LLMResponse(
                    text=f"ERROR: Groq API call failed: {e}",
                    stop_reason="error",
                )

        return LLMResponse(text="ERROR: Max retries exceeded.", stop_reason="error")

    # Message preparation
    def _prepare_messages(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Prepare messages for the Groq API.

        Our canonical format stores tool call arguments as Python dicts.
        Groq (like OpenAI) requires them as JSON-encoded strings.
        Everything else passes through unchanged.
        """
        prepared: list[dict[str, Any]] = []

        for msg in messages:
            if msg["role"] == "assistant" and msg.get("tool_calls"):
                prepared.append(self._serialise_tool_calls(msg))
            else:
                prepared.append(msg)

        return prepared

    def _serialise_tool_calls(self, msg: dict[str, Any]) -> dict[str, Any]:
        """
        Return a copy of an assistant message with tool call arguments
        serialised from dicts to JSON strings, as Groq requires.
        """
        serialised_calls = []
        for tc in msg.get("tool_calls", []):
            fn = tc.get("function", {})
            args = fn.get("arguments", {})
            serialised_calls.append(
                {
                    "id": tc["id"],
                    "type": "function",
                    "function": {
                        "name": fn.get("name", ""),
                        "arguments": json.dumps(args)
                        if isinstance(args, dict)
                        else args,
                    },
                }
            )
        return {**msg, "tool_calls": serialised_calls}

    # Response parsing
    def _parse_response(self, response: Any) -> LLMResponse:
        """
        Convert a raw Groq response to our normalised LLMResponse.

        Groq follows the OpenAI response shape:
          response.choices[0].message.content      -> text (may be None)
          response.choices[0].message.tool_calls   -> list (may be None)
          response.choices[0].finish_reason        -> "stop" | "tool_calls" | "length"
        """
        try:
            choice = response.choices[0]
            message = choice.message

            text = message.content or ""

            tool_calls: list[ToolCall] = []
            for tc in message.tool_calls or []:
                raw_args = tc.function.arguments or "{}"
                try:
                    args = json.loads(raw_args)
                except json.JSONDecodeError:
                    log.warning(
                        "GroqClient: could not parse tool args for '%s': %r",
                        tc.function.name,
                        raw_args,
                    )
                    args = {}

                tool_calls.append(
                    ToolCall(
                        id=tc.id,
                        name=tc.function.name,
                        arguments=args,
                    )
                )

            finish = choice.finish_reason or "stop"
            stop_reason = _STOP_REASON_MAP.get(finish, "end_turn")
            if tool_calls:
                stop_reason = "tool_use"

        except Exception as e:
            log.error("GroqClient: failed to parse response: %s", e, exc_info=True)
            return LLMResponse(
                text=f"ERROR: Failed to parse Groq response: {e}",
                stop_reason="error",
                raw=response,
            )

        return LLMResponse(
            text=text,
            tool_calls=tool_calls,
            stop_reason=stop_reason,
            raw=response,
        )

