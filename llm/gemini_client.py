"""
llm/gemini_client.py

Gemini client using the google-genai SDK (v1.0+).
Used by the maintenance agent for ingest, lint, and promote operations.

Model:   Gemini 2.5 Flash (free tier, 1M token context window)
SDK:     google-genai >= 1.0  (pip install google-genai)

The main work here is translation — our canonical message format
(OpenAI-style role/content dicts) maps to Gemini's types.Content objects,
and Gemini's response maps back to our LLMResponse. Everything else in
the codebase stays provider-agnostic.

Rate limiting: Gemini free tier allows ~10-30 RPM depending on model.
On 429s we retry with exponential backoff up to MAX_RETRIES times.
"""

from __future__ import annotations

import asyncio
import json
import random
from typing import Any

from google import genai
from google.genai import types

from core.config import settings
from core.logger import get_logger
from llm.base_client import LLMResponse, ToolCall

log = get_logger(__name__)

# Retry config for rate limit / transient errors
MAX_RETRIES = 4
BASE_BACKOFF_SECS = 5.0
MAX_BACKOFF_SECS = 60.0

# Gemini stop-reason strings → our normalised values
_STOP_REASON_MAP = {
    "STOP": "end_turn",
    "MAX_TOKENS": "max_tokens",
    "SAFETY": "end_turn",  # treat safety blocks as end_turn
    "RECITATION": "end_turn",
    "OTHER": "end_turn",
    "FUNCTION_CALLS": "tool_use",  # older SDK name
    "TOOL_CODE": "tool_use",
    "MALFORMED_FUNCTION_CALL": "end_turn",
}


class GeminiClient:
    """
    Wraps the google-genai SDK and translates to/from our LLMClient interface.
    Instantiated once by router.py and reused across all maintenance operations.
    """

    def __init__(self) -> None:
        self._client = genai.Client(api_key=settings.gemini_api_key)
        self._model = settings.maintenance_model
        log.info("GeminiClient initialised — model: %s", self._model)

    async def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        temperature: float | None = None,
    ) -> LLMResponse:
        """
        Send messages to Gemini and return a normalised LLMResponse.
        Retries on rate-limit errors. Never raises — errors become LLMResponse.
        """
        temp = (
            temperature if temperature is not None else settings.maintenance_temperature
        )

        # Extract system message (Gemini takes it separately from contents)
        system_instruction, contents = self._convert_messages(messages)

        # Convert our tool schemas to Gemini FunctionDeclarations
        gemini_tools = self._convert_tools(tools) if tools else None

        config = types.GenerateContentConfig(
            temperature=temp,
            max_output_tokens=settings.max_tokens,
            system_instruction=system_instruction or None,
            tools=gemini_tools or None,
        )

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                # google-genai SDK is synchronous — run in thread pool
                # so we don't block the FastAPI event loop
                response = await asyncio.to_thread(
                    self._client.models.generate_content,
                    model=self._model,
                    contents=contents,
                    config=config,
                )
                return self._parse_response(response)

            except Exception as e:
                err_str = str(e)
                is_rate_limit = "429" in err_str or "quota" in err_str.lower()
                is_transient = "503" in err_str or "500" in err_str

                if (is_rate_limit or is_transient) and attempt < MAX_RETRIES:
                    wait = min(
                        BASE_BACKOFF_SECS * (2 ** (attempt - 1)) + random.uniform(0, 1),
                        MAX_BACKOFF_SECS,
                    )
                    log.warning(
                        "GeminiClient: %s error on attempt %d/%d — retrying in %.1fs",
                        "Rate limit" if is_rate_limit else "Transient",
                        attempt,
                        MAX_RETRIES,
                        wait,
                    )
                    await asyncio.sleep(wait)
                    continue

                log.error("GeminiClient: API error: %s", e)
                return LLMResponse(
                    text=f"ERROR: Gemini API call failed: {e}",
                    stop_reason="error",
                )

        # Should not reach here, but satisfy the type checker
        return LLMResponse(text="ERROR: Max retries exceeded.", stop_reason="error")

    # Message conversion
    def _convert_messages(
        self,
        messages: list[dict[str, Any]],
    ) -> tuple[str, list[types.Content]]:
        """
        Convert OpenAI-format messages to (system_instruction, contents).

        Gemini separates system instructions from the conversation contents.
        Tool result messages (role="tool") become function_response parts
        attached to a "user" turn — Gemini's convention for returning results.
        """
        system_instruction = ""
        contents: list[types.Content] = []

        i = 0
        while i < len(messages):
            msg = messages[i]
            role = msg["role"]

            if role == "system":
                # Gemini takes this out-of-band, not in contents
                system_instruction = msg.get("content", "")
                i += 1
                continue

            if role == "user":
                contents.append(
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(msg.get("content", ""))],
                    )
                )
                i += 1
                continue

            if role == "assistant":
                contents.append(self._convert_assistant_message(msg))
                i += 1
                continue

            if role == "tool":
                # Collect all consecutive tool results into one user turn
                tool_parts: list[types.Part] = []
                while i < len(messages) and messages[i]["role"] == "tool":
                    tool_msg = messages[i]
                    name = self._find_tool_name(messages, i)
                    tool_parts.append(
                        types.Part(
                            function_response=types.FunctionResponse(
                                name=name,
                                response={"result": tool_msg.get("content", "")},
                            )
                        )
                    )
                    i += 1
                contents.append(types.Content(role="user", parts=tool_parts))
                continue

            # Unknown role — skip
            log.warning("GeminiClient: unknown message role '%s', skipping", role)
            i += 1

        return system_instruction, contents

    def _convert_assistant_message(self, msg: dict[str, Any]) -> types.Content:
        """
        Convert an assistant message to a Gemini model turn.
        If the message contains tool_calls, add FunctionCall parts.
        """
        parts: list[types.Part] = []

        text = msg.get("content", "")
        if text:
            parts.append(types.Part.from_text(text))

        for tc in msg.get("tool_calls", []):
            fn = tc.get("function", {})
            args = fn.get("arguments", {})
            # arguments may be a dict or a JSON string depending on the source
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except json.JSONDecodeError:
                    args = {}
            parts.append(
                types.Part(
                    function_call=types.FunctionCall(
                        name=fn.get("name", ""),
                        args=args,
                    )
                )
            )

        return types.Content(role="model", parts=parts or [types.Part.from_text("")])

    def _find_tool_name(
        self, messages: list[dict[str, Any]], tool_msg_index: int
    ) -> str:
        """
        Find the tool name for a tool-result message by scanning back through
        the message history to find the matching tool_call_id in the preceding
        assistant message.

        Gemini's FunctionResponse requires the tool name, not the call ID.
        """
        target_id = messages[tool_msg_index].get("tool_call_id", "")

        for j in range(tool_msg_index - 1, -1, -1):
            if messages[j]["role"] == "assistant":
                for tc in messages[j].get("tool_calls", []):
                    if tc.get("id") == target_id:
                        return tc.get("function", {}).get("name", "unknown_tool")
                break

        log.warning(
            "GeminiClient: could not find tool name for call_id '%s'", target_id
        )
        return "unknown_tool"

    # Tool schema conversion
    def _convert_tools(self, tools: list[dict[str, Any]]) -> list[types.Tool]:
        """
        Convert OpenAI-format tool schemas to Gemini FunctionDeclarations.

        OpenAI: {"type": "function", "function": {"name": ..., "parameters": ...}}
        Gemini: types.FunctionDeclaration(name=..., parameters=...)

        JSON Schema types are lowercase in OpenAI ("string", "object") and
        must be uppercase in Gemini ("STRING", "OBJECT"). We convert here.
        """
        declarations: list[types.FunctionDeclaration] = []

        for tool in tools:
            fn = tool.get("function", {})
            name = fn.get("name", "")
            description = fn.get("description", "")
            parameters = self._convert_schema(fn.get("parameters", {}))

            declarations.append(
                types.FunctionDeclaration(
                    name=name,
                    description=description,
                    parameters=parameters,
                )
            )

        return [types.Tool(function_declarations=declarations)]

    def _convert_schema(self, schema: dict[str, Any]) -> types.Schema | None:
        """
        Recursively convert a JSON Schema dict to a Gemini types.Schema.
        Handles object, array, string, integer, boolean, and enum.
        """
        if not schema:
            return None

        schema_type = schema.get("type", "")
        gemini_type = _JSON_TYPE_TO_GEMINI.get(schema_type.lower(), types.Type.STRING)

        kwargs: dict[str, Any] = {"type": gemini_type}

        if "description" in schema:
            kwargs["description"] = schema["description"]

        if "enum" in schema:
            kwargs["enum"] = schema["enum"]

        if gemini_type == types.Type.OBJECT:
            raw_props = schema.get("properties", {})
            kwargs["properties"] = {
                k: self._convert_schema(v)
                for k, v in raw_props.items()
                if self._convert_schema(v) is not None
            }
            if "required" in schema:
                kwargs["required"] = schema["required"]

        if gemini_type == types.Type.ARRAY:
            items = schema.get("items")
            if items:
                kwargs["items"] = self._convert_schema(items)

        return types.Schema(**kwargs)

    # Response parsing
    def _parse_response(self, response: Any) -> LLMResponse:
        """
        Convert a raw Gemini response to our normalised LLMResponse.

        Gemini may return:
          - Text only
          - Function calls only
          - Text + function calls (common when the model explains its reasoning)
        We collect all parts and populate text and tool_calls accordingly.
        """
        text_parts: list[str] = []
        tool_calls: list[ToolCall] = []

        try:
            candidates = response.candidates or []
            if not candidates:
                return LLMResponse(
                    text="ERROR: Gemini returned no candidates.",
                    stop_reason="error",
                    raw=response,
                )

            candidate = candidates[0]
            content = candidate.content

            for part in content.parts or []:
                if hasattr(part, "text") and part.text:
                    text_parts.append(part.text)

                if hasattr(part, "function_call") and part.function_call:
                    fc = part.function_call
                    tool_calls.append(
                        ToolCall(
                            id=f"gemini-{fc.name}-{len(tool_calls)}",
                            name=fc.name,
                            arguments=dict(fc.args) if fc.args else {},
                        )
                    )

            # Normalise stop reason
            finish_reason = getattr(candidate, "finish_reason", None)
            finish_str = finish_reason.name if finish_reason else "STOP"
            stop_reason = _STOP_REASON_MAP.get(finish_str, "end_turn")

            # If there are tool calls, stop reason is tool_use regardless
            if tool_calls:
                stop_reason = "tool_use"

        except Exception as e:
            log.error("GeminiClient: failed to parse response: %s", e, exc_info=True)
            return LLMResponse(
                text=f"ERROR: Failed to parse Gemini response: {e}",
                stop_reason="error",
                raw=response,
            )

        return LLMResponse(
            text="\n".join(text_parts),
            tool_calls=tool_calls,
            stop_reason=stop_reason,
            raw=response,
        )


# Type map
_JSON_TYPE_TO_GEMINI: dict[str, types.Type] = {
    "string": types.Type.STRING,
    "number": types.Type.NUMBER,
    "integer": types.Type.INTEGER,
    "boolean": types.Type.BOOLEAN,
    "object": types.Type.OBJECT,
    "array": types.Type.ARRAY,
}