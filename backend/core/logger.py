"""
core/logger.py

Two responsibilities:

1. Python logging setup — structured console output for the server process.
   Every module gets its logger via: log = get_logger(__name__)

2. Wiki activity log — append_activity() writes human-readable entries to
   log.md in the format defined in schema.md section 9.
   Called by agents at the end of every ingest, promote, and lint operation.
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from backend.core.config import settings


# Operation types (mirrors schema.md section 9)
Operation = Literal["ingest", "query->promote", "lint", "schema-update"]


# Python logging setup
def _build_formatter() -> logging.Formatter:
    """
    Single-line format:
      2026-05-24 14:30:01 | INFO     | agents.maintenance | Ingest complete
    Clean enough to read in Docker logs or a terminal.
    """
    return logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def _configure_root_logger() -> None:
    """
    Configure the root logger once at import time.
    All child loggers (from get_logger) inherit this config.
    """
    root = logging.getLogger()

    # Avoid adding duplicate handlers if this module is imported multiple times
    if root.handlers:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_build_formatter())
    root.addHandler(handler)
    root.setLevel(settings.log_level.upper())


_configure_root_logger()


def get_logger(name: str) -> logging.Logger:
    """
    Get a named logger for a module.

    Usage at the top of any backend file:
        from core.logger import get_logger
        log = get_logger(__name__)

        log.info("Starting ingest for %s", slug)
        log.warning("Rate limit hit, retrying in %ds", delay)
        log.error("Tool call failed: %s", err)
    """
    return logging.getLogger(name)


# Wiki activity log
def append_activity(
    operation: Operation,
    title: str,
    summary: str,
    pages_created: list[str] | None = None,
    pages_updated: list[str] | None = None,
    notes: str | None = None,
) -> None:
    """
    Append one entry to log.md following the format in schema.md section 9.

    This is the human-readable record of everything the maintenance agent does.
    New entries go at the top (below the header), not at the bottom — so the
    most recent activity is always visible without scrolling.

    Args:
        operation:     One of: ingest | query->promote | lint | schema-update
        title:         Short description e.g. "vaswani-2017-attention"
        summary:       1-2 sentences of what happened.
        pages_created: List of slugs created in this operation.
        pages_updated: List of slugs updated (with optional notes in parens).
        notes:         Anything notable — contradictions found, user decisions, etc.

    Example output in log.md:
        ## [2026-05-24 14:30] ingest | vaswani-2017-attention
        **Operation:** ingest
        **Summary:** Ingested "Attention Is All You Need". Created 4 pages,
        updated 2 existing pages.
        **Pages created:** [[vaswani-2017-attention]], [[attention-mechanism]],
        [[ashish-vaswani]], [[google-brain]]
        **Pages updated:** [[index]] (4 new entries), [[log]] (this entry)
        **Notes:** No contradictions found with existing wiki content.
        ---
    """
    from backend.core.wiki_manager import wm  # deferred to avoid eager Settings() at import time
    log = get_logger(__name__)

    if not wm.is_initialised():
        log.warning(
            "Wiki not initialised — skipping append_activity. "
            "Run scripts/init_wiki.py first."
        )
        return

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    created_str = _format_slug_list(pages_created)
    updated_str = _format_slug_list(pages_updated)

    entry = _build_entry(
        timestamp=timestamp,
        operation=operation,
        title=title,
        summary=summary,
        created_str=created_str,
        updated_str=updated_str,
        notes=notes,
    )

    _prepend_to_log(wm.log, entry)
    log.info("Activity logged: [%s] %s | %s", timestamp, operation, title)


def _format_slug_list(slugs: list[str] | None) -> str:
    """Convert a list of slugs to comma-separated wikilinks."""
    if not slugs:
        return "—"
    return ", ".join(f"[[{s}]]" for s in slugs)


def _build_entry(
    timestamp: str,
    operation: str,
    title: str,
    summary: str,
    created_str: str,
    updated_str: str,
    notes: str | None,
) -> str:
    lines = [
        f"## [{timestamp}] {operation} | {title}",
        "",
        f"**Operation:** {operation}",
        f"**Summary:** {summary}",
        f"**Pages created:** {created_str}",
        f"**Pages updated:** {updated_str}",
    ]
    if notes:
        lines.append(f"**Notes:** {notes}")
    lines += ["", "---", ""]
    return "\n".join(lines)


def _prepend_to_log(log_path: Path, entry: str) -> None:
    """
    Insert entry at the top of log.md, just below the '# Activity Log' header.
    If log.md doesn't exist or has no header yet, write it fresh.
    """
    header = "# Activity Log\n"

    if log_path.exists():
        existing = log_path.read_text(encoding="utf-8")
        if existing.startswith(header):
            # Insert new entry right after the header line
            rest = existing[len(header) :]
            log_path.write_text(header + "\n" + entry + rest, encoding="utf-8")
            return

    # First entry ever — write header + entry from scratch
    log_path.write_text(header + "\n" + entry, encoding="utf-8")
