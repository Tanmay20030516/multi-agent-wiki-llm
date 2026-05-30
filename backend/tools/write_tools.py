"""
tools/write_tools.py

Read-write filesystem operations for the maintenance agent.
The query agent never receives these — only maintenance_agent does.

These tools are the only way the LLM writes to the wiki. Every function:
  - Validates the target path is inside wiki/ before touching anything
  - Refuses to touch schema.md
  - Returns a result string the LLM reads as a tool result
  - Logs every write to the Python logger for observability

Security model:
  - wm.assert_in_wiki()     → path must be inside data/wiki/
  - wm.assert_not_schema()  → schema.md is never agent-writable
  - wm.assert_in_raw()      → read_source() cannot escape data/raw/
  - Slug validation          → no path traversal via malformed slugs
"""

from __future__ import annotations

import re
from pathlib import Path

from backend.core.logger import get_logger, append_activity  # , Operation
from backend.core.wiki_manager import wm, PAGE_TYPE_DIRS

log = get_logger(__name__)


# Frontmatter validation
_FRONTMATTER_RE = re.compile(r"^---\s*\n.*?\n---\s*\n", re.DOTALL)


def _has_frontmatter(content: str) -> bool:
    return bool(_FRONTMATTER_RE.match(content))


# Tools
def write_file(path: str, content: str) -> str:
    """
    Create or overwrite a wiki page with the given content.

    Use this to create new pages. For making targeted edits to an
    existing page prefer edit_file() — it is safer and shows the LLM
    exactly what changed.

    Args:
        path:    Relative to wiki root, e.g. "concepts/attention-mechanism.md"
                 Must include the subdirectory. Bare slugs are rejected because
                 the LLM must decide the page type before writing.
        content: Full markdown content. Must begin with a YAML frontmatter block.

    Returns:
        Success message with character count, or an error string.
    """
    log.debug("write_file: %s", path)

    # Reject bare slugs — force the LLM to declare the page type in the path
    if "/" not in path:
        return (
            f"ERROR: Path '{path}' must include a subdirectory. "
            f"Example: 'concepts/{path}.md'. "
            f"Valid subdirectories: {', '.join(PAGE_TYPE_DIRS.values())}."
        )

    resolved = wm.wiki_root / path.strip()

    try:
        wm.assert_in_wiki(resolved)
        wm.assert_not_schema(resolved)
    except PermissionError as e:
        return f"ERROR: {e}"

    if not _has_frontmatter(content):
        return (
            "ERROR: Content must begin with a YAML frontmatter block (--- ... ---). "
            "Every wiki page requires frontmatter. See schema.md section 4."
        )

    action = "Updated" if resolved.exists() else "Created"

    try:
        resolved.parent.mkdir(parents=True, exist_ok=True)
        resolved.write_text(content, encoding="utf-8")
        log.info("write_file: %s %s (%d chars)", action, resolved.name, len(content))
        return f"{action}: {path} ({len(content)} chars written)."
    except OSError as e:
        log.error("write_file: OS error writing %s: %s", path, e)
        return f"ERROR: Could not write '{path}': {e}"


def edit_file(path: str, old_str: str, new_str: str) -> str:
    """
    Replace an exact substring in an existing wiki page.

    Safer than write_file for incremental changes — only the specified
    substring is modified, everything else is untouched. The LLM must
    provide the exact text to replace, which forces it to read the file
    first and reason carefully about what to change.

    Rules:
      - old_str must appear exactly once in the file. Zero matches → error.
        More than one match → error (ambiguous; make old_str more specific).
      - Replacement is exact, including whitespace and newlines.
      - Cannot be used on schema.md.

    Args:
        path:    Relative to wiki root, e.g. "entities/openai.md"
        old_str: Exact text to find and replace.
        new_str: Text to substitute in its place. Can be empty string to delete.

    Returns:
        Success message, or an error string describing the problem.
    """
    log.debug("edit_file: %s", path)

    resolved = _resolve_existing_wiki_path(path)
    if isinstance(resolved, str):
        return resolved  # error message from helper

    try:
        wm.assert_not_schema(resolved)
    except PermissionError as e:
        return f"ERROR: {e}"

    try:
        original = resolved.read_text(encoding="utf-8")
    except OSError as e:
        return f"ERROR: Could not read '{path}': {e}"

    count = original.count(old_str)
    if count == 0:
        return (
            f"ERROR: The text to replace was not found in '{path}'.\n"
            f"Make sure you copied it exactly, including whitespace.\n"
            f"Tip: Read the file again with read_file('{path}') to see the current content."
        )
    if count > 1:
        return (
            f"ERROR: The text to replace appears {count} times in '{path}'. "
            f"Make old_str longer and more specific so it matches exactly once."
        )

    updated = original.replace(old_str, new_str, 1)

    try:
        resolved.write_text(updated, encoding="utf-8")
        log.info("edit_file: OK — %s", resolved.name)
        return (
            f"Edited: {path} — replaced {len(old_str)} chars with {len(new_str)} chars."
        )
    except OSError as e:
        log.error("edit_file: OS error writing %s: %s", path, e)
        return f"ERROR: Could not write '{path}': {e}"


def update_index(
    slug: str,
    page_type: str,
    summary: str,
    action: str = "add",
) -> str:
    """
    Add, update, or remove one entry in index.md.

    index.md has a strict format (schema.md section 8). Rather than asking
    the LLM to write raw markdown into the index, this tool handles the
    insertion logic — finding the right section, formatting the entry
    correctly, and keeping counts accurate.

    Args:
        slug:      The page slug, e.g. "attention-mechanism".
        page_type: One of: source, entity, concept, analysis.
                   For entities, also pass the entity sub-type in summary
                   so this tool can route to the right sub-section.
        summary:   One-line description for the index entry (no newlines).
                   For entity pages, prefix with entity_type in brackets:
                   "[researcher] Former OpenAI, Tesla. Known for nanoGPT."
        action:    "add"    → insert new entry (error if slug already exists)
                   "update" → replace existing entry (error if not found)
                   "remove" → strike through entry with ~~[[slug]]~~

    Returns:
        Success message, or an error string.
    """
    log.debug("update_index: %s %s %s", action, page_type, slug)

    if not wm.index.exists():
        return "ERROR: index.md not found. Run scripts/init_wiki.py first."

    if page_type not in PAGE_TYPE_DIRS:
        return (
            f"ERROR: Unknown page_type '{page_type}'. "
            f"Valid options: {', '.join(PAGE_TYPE_DIRS.keys())}."
        )

    if action not in ("add", "update", "remove"):
        return "ERROR: action must be 'add', 'update', or 'remove'."

    if "\n" in summary:
        return "ERROR: summary must be a single line with no newlines."

    try:
        content = wm.index.read_text(encoding="utf-8")
    except OSError as e:
        return f"ERROR: Could not read index.md: {e}"

    entry_line = f"- [[{slug}]] — {summary}"
    existing_pattern = re.compile(rf"^- \[\[{re.escape(slug)}\]\].*$", re.MULTILINE)
    existing_match = existing_pattern.search(content)

    if action == "add":
        if existing_match:
            return (
                f"ERROR: Slug '[[{slug}]]' already exists in index.md. "
                f"Use action='update' to change it."
            )
        content = _insert_index_entry(content, page_type, entry_line, slug)

    elif action == "update":
        if not existing_match:
            return (
                f"ERROR: Slug '[[{slug}]]' not found in index.md. "
                f"Use action='add' to create it."
            )
        content = existing_pattern.sub(entry_line, content)

    elif action == "remove":
        if not existing_match:
            return f"ERROR: Slug '[[{slug}]]' not found in index.md."
        struck = f"- ~~[[{slug}]]~~ — removed"
        content = existing_pattern.sub(struck, content)

    # Update the "Last updated" line and page count
    content = _refresh_index_header(content)

    try:
        wm.index.write_text(content, encoding="utf-8")
        log.info("update_index: %s [[%s]] OK", action, slug)
        return f"Index {action}d: [[{slug}]] in {page_type}s section."
    except OSError as e:
        log.error("update_index: OS error: %s", e)
        return f"ERROR: Could not write index.md: {e}"


def append_log(
    operation: str,
    title: str,
    summary: str,
    pages_created: list[str] | None = None,
    pages_updated: list[str] | None = None,
    notes: str | None = None,
) -> str:
    """
    Append one activity entry to log.md.

    Always call this as the final step of every ingest, promote, and
    lint operation. The log is the permanent record of what the agent did.

    Args:
        operation:     One of: ingest | query->promote | lint | schema-update
        title:         Short identifier e.g. "vaswani-2017-attention"
        summary:       1-2 sentences describing what happened.
        pages_created: List of slugs created in this operation.
        pages_updated: List of slugs updated (include brief note in parens if useful).
        notes:         Anything notable — contradictions, decisions, open questions.

    Returns:
        Confirmation string, or an error message.
    """
    log.debug("append_log: %s | %s", operation, title)

    valid_ops = ("ingest", "query->promote", "lint", "schema-update")
    if operation not in valid_ops:
        return (
            f"ERROR: Unknown operation '{operation}'. "
            f"Valid options: {', '.join(valid_ops)}."
        )

    try:
        append_activity(
            operation=operation,  # type: ignore[arg-type]
            title=title,
            summary=summary,
            pages_created=pages_created,
            pages_updated=pages_updated,
            notes=notes,
        )
        return f"Log entry written: [{operation}] {title}."
    except Exception as e:
        log.error("append_log: failed: %s", e)
        return f"ERROR: Could not write log entry: {e}"


def delete_file(path: str) -> str:
    """
    Delete a wiki page.

    Use sparingly — prefer marking a page as deprecated by updating its
    content rather than deleting it. Deletion removes history.

    If you delete a page, you must also:
      1. Call update_index(slug, page_type, summary, action="remove")
      2. Remove the slug from the `related` field of all pages that reference it
      3. Call append_log() to record the deletion

    Args:
        path: Relative to wiki root, e.g. "analyses/old-comparison.md"

    Returns:
        Confirmation string, or an error message.
    """
    log.debug("delete_file: %s", path)

    resolved = _resolve_existing_wiki_path(path)
    if isinstance(resolved, str):
        return resolved  # error message

    try:
        wm.assert_not_schema(resolved)
    except PermissionError as e:
        return f"ERROR: {e}"

    slug = resolved.stem

    try:
        resolved.unlink()
        log.info("delete_file: deleted %s", resolved.name)
        return (
            f"Deleted: {path}.\n"
            f"Remember to: update_index('{slug}', ..., action='remove') "
            f"and remove [[{slug}]] from related fields on other pages."
        )
    except OSError as e:
        log.error("delete_file: OS error: %s", e)
        return f"ERROR: Could not delete '{path}': {e}"


def read_source(path: str) -> str:
    """
    Read a file from the immutable raw sources directory.

    This is the only way the maintenance agent reads source documents.
    The query agent does not have this tool — it reads from wiki/ only.

    Args:
        path: Path relative to data/raw/, e.g. "papers/vaswani-2017.pdf"
              or "articles/2026-05-24-rlhf-overview.md"

    Returns:
        Full file content as a string, or an error message.

    Note on PDFs: PDF binary content is not human-readable. If a PDF
    is passed, the backend will have extracted its text during ingest
    and saved it as a .txt alongside the PDF. Pass the .txt path instead,
    or the frontend will handle extraction before calling this tool.
    """
    log.debug("read_source: %s", path)

    resolved = wm.raw_root / path.strip()

    try:
        wm.assert_in_raw(resolved)
    except PermissionError as e:
        return f"ERROR: {e}"

    if not resolved.exists():
        # Help the LLM find what's actually there
        available = [str(f.relative_to(wm.raw_root)) for f in wm.list_raw_files()]
        hint = (
            f" Available files: {available[:10]}" if available else " (raw/ is empty)"
        )
        return f"ERROR: Source file '{path}' not found.{hint}"

    if resolved.suffix.lower() == ".pdf":
        # Check if a text extraction exists alongside the PDF
        txt_path = resolved.with_suffix(".txt")
        if txt_path.exists():
            content = txt_path.read_text(encoding="utf-8", errors="replace")
            log.info("read_source: reading extracted text for %s", resolved.name)
            return f"[Extracted text from {resolved.name}]\n\n{content}"
        return (
            f"ERROR: '{path}' is a PDF. "
            f"Text extraction file '{resolved.stem}.txt' not found alongside it. "
            f"Upload the PDF via the Admin UI — extraction happens automatically on ingest."
        )

    try:
        content = resolved.read_text(encoding="utf-8", errors="replace")
        log.info("read_source: OK — %s (%d chars)", resolved.name, len(content))
        return content
    except OSError as e:
        log.error("read_source: OS error reading %s: %s", path, e)
        return f"ERROR: Could not read '{path}': {e}"


# Private helpers
def _resolve_existing_wiki_path(path: str) -> Path | str:
    """
    Resolve a path string to an existing wiki file.
    Returns the Path on success, or an error string if not found/safe.
    """
    stripped = path.strip()
    resolved = wm.wiki_root / stripped

    if not stripped.endswith(".md"):
        resolved = wm.wiki_root / (stripped + ".md")

    try:
        wm.assert_in_wiki(resolved)
    except PermissionError as e:
        return f"ERROR: {e}"

    if not resolved.exists():
        return (
            f"ERROR: '{path}' does not exist in the wiki. "
            f"Use list_files() to see what pages exist."
        )

    return resolved


def _insert_index_entry(
    content: str, page_type: str, entry_line: str, slug: str
) -> str:
    """
    Insert a new entry into the correct section of index.md.

    For entities, routes into the right sub-section (Researchers,
    Organizations, Models, Datasets, Tools, Benchmarks) based on the
    entity_type prefix in the entry_line summary, e.g. "[researcher]".

    Insertion is alphabetical within the section.
    """
    section_headers = {
        "source": "## Sources",
        "entity": "## Entities",
        "concept": "## Concepts",
        "analysis": "## Analyses",
    }

    # For entities, try to find the right sub-section header
    if page_type == "entity":
        entity_subsection = _detect_entity_subsection(entry_line)
        if entity_subsection:
            return _insert_after_header(content, f"### {entity_subsection}", entry_line)

    return _insert_after_header(content, section_headers[page_type], entry_line)


def _detect_entity_subsection(entry_line: str) -> str | None:
    """
    Check if the entry line has an entity_type prefix like "[researcher]"
    and return the corresponding sub-section header name.
    """
    mapping = {
        "researcher": "Researchers",
        "organization": "Organizations",
        "model": "Models",
        "dataset": "Datasets",
        "tool": "Tools",
        "benchmark": "Benchmarks",
    }
    match = re.search(r"\[(\w+)\]", entry_line)
    if match:
        return mapping.get(match.group(1).lower())
    return None


def _insert_after_header(content: str, header: str, entry_line: str) -> str:
    """
    Insert entry_line into the section that starts with `header`,
    maintaining alphabetical order among existing entries.
    """
    lines = content.split("\n")
    insert_at = None

    in_section = False
    for i, line in enumerate(lines):
        if line.startswith(header):
            in_section = True
            continue
        if in_section:
            # Stop at next ## header (new section)
            if line.startswith("## ") and not line.startswith(header):
                insert_at = i
                break
            # Insert alphabetically among existing entries
            if line.startswith("- [[") and line > entry_line:
                insert_at = i
                break
        if in_section and line.startswith("## ") and insert_at is None:
            insert_at = i
            break

    if insert_at is None:
        # Append to end of file
        lines.append(entry_line)
    else:
        lines.insert(insert_at, entry_line)

    return "\n".join(lines)


def _refresh_index_header(content: str) -> str:
    """
    Update the '_Last updated_' line and total page count in index.md.
    """
    from datetime import date

    today = date.today().isoformat()

    total = sum(
        1
        for line in content.splitlines()
        if line.startswith("- [[") and "~~" not in line
    )

    updated_line = f"_Last updated: {today}. {total} pages total._"
    content = re.sub(
        r"_Last updated:.*?_",
        updated_line,
        content,
        count=1,
    )
    return content
