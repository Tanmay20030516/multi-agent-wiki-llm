"""
api/routes/wiki.py

Read-only wiki access routes. Used by both UIs to browse wiki content.

GET  /api/wiki/index       — Read index.md
GET  /api/wiki/log         — Read log.md (recent entries)
GET  /api/wiki/tree        — Directory tree of all wiki pages
GET  /api/wiki/page/{path} — Read a specific wiki page
PUT  /api/wiki/schema      — Update schema.md (user-only, not agent)
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.core.wiki_manager import wm, PAGE_TYPE_DIRS
from backend.core.logger import get_logger

log = get_logger(__name__)
router = APIRouter(prefix="/api/wiki", tags=["wiki"])


class PageResponse(BaseModel):
    path: str
    slug: str
    content: str


class TreeEntry(BaseModel):
    slug: str
    path: str


class TreeResponse(BaseModel):
    sources: list[TreeEntry]
    entities: list[TreeEntry]
    concepts: list[TreeEntry]
    analyses: list[TreeEntry]
    total: int


class SchemaUpdateRequest(BaseModel):
    content: str = Field(..., min_length=1)


@router.get("/index")
async def get_index() -> PageResponse:
    """Return the contents of index.md."""
    if not wm.index.exists():
        raise HTTPException(status_code=404, detail="index.md not found.")

    content = wm.index.read_text(encoding="utf-8")
    return PageResponse(path="index.md", slug="index", content=content)


@router.get("/log")
async def get_log() -> PageResponse:
    """Return the contents of log.md."""
    if not wm.log.exists():
        raise HTTPException(status_code=404, detail="log.md not found.")

    content = wm.log.read_text(encoding="utf-8")
    return PageResponse(path="log.md", slug="log", content=content)


@router.get("/schema")
async def get_schema() -> PageResponse:
    """Return the contents of schema.md."""
    if not wm.schema.exists():
        raise HTTPException(status_code=404, detail="schema.md not found.")

    content = wm.schema.read_text(encoding="utf-8")
    return PageResponse(path="schema.md", slug="schema", content=content)


@router.get("/tree", response_model=TreeResponse)
async def get_tree() -> TreeResponse:
    """Return a directory tree of all wiki pages grouped by type."""
    tree: dict[str, list[TreeEntry]] = {}

    for page_type, dir_name in PAGE_TYPE_DIRS.items():
        pages = wm.list_wiki_pages(page_type)
        tree[dir_name] = [
            TreeEntry(
                slug=p.stem,
                path=str(p.relative_to(wm.wiki_root)),
            )
            for p in pages
        ]

    return TreeResponse(
        sources=tree.get("sources", []),
        entities=tree.get("entities", []),
        concepts=tree.get("concepts", []),
        analyses=tree.get("analyses", []),
        total=sum(len(v) for v in tree.values()),
    )


@router.get("/page/{path:path}", response_model=PageResponse)
async def get_page(path: str) -> PageResponse:
    """
    Read a specific wiki page by its path relative to wiki root.
    Examples: /api/wiki/page/concepts/attention-mechanism.md
              /api/wiki/page/entities/openai.md
    """
    if not path.endswith(".md"):
        path = path + ".md"

    full_path = wm.wiki_root / path

    try:
        wm.assert_in_wiki(full_path)
    except PermissionError:
        raise HTTPException(
            status_code=403, detail="Path is outside the wiki directory."
        )

    if not full_path.exists():
        raise HTTPException(status_code=404, detail=f"Page not found: {path}")

    content = full_path.read_text(encoding="utf-8")
    return PageResponse(
        path=path,
        slug=full_path.stem,
        content=content,
    )


@router.put("/schema")
async def update_schema(req: SchemaUpdateRequest) -> dict:
    """
    Update schema.md. This is a user action, not an agent action.
    The maintenance agent is blocked from modifying schema.md via
    wm.assert_not_schema() — only this endpoint can do it.
    """
    if not wm.schema.exists():
        raise HTTPException(status_code=404, detail="schema.md not found.")

    wm.schema.write_text(req.content, encoding="utf-8")
    log.info("schema.md updated by user (%d chars)", len(req.content))

    return {"message": "schema.md updated.", "size": len(req.content)}
