"""
core/chat_store.py

SQLite-backed storage for chat threads and messages.
Database file: data/chats.db (auto-created alongside wiki data).

Schema
------
threads  : id, title, created_at, updated_at
messages : id, thread_id, role, content, is_error, created_at
"""

from __future__ import annotations

import asyncio
import sqlite3
import time
from pathlib import Path
from typing import Any

from backend.core.config import get_settings

_DB_PATH: Path | None = None


def _db_path() -> Path:
    global _DB_PATH
    if _DB_PATH is None:
        settings = get_settings()
        _DB_PATH = Path(settings.data_path) / "chats.db"
        _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return _DB_PATH


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(_db_path(), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")   # safe concurrent reads
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _init_db(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS threads (
            id         TEXT    PRIMARY KEY,
            title      TEXT    NOT NULL DEFAULT 'New thread',
            created_at INTEGER NOT NULL,
            updated_at INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS messages (
            id         TEXT    NOT NULL,
            thread_id  TEXT    NOT NULL REFERENCES threads(id) ON DELETE CASCADE,
            role       TEXT    NOT NULL,
            content    TEXT    NOT NULL DEFAULT '',
            is_error   INTEGER NOT NULL DEFAULT 0,
            created_at INTEGER NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_messages_thread
            ON messages(thread_id, created_at);
    """)
    conn.commit()


# Module-level connection (re-used across requests in the same process)
_conn: sqlite3.Connection | None = None


def get_conn() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        _conn = _connect()
        _init_db(_conn)
    return _conn


# ── helpers ────────────────────────────────────────────────────────────────

def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return dict(row)


# ── sync implementations (run in thread pool via asyncio.to_thread) ────────

def _list_threads() -> list[dict]:
    conn = get_conn()
    rows = conn.execute("""
        SELECT t.id, t.title, t.created_at, t.updated_at,
               COUNT(m.id) AS message_count
        FROM threads t
        LEFT JOIN messages m ON m.thread_id = t.id
        GROUP BY t.id
        ORDER BY t.updated_at DESC
    """).fetchall()
    return [_row_to_dict(r) for r in rows]


def _create_thread(thread_id: str, title: str = "New thread") -> dict:
    now = int(time.time() * 1000)
    conn = get_conn()
    conn.execute(
        "INSERT INTO threads (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
        (thread_id, title, now, now),
    )
    conn.commit()
    return {"id": thread_id, "title": title, "created_at": now, "updated_at": now, "message_count": 0}


def _get_thread(thread_id: str) -> dict | None:
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM threads WHERE id = ?", (thread_id,)
    ).fetchone()
    if not row:
        return None
    thread = _row_to_dict(row)
    msgs = conn.execute(
        "SELECT * FROM messages WHERE thread_id = ? ORDER BY created_at",
        (thread_id,),
    ).fetchall()
    thread["messages"] = [_row_to_dict(m) for m in msgs]
    return thread


def _update_thread_title(thread_id: str, title: str) -> bool:
    now = int(time.time() * 1000)
    conn = get_conn()
    cur = conn.execute(
        "UPDATE threads SET title = ?, updated_at = ? WHERE id = ?",
        (title, now, thread_id),
    )
    conn.commit()
    return cur.rowcount > 0


def _delete_thread(thread_id: str) -> bool:
    conn = get_conn()
    cur = conn.execute("DELETE FROM threads WHERE id = ?", (thread_id,))
    conn.commit()
    return cur.rowcount > 0


def _replace_messages(thread_id: str, messages: list[dict]) -> None:
    """Replace all messages for a thread in one transaction."""
    now = int(time.time() * 1000)
    conn = get_conn()
    with conn:
        conn.execute("DELETE FROM messages WHERE thread_id = ?", (thread_id,))
        for i, m in enumerate(messages):
            conn.execute(
                """INSERT INTO messages (id, thread_id, role, content, is_error, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    m.get("id", f"{thread_id}_{i}"),
                    thread_id,
                    m.get("role", "user"),
                    m.get("content", ""),
                    1 if m.get("isError") else 0,
                    m.get("created_at", now + i),
                ),
            )
        conn.execute(
            "UPDATE threads SET updated_at = ? WHERE id = ?", (now, thread_id)
        )


# ── async public API ───────────────────────────────────────────────────────

async def list_threads() -> list[dict]:
    return await asyncio.to_thread(_list_threads)

async def create_thread(thread_id: str, title: str = "New thread") -> dict:
    return await asyncio.to_thread(_create_thread, thread_id, title)

async def get_thread(thread_id: str) -> dict | None:
    return await asyncio.to_thread(_get_thread, thread_id)

async def update_thread_title(thread_id: str, title: str) -> bool:
    return await asyncio.to_thread(_update_thread_title, thread_id, title)

async def delete_thread(thread_id: str) -> bool:
    return await asyncio.to_thread(_delete_thread, thread_id)

async def replace_messages(thread_id: str, messages: list[dict]) -> None:
    await asyncio.to_thread(_replace_messages, thread_id, messages)
