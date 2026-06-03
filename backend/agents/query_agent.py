"""
agents/query_agent.py

Wires the base agent loop with:
  - Read-only tool set (read_file, read_index, list_files, search_wiki)
  - Gemini client (gemini-2.5-flash-lite — fast, tool-use capable)
  - Query-specific system prompt

The query agent answers user questions grounded in wiki content.
It cannot write to the wiki. If the user wants to save a good answer,
the promote workflow in maintenance_agent handles that separately.

The system prompt instructs the LLM to:
  1. Always read index.md first
  2. Identify and read relevant pages
  3. Synthesize an answer with [[wikilink]] citations
  4. Offer to promote the answer to an analysis page
"""

from __future__ import annotations

from typing import Any, AsyncIterator

from backend.agents.base_agent import run_agent_loop, AgentEvent
from backend.llm.router import get_client
from backend.llm.base_client import system_message, user_message
from backend.tools.registry import query_registry


# System prompt
QUERY_SYSTEM_PROMPT = """\
You are the query agent for an AI/ML research wiki. Your job is to answer
the user's question using the wiki's contents as your knowledge base.

## Your tools (read-only)
- read_index()        — read the master catalog of all wiki pages. ALWAYS call this first.
- read_file(path)     — read a specific wiki page by slug or path.
- list_files(dir)     — list pages in a directory (sources/entities/concepts/analyses).
- search_wiki(query)  — full-text search across all wiki pages.

## Your workflow
1. Call read_index() to see all available pages and their summaries.
2. Identify the 3-5 pages most relevant to the user's question.
3. Call read_file() on each of those pages.
4. If you need more context, use search_wiki() to find additional pages.
5. Synthesize an answer using what you found.

## Citation rules
- When you reference information from a wiki page, cite it as [[slug]].
  Example: "Transformers use self-attention [[attention-mechanism]] to process..."
- Cite the first mention of every entity or concept that has a wiki page.
- Do not cite pages you did not actually read.

## If the wiki doesn't have the answer
- Say clearly that the wiki doesn't contain information on this topic.
- Do NOT make up information or answer from general knowledge.
- Suggest what source could be ingested to add this knowledge.

## Style
- Be concise and precise. This is a research context, not a chatbot.
- Use specific claims with citations, not vague summaries.
- Use LaTeX for math when relevant: $x^2$ inline, $$....$$ for block.
"""


# Entry point
async def run_query(
    question: str,
    conversation_history: list[dict[str, Any]] | None = None,
) -> AsyncIterator[AgentEvent]:
    """
    Answer a user question using wiki content.

    Args:
        question:             The user's question.
        conversation_history: Optional prior turns for multi-turn conversations.
                              Each entry is a {"role": ..., "content": ...} dict.

    Yields:
        AgentEvent objects. The final "done" event contains the answer text.

    Usage:
        async for event in run_query("How does attention work?"):
            if event.type == "done":
                answer = event.content
    """
    client = get_client("query")
    tools = query_registry()

    messages: list[dict[str, Any]] = [system_message(QUERY_SYSTEM_PROMPT)]

    # Append any prior conversation turns
    if conversation_history:
        messages.extend(conversation_history)

    messages.append(user_message(question))

    async for event in run_agent_loop(client, messages, tools):
        yield event
