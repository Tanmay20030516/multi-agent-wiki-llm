"""
agents/maintenance_agent.py

Wires the base agent loop with:
  - Full read-write tool set
  - Gemini client (Gemini 2.5 Flash — long context, reliable tool calling)
  - Workflow-specific system prompts

Three entry points, one per workflow:
  run_ingest()   — process a raw source into wiki pages
  run_lint()     — health-check the wiki
  run_promote()  — save a query result as an analysis page

Each entry point constructs the right system prompt and user message,
then delegates to the same base agent loop. The LLM does the thinking;
this module just sets up the context.
"""

from __future__ import annotations

from typing import Any, AsyncIterator

from backend.agents.base_agent import run_agent_loop, AgentEvent
from backend.llm.router import get_client
from backend.llm.base_client import system_message, user_message
from backend.tools.registry import maintenance_registry
from backend.core.wiki_manager import wm


# Shared preamble
# Loaded once and prepended to every maintenance system prompt.
# Contains the full schema.md so the LLM knows all wiki conventions.


def _load_schema_preamble() -> str:
    """
    Read schema.md and wrap it as the opening section of the system prompt.
    If schema.md doesn't exist, return a minimal fallback.
    """
    if wm.schema.exists():
        schema_content = wm.schema.read_text(encoding="utf-8")
        return (
            "You are the maintenance agent for an AI/ML research wiki.\n"
            "Below is the complete wiki schema — follow every rule precisely.\n\n"
            "---BEGIN SCHEMA---\n"
            f"{schema_content}\n"
            "---END SCHEMA---\n\n"
        )

    return (
        "You are the maintenance agent for an AI/ML research wiki.\n"
        "WARNING: schema.md not found. Follow standard wiki conventions.\n"
    )


# Ingest
INGEST_INSTRUCTIONS = """\
## Your task: INGEST

A new source document has been provided. Process it following the ingest
workflow in schema.md section 10.1 exactly.

## Your tools
- read_source(path)  — read the raw source document (in data/raw/)
- read_index()       — read the master catalog
- read_file(path)    — read any existing wiki page
- search_wiki(query) — search across wiki pages
- list_files(dir)    — list pages in a directory
- write_file(path, content)   — create a new wiki page
- edit_file(path, old, new)   — edit an existing wiki page
- update_index(slug, type, summary) — add/update index entries
- append_log(...)    — write to the activity log (always do this last)

## Critical rules
1. Read the source FIRST, then read index.md, then read related pages.
2. STOP AND PRESENT YOUR PLAN before writing anything. Show the user:
   - What the source is about (2-3 sentences)
   - Key takeaways (3-5 bullets)
   - Which pages you plan to create
   - Which existing pages you plan to update
   - Any contradictions with existing wiki content
3. WAIT for user confirmation. Do not proceed until they say yes.
4. After confirmation, execute writes in this order:
   a. Create the source summary page
   b. Create new entity/concept pages
   c. Update existing entity/concept pages
   d. Update index.md (one update_index call per new/changed page)
   e. Append to log.md (always last)
5. After all writes, report every file created and updated.

## Frontmatter
Every page MUST start with a YAML frontmatter block (--- ... ---).
Follow the templates in schema.md section 7 exactly.

## Cross-references
- Use [[slug]] wikilinks for every first mention of an entity or concept.
- Update the `related` field in BOTH directions when linking pages.
"""


async def run_ingest(
    source_path: str,
    source_text: str | None = None,
) -> AsyncIterator[AgentEvent]:
    """
    Ingest a raw source document into the wiki.

    Args:
        source_path: Path relative to data/raw/,
                     e.g. "articles/2026-05-24-attention-paper.md"
        source_text: If the source was pasted directly (not a file),
                     pass the full text here. The agent will use this
                     instead of calling read_source().

    Yields:
        AgentEvent objects. The agent will pause (via llm_response event)
        to present its plan and wait for confirmation.
    """
    client = get_client("maintenance")
    tools = maintenance_registry()
    schema = _load_schema_preamble()

    if source_text:
        user_content = (
            f"Ingest the following pasted source.\n\n"
            f"**Source path for reference:** {source_path}\n\n"
            f"---BEGIN SOURCE---\n"
            f"{source_text}\n"
            f"---END SOURCE---\n\n"
            f"Follow the ingest workflow. Read schema.md conventions, "
            f"read the index, then present your plan before writing."
        )
    else:
        user_content = (
            f"Ingest the source at: {source_path}\n\n"
            f"Start by calling read_source('{source_path}') to read it, "
            f"then follow the ingest workflow. Read the index, identify "
            f"related pages, then present your plan before writing."
        )

    messages: list[dict[str, Any]] = [
        system_message(schema + INGEST_INSTRUCTIONS),
        user_message(user_content),
    ]

    async for event in run_agent_loop(client, messages, tools):
        yield event


async def continue_ingest(
    messages: list[dict[str, Any]],
    user_response: str,
) -> AsyncIterator[AgentEvent]:
    """
    Continue an ingest after the user responds to the agent's plan.

    The interactive ingest flow works like this:
      1. run_ingest() yields events until the LLM presents its plan
         and stops (no more tool calls — it's waiting for confirmation).
      2. The API layer captures the full message history at that point.
      3. The user sends "yes" or "yes, but change X".
      4. continue_ingest() resumes the loop with the user's response appended.

    Args:
        messages:       The full message history from the paused ingest.
        user_response:  The user's confirmation or modification request.

    Yields:
        AgentEvent objects for the rest of the ingest operation.
    """
    client = get_client("maintenance")
    tools = maintenance_registry()

    messages.append(user_message(user_response))

    async for event in run_agent_loop(client, messages, tools):
        yield event


# Lint
LINT_INSTRUCTIONS = """\
## Your task: LINT

Perform a health check on the entire wiki. Follow the lint workflow
in schema.md section 10.4.

## Your tools
Same as ingest — you have full read-write access.

## Procedure
1. Call read_index() to get the full page catalog.
2. Call list_files() for each directory to compare with index entries.
3. Read pages that might have issues (check frontmatter, wikilinks, dates).
4. Use search_wiki() to find mentions of entities/concepts without pages.
5. Generate a lint report in the format from schema.md section 10.4:
   - 🔴 Errors (must fix)
   - 🟡 Warnings (should fix)
   - 🔵 Suggestions (consider fixing)
   - ✅ Summary line
6. PRESENT the report and WAIT for user approval before fixing anything.
7. Only apply fixes the user approves.
8. After fixes, call append_log() to record the lint pass.

## What to check
- Orphan pages (no inbound `related` links)
- Broken [[wikilinks]] (slug doesn't match any file)
- Missing pages (entities/concepts mentioned but no page exists)
- Stale pages (updated date much older than related sources)
- Contradictions (conflicting claims across pages)
- index.md drift (files on disk not in index, or index entries without files)
- Frontmatter gaps (required fields missing)
- Empty `related` or `tags` arrays (schema requires min 2 each)
"""


async def run_lint() -> AsyncIterator[AgentEvent]:
    """
    Run a wiki health check.

    Yields:
        AgentEvent objects. The agent presents a report and waits
        for approval before applying fixes.
    """
    client = get_client("maintenance")
    tools = maintenance_registry()
    schema = _load_schema_preamble()

    messages: list[dict[str, Any]] = [
        system_message(schema + LINT_INSTRUCTIONS),
        user_message(
            "Run a full lint check on the wiki. "
            "Read the index and files, then present your report."
        ),
    ]

    async for event in run_agent_loop(client, messages, tools):
        yield event


async def continue_lint(
    messages: list[dict[str, Any]],
    user_response: str,
) -> AsyncIterator[AgentEvent]:
    """Continue a lint operation after user approves/rejects fixes."""
    client = get_client("maintenance")
    tools = maintenance_registry()
    messages.append(user_message(user_response))

    async for event in run_agent_loop(client, messages, tools):
        yield event


# Promote
PROMOTE_INSTRUCTIONS = """\
## Your task: PROMOTE

Save a query result as a permanent analysis page in the wiki.
Follow the promote workflow in schema.md section 10.3.

## Your tools
Same as ingest — you have full read-write access.

## Procedure
1. Read index.md to check for existing related analyses.
2. Propose a slug for the new analysis page and confirm with the user.
3. Write the analysis page using the analysis template (schema.md 7.4).
   - Include `promoted_from` in frontmatter with the original question.
   - List all wiki pages referenced in the `sources_used` field.
   - Add [[wikilinks]] for every entity and concept mentioned.
4. Update index.md with the new entry.
5. Update `related` fields on all pages referenced by the analysis.
6. Call append_log() to record the promotion.
"""


async def run_promote(
    question: str,
    answer: str,
    suggested_slug: str | None = None,
) -> AsyncIterator[AgentEvent]:
    """
    Promote a query answer to a permanent analysis page.

    Args:
        question:       The original query that produced this answer.
        answer:         The answer text to promote (may contain [[wikilinks]]).
        suggested_slug: Optional slug suggestion. The agent will confirm
                        or propose an alternative.

    Yields:
        AgentEvent objects.
    """
    client = get_client("maintenance")
    tools = maintenance_registry()
    schema = _load_schema_preamble()

    slug_hint = f"\nSuggested slug: `{suggested_slug}`" if suggested_slug else ""

    messages: list[dict[str, Any]] = [
        system_message(schema + PROMOTE_INSTRUCTIONS),
        user_message(
            f"Promote this query result to an analysis page.\n\n"
            f"**Original question:** {question}\n\n"
            f"**Answer to promote:**\n{answer}\n"
            f"{slug_hint}\n\n"
            f"Read the index first, then confirm the slug with me before writing."
        ),
    ]

    async for event in run_agent_loop(client, messages, tools):
        yield event


async def continue_promote(
    messages: list[dict[str, Any]],
    user_response: str,
) -> AsyncIterator[AgentEvent]:
    """Continue a promote operation after user confirms the slug."""
    client = get_client("maintenance")
    tools = maintenance_registry()
    messages.append(user_message(user_response))

    async for event in run_agent_loop(client, messages, tools):
        yield event
