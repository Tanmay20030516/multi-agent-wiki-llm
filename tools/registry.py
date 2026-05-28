"""
tools/registry.py

Builds the tool-schema dicts sent to the LLM API, and dispatches
incoming tool calls to the correct Python function.

Two responsibilities:

1. Schema export — query_registry() and maintenance_registry() return
   lists of tool definitions in OpenAI/Groq JSON schema format. The LLM
   reads these at the start of each session and knows what tools it has.

2. Dispatch — execute(name, arguments) maps a tool name from an LLM
   response to the actual Python function and calls it. The agent loop
   calls this without knowing anything about individual tool functions.

Adding a new tool:
  1. Write the function in read_tools.py or write_tools.py
  2. Add its schema to _READ_TOOLS or _WRITE_TOOLS below
  3. Add it to _TOOL_FUNCTIONS dispatch table
  That's it — both agents pick it up automatically.
"""

from __future__ import annotations

from typing import Any

from core.logger import get_logger
from tools.read_tools import read_file, read_index, list_files
from tools.write_tools import (
    write_file,
    edit_file,
    update_index,
    append_log,
    delete_file,
    read_source,
)
from tools.search_tools import search_wiki

log = get_logger(__name__)


# ── Tool schema format ─────────────────────────────────────────────────────────
#
# Both Groq (OpenAI-compatible) and Gemini accept this format.
# Each entry is one dict with keys: type, function.
# The function dict has: name, description, parameters (JSON Schema object).
#
# Rules for writing good tool descriptions:
#   - First sentence tells the LLM WHEN to call this tool
#   - Subsequent sentences tell it HOW (argument format, edge cases)
#   - Keep descriptions tight — they eat context window on every call
# ──────────────────────────────────────────────────────────────────────────────

_READ_TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "read_index",
            "description": (
                "Read index.md — the master catalog of all wiki pages. "
                "Always call this first at the start of a query session before "
                "reading any individual pages. Returns the full index content."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": (
                "Read a wiki page and return its full content. "
                "Call this after read_index to get the full content of pages "
                "identified as relevant. "
                "Accepts a bare slug ('attention-mechanism'), a path relative "
                "to the wiki root ('concepts/attention-mechanism.md'), or a "
                "relative path without extension ('concepts/attention-mechanism')."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": (
                            "Page slug or path. Examples: "
                            "'attention-mechanism', "
                            "'concepts/attention-mechanism.md'"
                        ),
                    },
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": (
                "List wiki pages, optionally filtered to one directory. "
                "Use this to verify a page exists before reading it, or to "
                "browse all pages of a given type."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "enum": ["sources", "entities", "concepts", "analyses"],
                        "description": (
                            "Page type directory to list. "
                            "Omit to list all pages across all directories."
                        ),
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_wiki",
            "description": (
                "Full-text search across wiki pages. "
                "Use this when index.md lookup is not sufficient — e.g. the "
                "user's question references something not in a page title but "
                "mentioned in several page bodies. "
                "Results are ranked by match frequency. "
                "Wrap query in double quotes for exact phrase matching."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "Search terms. Multi-word queries use AND logic "
                            "(all words must appear). "
                            "Use quotes for exact phrases: '\"attention mechanism\"'."
                        ),
                    },
                    "page_type": {
                        "type": "string",
                        "enum": ["source", "entity", "concept", "analysis"],
                        "description": "Limit search to one page type. Omit to search all.",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum results to return. Default 8, max 50.",
                        "default": 8,
                    },
                },
                "required": ["query"],
            },
        },
    },
]


_WRITE_TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "read_source",
            "description": (
                "Read a raw source file from data/raw/. "
                "Call this during ingest step 1 to read the source document "
                "before processing it. Never writes anything. "
                "For PDFs, reads the extracted .txt file if available."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": (
                            "Path relative to data/raw/. Examples: "
                            "'papers/vaswani-2017.pdf', "
                            "'articles/2026-05-24-rlhf-overview.md'"
                        ),
                    },
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": (
                "Create or overwrite a wiki page. "
                "Use for new pages. For editing existing pages prefer edit_file "
                "— it is safer. "
                "Path must include the subdirectory "
                "('concepts/attention-mechanism.md'). "
                "Content must start with a YAML frontmatter block (--- ... ---)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": (
                            "Path relative to wiki root, including subdirectory. "
                            "Example: 'concepts/attention-mechanism.md'"
                        ),
                    },
                    "content": {
                        "type": "string",
                        "description": (
                            "Full page content. Must begin with --- frontmatter ---. "
                            "Follow the page template in schema.md section 7."
                        ),
                    },
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": (
                "Replace an exact substring in an existing wiki page. "
                "Safer than write_file for incremental changes. "
                "old_str must appear exactly once in the file — make it "
                "specific enough to be unique. Read the file first to get "
                "the exact current text."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": (
                            "Path relative to wiki root. Example: 'entities/openai.md'"
                        ),
                    },
                    "old_str": {
                        "type": "string",
                        "description": (
                            "Exact text to find and replace. "
                            "Must appear exactly once. Include surrounding "
                            "context if needed to make it unique."
                        ),
                    },
                    "new_str": {
                        "type": "string",
                        "description": (
                            "Replacement text. Pass an empty string to delete old_str."
                        ),
                    },
                },
                "required": ["path", "old_str", "new_str"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_index",
            "description": (
                "Add, update, or remove one entry in index.md. "
                "Call this after write_file to register the new page. "
                "For entities, prefix the summary with the entity type "
                "in brackets: '[researcher] Former OpenAI. Known for nanoGPT.'"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "slug": {
                        "type": "string",
                        "description": "Page slug. Example: 'attention-mechanism'",
                    },
                    "page_type": {
                        "type": "string",
                        "enum": ["source", "entity", "concept", "analysis"],
                        "description": "Type of the page being indexed.",
                    },
                    "summary": {
                        "type": "string",
                        "description": (
                            "One-line description for the index entry. No newlines. "
                            "For entities prefix with type: '[model] GPT-4 by OpenAI...'"
                        ),
                    },
                    "action": {
                        "type": "string",
                        "enum": ["add", "update", "remove"],
                        "description": (
                            "'add' for new pages, "
                            "'update' to change an existing entry, "
                            "'remove' to strike through a deleted page."
                        ),
                        "default": "add",
                    },
                },
                "required": ["slug", "page_type", "summary"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "append_log",
            "description": (
                "Append one activity entry to log.md. "
                "Always call this as the final step of every ingest, "
                "promote, and lint operation. Never skip it."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["ingest", "query->promote", "lint", "schema-update"],
                        "description": "The type of operation just completed.",
                    },
                    "title": {
                        "type": "string",
                        "description": (
                            "Short identifier for this operation. "
                            "For ingest: the source slug. "
                            "For lint: 'health-check-YYYY-MM-DD'."
                        ),
                    },
                    "summary": {
                        "type": "string",
                        "description": "1-2 sentences describing what happened.",
                    },
                    "pages_created": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Slugs of pages created in this operation.",
                    },
                    "pages_updated": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Slugs of pages updated.",
                    },
                    "notes": {
                        "type": "string",
                        "description": (
                            "Anything notable: contradictions found, "
                            "decisions made, open questions."
                        ),
                    },
                },
                "required": ["operation", "title", "summary"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_file",
            "description": (
                "Delete a wiki page. Use sparingly — prefer updating content "
                "to mark a page deprecated rather than deleting it. "
                "After deleting: call update_index with action='remove', "
                "clean up related fields on other pages, then call append_log."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": (
                            "Path relative to wiki root. "
                            "Example: 'analyses/old-comparison.md'"
                        ),
                    },
                },
                "required": ["path"],
            },
        },
    },
]


# ── Dispatch table ─────────────────────────────────────────────────────────────
#
# Maps tool name (string from LLM response) → Python callable.
# Every tool in _READ_TOOLS and _WRITE_TOOLS must have an entry here.
# ──────────────────────────────────────────────────────────────────────────────

_TOOL_FUNCTIONS: dict[str, Any] = {
    # Read tools
    "read_index": read_index,
    "read_file": read_file,
    "list_files": list_files,
    "search_wiki": search_wiki,
    # Write tools
    "read_source": read_source,
    "write_file": write_file,
    "edit_file": edit_file,
    "update_index": update_index,
    "append_log": append_log,
    "delete_file": delete_file,
}


# ── Public API ─────────────────────────────────────────────────────────────────


def query_registry() -> list[dict[str, Any]]:
    """
    Tool schemas for the query agent — read-only tools only.
    Pass this list as the `tools` argument to the Groq/Gemini client.
    """
    return _READ_TOOLS


def maintenance_registry() -> list[dict[str, Any]]:
    """
    Tool schemas for the maintenance agent — read + write tools.
    Pass this list as the `tools` argument to the Gemini client.
    """
    return _READ_TOOLS + _WRITE_TOOLS


def execute(name: str, arguments: dict[str, Any]) -> str:
    """
    Dispatch a tool call from the LLM to the correct Python function.

    Called by base_agent.py every time the LLM returns a tool_call.
    Returns the tool result as a string to be fed back to the LLM.

    Args:
        name:      Tool name exactly as returned by the LLM API.
        arguments: Dict of arguments parsed from the LLM's tool call JSON.

    Returns:
        String result to pass back as a tool result message.
    """
    fn = _TOOL_FUNCTIONS.get(name)

    if fn is None:
        log.warning("execute: unknown tool '%s'", name)
        return (
            f"ERROR: Unknown tool '{name}'. "
            f"Available tools: {', '.join(_TOOL_FUNCTIONS.keys())}."
        )

    log.debug("execute: %s(%s)", name, arguments)

    try:
        result = fn(**arguments)
        # All tool functions return strings, but guard just in case
        return str(result)
    except TypeError as e:
        # Wrong arguments — tell the LLM what it got wrong
        log.warning("execute: bad arguments for '%s': %s", name, e)
        
        return (
            f"ERROR: Invalid arguments for tool '{name}': {e}. "
            f"Check the tool schema and try again."
        )
    except Exception as e:
        log.error("execute: unexpected error in '%s': %s", name, e, exc_info=True)
        return f"ERROR: Tool '{name}' failed unexpectedly: {e}"
