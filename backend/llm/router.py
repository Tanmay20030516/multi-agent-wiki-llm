"""
llm/router.py

Returns the right LLM client for a given operation type.
This is the only file that knows which model maps to which operation.
Swap models by changing one line here — nothing else needs to change.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from backend.core.config import settings
from backend.core.logger import get_logger
from backend.llm.base_client import LLMClient
from backend.llm.gemini_client import GeminiClient

log = get_logger(__name__)

OperationType = Literal["query", "maintenance"]


@lru_cache(maxsize=2)
def get_client(operation: OperationType) -> LLMClient:
    """
    Return the cached LLM client for the given operation type.

      get_client("query")       -> GeminiClient (gemini-2.5-flash-lite, fast chat)
      get_client("maintenance") -> GeminiClient (gemini-2.5-flash, long context)

    Clients are instantiated once and reused — lru_cache ensures we don't
    create a new SDK connection on every agent invocation.

    Args:
        operation: "query" for chat/answer operations,
                   "maintenance" for ingest/lint/promote operations.

    Returns:
        An LLMClient instance satisfying the Protocol.
    """
    if operation == "query":
        client = GeminiClient(
            model=settings.query_model,
            default_temperature=settings.query_temperature,
        )
        log.info("Router: query -> GeminiClient (%s)", settings.query_model)
    elif operation == "maintenance":
        client = GeminiClient(
            model=settings.maintenance_model,
            default_temperature=settings.maintenance_temperature,
        )
        log.info("Router: maintenance -> GeminiClient (%s)", settings.maintenance_model)
    else:
        raise ValueError(
            f"Unknown operation type '{operation}'. Use 'query' or 'maintenance'."
        )

    assert isinstance(client, LLMClient), (
        f"{type(client).__name__} does not satisfy the LLMClient Protocol. "
        "Ensure it implements async chat(messages, tools, temperature) -> LLMResponse."
    )

    return client
