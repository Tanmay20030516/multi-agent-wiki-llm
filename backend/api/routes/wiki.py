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

import re as _re
import pathlib as _pathlib
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


class TreeNode(BaseModel):
    type: str        # "directory" | "file"
    name: str
    path: str
    children: list["TreeNode"] | None = None


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


@router.get("/tree", response_model=list[TreeNode])
async def get_tree() -> list[TreeNode]:
    """Return a directory tree of all wiki pages as a nested list of nodes."""
    result: list[TreeNode] = []

    for page_type, dir_name in PAGE_TYPE_DIRS.items():
        pages = wm.list_wiki_pages(page_type)
        children = [
            TreeNode(
                type="file",
                name=p.name,
                path=str(p.relative_to(wm.wiki_root)),
            )
            for p in pages
        ]
        result.append(
            TreeNode(type="directory", name=dir_name, path=dir_name, children=children)
        )

    return result


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

    # If the path doesn't exist as-is, search subdirectories for the slug
    if not full_path.exists():
        slug = _pathlib.Path(path).stem
        for subdir in ("sources", "entities", "concepts", "analyses"):
            candidate = wm.wiki_root / subdir / f"{slug}.md"
            if candidate.exists():
                full_path = candidate
                path = f"{subdir}/{slug}.md"
                break

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


_WIKILINK_RE = _re.compile(r"\[\[([^\]]+)\]\]")


@router.get("/graph")
async def get_graph() -> dict:
    """
    Return nodes and edges for a force-directed graph of the wiki.
    Nodes are all wiki pages; edges come from [[wikilink]] references.
    """
    nodes: list[dict] = []
    edges: list[dict] = []
    slug_to_id: dict[str, str] = {}

    for page_type, dir_name in PAGE_TYPE_DIRS.items():
        pages = wm.list_wiki_pages(page_type)
        for p in pages:
            node_id = str(p.relative_to(wm.wiki_root))
            slug = p.stem
            slug_to_id[slug] = node_id
            nodes.append({"id": node_id, "label": slug, "type": page_type})

    # Second pass: parse wikilinks to build edges
    for node in nodes:
        full_path = wm.wiki_root / node["id"]
        try:
            content = full_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for match in _WIKILINK_RE.finditer(content):
            target_slug = match.group(1)
            if target_slug in slug_to_id and slug_to_id[target_slug] != node["id"]:
                edges.append({"source": node["id"], "target": slug_to_id[target_slug]})

    # Deduplicate edges
    seen: set[tuple[str, str]] = set()
    unique_edges: list[dict] = []
    for e in edges:
        key = (min(e["source"], e["target"]), max(e["source"], e["target"]))
        if key not in seen:
            seen.add(key)
            unique_edges.append(e)

    return {"nodes": nodes, "edges": unique_edges}


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
