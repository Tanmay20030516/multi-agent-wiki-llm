"""
tools/read_tools.py

Read-only filesystem operations exposed to the LLM as tools.
These are the ONLY tools the query agent receives.
The maintenance agent also gets these, plus everything in write_tools.py.

Every function here:
  - Accepts simple string arguments (what the LLM sends)
  - Returns a string (what gets fed back to the LLM as a tool result)
  - Never raises — errors are returned as descriptive strings so the
    LLM can understand what went wrong and try a different approach
  - Enforces read boundaries via wiki_manager safety checks

The LLM calls these by name with JSON arguments. The agent loop in
base_agent.py receives the tool call, dispatches here, and feeds the
return value back as a tool result message.

Path argument convention (applies to all tools that accept a path):
  The LLM may pass any of these formats — all are handled:
    "attention-mechanism"                         <- bare slug
    "concepts/attention-mechanism.md"             <- relative to wiki root
    "concepts/attention-mechanism"                <- relative, no extension
"""

from __future__ import annotations

from pathlib import Path

from backend.core.logger import get_logger
from backend.core.wiki_manager import wm, PAGE_TYPE_DIRS

log = get_logger(__name__)


# Path resolution helper
def _resolve_wiki_path(path_or_slug: str) -> Path | None:
    """
    Try to resolve a string the LLM provides into an actual wiki file path.

    Resolution order:
      1. Treat as a bare slug — search all subdirectories
      2. Treat as a path relative to wiki root — check directly
      3. Treat as a relative path without .md extension — append and check

    Returns the Path if found, None if not.
    """
    stripped = path_or_slug.strip()

    # 1. Bare slug (no slashes, no extension)
    if "/" not in stripped and not stripped.endswith(".md"):
        found = wm.resolve_slug(stripped)
        if found:
            return found

    # 2. Relative path — resolve against wiki root
    candidate = wm.wiki_root / stripped
    if candidate.exists():
        return candidate

    # 3. Relative path missing .md extension
    candidate_md = wm.wiki_root / (stripped + ".md")
    if candidate_md.exists():
        return candidate_md

    return None


# Tools
def read_file(path: str) -> str:
    """
    Read a wiki page and return its full content.

    The LLM uses this to read individual entity, concept, source, and
    analysis pages after identifying them from the index.

    Args:
        path: Slug, relative path, or relative path without extension.
              e.g. "attention-mechanism"
                   "concepts/attention-mechanism.md"

    Returns:
        Full file content as a string, or an error message if not found.
    """
    log.debug("read_file: %s", path)

    resolved = _resolve_wiki_path(path)

    if resolved is None:
        # Give the LLM a useful hint about what does exist nearby
        slug = Path(path).stem
        similar = _find_similar_slugs(slug)
        hint = f" Similar pages: {similar}" if similar else ""
        return (
            f"ERROR: Page '{path}' not found in the wiki.{hint}\n"
            f"Tip: Use list_files() to see what pages exist, "
            f"or read_index() to browse the full catalog."
        )

    try:
        content = resolved.read_text(encoding="utf-8")
        log.info("read_file: OK — %s (%d chars)", resolved.name, len(content))
        return content
    except OSError as e:
        log.error("read_file: OS error reading %s: %s", resolved, e)
        return f"ERROR: Could not read '{path}': {e}"


def read_index() -> str:
    """
    Read index.md — the master catalog of all wiki pages.

    This is always the first tool call in a query session. The LLM reads
    the index to identify which pages are relevant before calling read_file.

    Returns:
        Full content of index.md, or an error message if it doesn't exist.
    """
    log.debug("read_index called")

    if not wm.index.exists():
        return (
            "ERROR: index.md not found. The wiki may not be initialised yet.\n"
            "Run scripts/init_wiki.py to set up the wiki structure."
        )

    try:
        content = wm.index.read_text(encoding="utf-8")
        log.info("read_index: OK (%d chars)", len(content))
        return content
    except OSError as e:
        log.error("read_index: OS error: %s", e)
        return f"ERROR: Could not read index.md: {e}"


def list_files(directory: str | None = None) -> str:
    """
    List wiki pages, optionally filtered to one page-type directory.

    The LLM uses this when it needs to see all pages of a given type,
    or when it wants to verify that a page exists before reading it.

    Args:
        directory: One of "sources", "entities", "concepts", "analyses".
                   If None or omitted, lists all pages across all directories.

    Returns:
        A formatted plaintext listing, or an error message.

    Example output:
        concepts/ (12 pages)
          attention-mechanism.md
          byte-pair-encoding.md
          chain-of-thought.md
          ...
    """
    log.debug("list_files: directory=%s", directory)

    valid_dirs = list(PAGE_TYPE_DIRS.values())  # sources, entities, concepts, analyses

    if directory is not None:
        # Normalise — accept "concept" or "concepts", "source" or "sources"
        normalised = (
            directory.rstrip("s") + "s" if not directory.endswith("s") else directory
        )
        if normalised not in valid_dirs:
            return (
                f"ERROR: Unknown directory '{directory}'. "
                f"Valid options: {', '.join(valid_dirs)} (or omit for all)."
            )
        return _format_dir_listing(normalised)

    # All directories
    sections: list[str] = []
    total = 0
    for d in valid_dirs:
        section = _format_dir_listing(d)
        sections.append(section)
        # Count lines that end in .md to get page count
        total += sum(1 for line in section.splitlines() if line.strip().endswith(".md"))

    header = f"Wiki pages — {total} total\n" + ("─" * 40) + "\n"
    return header + "\n".join(sections)


def _format_dir_listing(subdir_name: str) -> str:
    """Format one subdirectory's contents as a readable string."""
    subdir = wm.wiki_root / subdir_name

    if not subdir.exists():
        return f"{subdir_name}/ (directory not found)\n"

    pages = sorted(subdir.glob("*.md"))

    if not pages:
        return f"{subdir_name}/ (empty)\n"

    lines = [f"{subdir_name}/ ({len(pages)} page{'s' if len(pages) != 1 else ''})"]
    for page in pages:
        lines.append(f"  {page.name}")
    return "\n".join(lines) + "\n"


def _find_similar_slugs(target: str, max_results: int = 3) -> str:
    """
    Find wiki pages whose slug contains any word from target.
    Used to hint the LLM when a page isn't found.
    """
    target_words = set(target.lower().replace("-", " ").split())
    if not target_words:
        return ""

    matches: list[str] = []
    for page in wm.list_wiki_pages():
        slug = page.stem
        slug_words = set(slug.replace("-", " ").split())
        if target_words & slug_words:  # any word in common
            matches.append(slug)
        if len(matches) >= max_results:
            break

    return ", ".join(matches) if matches else ""
