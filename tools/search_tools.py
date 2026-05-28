"""
tools/search_tools.py

Full-text search across wiki pages, exposed to both agents as a tool.

Phase 1 (current): regex scan across all .md files in wiki/.
  Fast enough for < 300 pages. No index to build or maintain.
  Results ranked by match frequency — most-mentioned pages first.

Phase 2 (future): swap in Whoosh BM25 index for larger wikis.
  The tool signature stays identical — only the implementation changes.
  The switch point is when search_wiki becomes noticeably slow
  (rough guide: > 500 pages or > 300ms response time).

Both agents use this. The query agent calls it when index.md lookup
isn't sufficient — e.g. the user asks about something that isn't a
top-level page title but appears in the body of several pages.
The maintenance agent calls it during lint to find all mentions of
a concept or entity across the wiki.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from core.logger import get_logger
from core.wiki_manager import wm

log = get_logger(__name__)


# Result model
@dataclass(order=True)
class SearchResult:
    # order=True sorts by the first field — we put match_count negative
    # so higher counts sort first (descending) with a plain sort()
    sort_key: int = field(init=False, repr=False)

    slug: str
    path: Path
    match_count: int
    excerpts: list[str]

    def __post_init__(self) -> None:
        self.sort_key = -self.match_count  # descending by match count

    def to_str(self) -> str:
        excerpt_block = "\n".join(f"  …{e}…" for e in self.excerpts)
        return (
            f"[[{self.slug}]] ({self.match_count} match{'es' if self.match_count != 1 else ''})\n"
            f"{excerpt_block}"
        )


# Tool
def search_wiki(
    query: str,
    page_type: str | None = None,
    max_results: int = 8,
) -> str:
    """
    Search wiki pages for a query string and return ranked results.

    Each result includes the page slug, how many times the query
    matched, and short excerpts showing the match in context.
    Results are ranked by match frequency — the most-mentioned page first.

    The search is case-insensitive. Multi-word queries match pages
    that contain ALL words anywhere in the document (AND logic), not
    necessarily adjacent. For phrase matching, wrap in quotes —
    "attention mechanism" will match that exact phrase.

    Args:
        query:       Search terms. Examples:
                       "attention"
                       "sparse mixture of experts"
                       '"key-value cache"'   ← quoted for exact phrase
        page_type:   Optional filter. One of: source, entity, concept, analysis.
                     If omitted, searches all page types.
        max_results: Maximum number of results to return. Default 8.

    Returns:
        Formatted search results string, or a message if nothing found.

    Example output:
        Search: "attention" — 3 results

        [[attention-mechanism]] (12 matches)
          …The attention mechanism computes a weighted sum…
          …Multi-head attention applies this operation…

        [[vaswani-2017-attention]] (5 matches)
          …introduces scaled dot-product attention as the…

        [[transformer-architecture]] (2 matches)
          …relies entirely on attention, dispensing with…
    """
    log.debug("search_wiki: query=%r page_type=%s", query, page_type)

    query = query.strip()
    if not query:
        return "ERROR: Search query cannot be empty."

    if max_results < 1 or max_results > 50:
        return "ERROR: max_results must be between 1 and 50."

    # Determine which pages to search
    pages = _get_pages_to_search(page_type)
    if not pages:
        scope = f" in {page_type}s" if page_type else ""
        return f"No wiki pages found{scope}. The wiki may be empty."

    # Build the matcher from the query string
    matcher = _build_matcher(query)

    # Run the search
    results: list[SearchResult] = []
    for page_path in pages:
        result = _search_page(page_path, matcher)
        if result is not None:
            results.append(result)

    if not results:
        scope = f" in {page_type}s" if page_type else ""
        return (
            f"No results for '{query}'{scope}.\n"
            f"Tip: Try broader terms, check spelling, or use list_files() "
            f"to browse pages directly."
        )

    results.sort()  # sorts by sort_key = -match_count
    results = results[:max_results]

    log.info(
        "search_wiki: '%s' → %d result(s) (searched %d pages)",
        query,
        len(results),
        len(pages),
    )

    header = f'Search: "{query}" — {len(results)} result(s)\n'
    body = "\n\n".join(r.to_str() for r in results)
    return header + "\n" + body


# Internals
def _get_pages_to_search(page_type: str | None) -> list[Path]:
    """Return the list of wiki .md files to search."""
    from core.wiki_manager import PAGE_TYPE_DIRS

    if page_type is not None:
        if page_type not in PAGE_TYPE_DIRS:
            return []
        return wm.list_wiki_pages(page_type)  # type: ignore[arg-type]

    return wm.list_wiki_pages()


@dataclass
class Matcher:
    """Compiled search logic for one query."""

    is_phrase: bool
    pattern: re.Pattern[str]
    words: list[str]


def _build_matcher(query: str) -> Matcher:
    """
    Parse the query string and compile a regex.

    Quoted query  → exact phrase match, case-insensitive
    Unquoted      → all words must appear (AND), case-insensitive,
                    words can be anywhere in the document

    Examples:
      "attention mechanism"  → exact phrase
      attention mechanism    → both words present anywhere
    """
    if query.startswith('"') and query.endswith('"') and len(query) > 2:
        # Exact phrase
        phrase = re.escape(query[1:-1].strip())
        pattern = re.compile(phrase, re.IGNORECASE)
        return Matcher(is_phrase=True, pattern=pattern, words=[query[1:-1].strip()])

    # Multi-word AND: compile each word separately
    words = [w for w in re.split(r"\s+", query) if w]
    # For match counting, use the first word's pattern (or a joined OR)
    joined = "|".join(re.escape(w) for w in words)
    pattern = re.compile(joined, re.IGNORECASE)
    return Matcher(is_phrase=False, pattern=pattern, words=words)


def _search_page(page_path: Path, matcher: Matcher) -> SearchResult | None:
    """
    Search one page. Returns a SearchResult if the page matches, else None.
    For AND queries, all words must appear somewhere in the document.
    """
    try:
        text = page_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None

    text_lower = text.lower()

    # AND check — all words must be present
    if not matcher.is_phrase:
        if not all(w.lower() in text_lower for w in matcher.words):
            return None

    # Count total matches
    matches = list(matcher.pattern.finditer(text))
    if not matches:
        return None

    excerpts = _extract_excerpts(text, matches, max_excerpts=3, context_chars=60)

    return SearchResult(
        slug=page_path.stem,
        path=page_path,
        match_count=len(matches),
        excerpts=excerpts,
    )


def _extract_excerpts(
    text: str,
    matches: list[re.Match[str]],
    max_excerpts: int,
    context_chars: int,
) -> list[str]:
    """
    Pull short excerpts around match positions.
    Tries to find matches spread across the document (not just the first N).
    Cleans up whitespace so excerpts read naturally.
    """
    if not matches:
        return []

    # Pick matches spread across the document
    step = max(1, len(matches) // max_excerpts)
    selected = matches[::step][:max_excerpts]

    excerpts: list[str] = []
    for m in selected:
        start = max(0, m.start() - context_chars)
        end = min(len(text), m.end() + context_chars)
        snippet = text[start:end]
        # Collapse whitespace and newlines to keep excerpts single-line
        snippet = re.sub(r"\s+", " ", snippet).strip()
        excerpts.append(snippet)

    return excerpts
