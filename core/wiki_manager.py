"""
core/wiki_manager.py

Path resolution and filesystem safety layer for the wiki.

This is the ONLY place in the codebase that knows how the wiki directory
is structured. All tools in tools/ import from here — they never construct
paths manually.

Two guarantees this module provides:
  1. Every path it returns is inside data/wiki/ or data/raw/ (never outside)
  2. Every slug resolution is deterministic — one slug maps to one path

Usage:
    from core.wiki_manager import wm

    path = wm.page_path("attention-mechanism")   # resolves to correct subdir
    wm.assert_in_wiki(some_path)                 # raises if path escapes wiki
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Literal

from core.config import settings


# Types
PageType = Literal["source", "entity", "concept", "analysis"]

# Maps page type to subdirectory name
PAGE_TYPE_DIRS: dict[PageType, str] = {
    "source": "sources",
    "entity": "entities",
    "concept": "concepts",
    "analysis": "analyses",
}

# All valid raw source subdirectories
RAW_SUBDIRS = ("articles", "papers", "notes", "assets")


# WikiManager
class WikiManager:
    """
    Path helpers and safety checks for the wiki and raw directories.
    Instantiated once as the module-level `wm` singleton.
    """

    # Core paths
    @property
    def wiki_root(self) -> Path:
        return settings.wiki_path

    @property
    def raw_root(self) -> Path:
        return settings.raw_path

    @property
    def schema(self) -> Path:
        return settings.schema_path

    @property
    def index(self) -> Path:
        return settings.index_path

    @property
    def log(self) -> Path:
        return settings.log_path

    # Subdirectory paths
    def subdir(self, page_type: PageType) -> Path:
        """Return the wiki subdirectory for a given page type."""
        return self.wiki_root / PAGE_TYPE_DIRS[page_type]

    def sources_dir(self) -> Path:
        return self.wiki_root / "sources"

    def entities_dir(self) -> Path:
        return self.wiki_root / "entities"

    def concepts_dir(self) -> Path:
        return self.wiki_root / "concepts"

    def analyses_dir(self) -> Path:
        return self.wiki_root / "analyses"

    def raw_subdir(self, category: str) -> Path:
        """
        Return a raw/ subdirectory path.
        Raises ValueError for unknown categories.
        """
        if category not in RAW_SUBDIRS:
            raise ValueError(
                f"Unknown raw category '{category}'. Valid options: {RAW_SUBDIRS}"
            )
        return self.raw_root / category

    # Slug to path resolution
    def page_path(self, slug: str, page_type: PageType) -> Path:
        """
        Given a slug and page type, return the full path to the .md file.

        Example:
            wm.page_path("attention-mechanism", "concept") to /data/wiki/concepts/attention-mechanism.md
        """
        self._validate_slug(slug)
        return self.subdir(page_type) / f"{slug}.md"

    def resolve_slug(self, slug: str) -> Path | None:
        """
        Search all wiki subdirectories for a file matching this slug.
        Returns the path if found, None if not found.

        This is what the query agent uses when it encounters a [[wikilink]]
        and needs to find the actual file without knowing the page type.
        """
        self._validate_slug(slug)
        for page_type in PAGE_TYPE_DIRS:
            candidate = self.page_path(slug, page_type)
            if candidate.exists():
                return candidate
        return None

    def slug_exists(self, slug: str) -> bool:
        """Return True if any wiki page with this slug exists."""
        return self.resolve_slug(slug) is not None

    def slug_from_path(self, path: Path) -> str:
        """Extract the slug from a wiki page path (filename without extension)."""
        return path.stem

    # Safety checks
    def assert_in_wiki(self, path: Path) -> None:
        """
        Raise PermissionError if path is outside the wiki directory.

        Called by write_tools before every file write to prevent the
        maintenance agent from accidentally writing outside wiki/.
        """
        try:
            path.resolve().relative_to(self.wiki_root.resolve())
        except ValueError:
            raise PermissionError(
                f"Path '{path}' is outside the wiki directory '{self.wiki_root}'. "
                "The maintenance agent may only write within wiki/."
            )

    def assert_in_raw(self, path: Path) -> None:
        """
        Raise PermissionError if path is outside the raw directory.
        Used by read_source() to prevent reading arbitrary filesystem paths.
        """
        try:
            path.resolve().relative_to(self.raw_root.resolve())
        except ValueError:
            raise PermissionError(
                f"Path '{path}' is outside the raw directory '{self.raw_root}'. "
                "read_source() may only read from raw/."
            )

    def assert_not_schema(self, path: Path) -> None:
        """
        Raise PermissionError if path points to schema.md.
        Schema is never modified by the agent — only by the user.
        """
        if path.resolve() == self.schema.resolve():
            raise PermissionError(
                "schema.md cannot be modified by the maintenance agent. "
                "Edit it directly or use the schema editor in the Admin UI."
            )

    # Directory listing helpers
    def list_wiki_pages(self, page_type: PageType | None = None) -> list[Path]:
        """
        List all .md files in the wiki.
        If page_type is given, only list pages of that type.
        Returns paths sorted alphabetically.
        """
        if page_type is not None:
            subdir = self.subdir(page_type)
            if not subdir.exists():
                return []
            return sorted(subdir.glob("*.md"))

        # All page types
        paths: list[Path] = []
        for pt in PAGE_TYPE_DIRS:
            paths.extend(self.list_wiki_pages(pt))
        return sorted(paths)

    def list_raw_files(self, category: str | None = None) -> list[Path]:
        """
        List all files under raw/.
        If category is given (articles/papers/notes/assets), list only that subdir.
        """
        if category is not None:
            subdir = self.raw_subdir(category)
            if not subdir.exists():
                return []
            return sorted(p for p in subdir.iterdir() if p.is_file())

        paths: list[Path] = []
        for cat in RAW_SUBDIRS:
            paths.extend(self.list_raw_files(cat))
        return sorted(paths)

    def page_count(self) -> dict[str, int]:
        """
        Return a count of pages per type, plus a total.
        Useful for the 'pages before to after' report in ingest.
        """
        counts = {pt: len(self.list_wiki_pages(pt)) for pt in PAGE_TYPE_DIRS}
        counts["total"] = sum(counts.values())
        return counts

    # Slug validation
    _SLUG_PATTERN = re.compile(r"^[a-z0-9][a-z0-9\-]*[a-z0-9]$|^[a-z0-9]$")

    def _validate_slug(self, slug: str) -> None:
        """
        Raise ValueError if the slug doesn't follow wiki conventions:
        - lowercase alphanumeric and hyphens only
        - no leading or trailing hyphens
        - no consecutive hyphens

        This catches typos and injection attempts before they reach the filesystem.
        """
        if not slug:
            raise ValueError("Slug cannot be empty.")
        if not self._SLUG_PATTERN.match(slug):
            raise ValueError(
                f"Invalid slug '{slug}'. "
                "Slugs must be lowercase, hyphen-separated, e.g. 'attention-mechanism'."
            )
        if "--" in slug:
            raise ValueError(
                f"Invalid slug '{slug}'. Consecutive hyphens are not allowed."
            )

    def validate_slug(self, slug: str) -> bool:
        """Public version — returns bool instead of raising."""
        try:
            self._validate_slug(slug)
            return True
        except ValueError:
            return False

    # Initialisation check
    def is_initialised(self) -> bool:
        """
        Return True if the wiki directory is properly set up.
        Checks for the three required root files and all four subdirectories.
        """
        required_files = [self.schema, self.index, self.log]
        required_dirs = [self.subdir(pt) for pt in PAGE_TYPE_DIRS]

        return all(f.exists() for f in required_files) and all(
            d.exists() for d in required_dirs
        )

    def ensure_dirs(self) -> None:
        """
        Create all required wiki and raw subdirectories if they don't exist.
        Called by init_wiki.py and at backend startup as a safety measure.
        """
        for page_type in PAGE_TYPE_DIRS:
            self.subdir(page_type).mkdir(parents=True, exist_ok=True)
        for cat in RAW_SUBDIRS:
            (self.raw_root / cat).mkdir(parents=True, exist_ok=True)


# Module-level singleton

# Import this everywhere instead of instantiating WikiManager yourself:
#   from core.wiki_manager import wm
wm = WikiManager()
