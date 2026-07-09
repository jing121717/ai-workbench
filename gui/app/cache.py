"""
AI Workbench · 桌面端本地 SQLite 缓存
离线时保存会话历史、设置、API 配置
"""
import json
import sqlite3
import threading
from pathlib import Path


class LocalCache:
    """轻量级 SQLite 本地缓存，线程安全"""

    def __init__(self, db_path: str | None = None) -> None:
        self._db_path = db_path or str(Path(__file__).parent.parent / "cache.db")
        self._lock = threading.Lock()
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self._db_path, check_same_thread=False)

    def _init_db(self) -> None:
        with self._lock:
            conn = self._conn()
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY, value TEXT
                );
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER, role TEXT, content TEXT,
                    sources TEXT, created_at TEXT
                );
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY, title TEXT,
                    created_at TEXT, updated_at TEXT
                );
                CREATE TABLE IF NOT EXISTS code_projects (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    local_path TEXT,
                    branch TEXT,
                    last_synced_at TEXT
                );
                CREATE TABLE IF NOT EXISTS snippets (
                    id INTEGER PRIMARY KEY,
                    title TEXT,
                    content TEXT,
                    language TEXT,
                    category TEXT,
                    updated_at TEXT
                );
            """)
            conn.commit()
            conn.close()

    # ── Settings ──────────────────────────────────────────────────────────────
    def set_setting(self, key: str, value: str) -> None:
        with self._lock:
            conn = self._conn()
            conn.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, value),
            )
            conn.commit()
            conn.close()

    def get_setting(self, key: str, default: str = "") -> str:
        with self._lock:
            conn = self._conn()
            row = conn.execute(
                "SELECT value FROM settings WHERE key = ?", (key,)
            ).fetchone()
            conn.close()
            return row[0] if row else default

    # ── Sessions ──────────────────────────────────────────────────────────────
    def save_session(self, session_id: int, title: str, created_at: str, updated_at: str) -> None:
        with self._lock:
            conn = self._conn()
            conn.execute(
                "INSERT OR REPLACE INTO sessions (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (session_id, title, created_at, updated_at),
            )
            conn.commit()
            conn.close()

    def get_sessions(self) -> list[dict]:
        with self._lock:
            conn = self._conn()
            rows = conn.execute("SELECT id, title, created_at, updated_at FROM sessions ORDER BY id DESC").fetchall()
            conn.close()
            return [{"id": r[0], "title": r[1], "created_at": r[2], "updated_at": r[3]} for r in rows]

    # ── Messages ────────────────────────────────────────────────────────────────
    def save_message(self, session_id: int, role: str, content: str, sources: str = "[]", created_at: str = "") -> None:
        import datetime
        with self._lock:
            conn = self._conn()
            conn.execute(
                "INSERT INTO messages (session_id, role, content, sources, created_at) VALUES (?, ?, ?, ?, ?)",
                (session_id, role, content, sources, created_at or datetime.datetime.now().isoformat()),
            )
            conn.commit()
            conn.close()

    def get_messages(self, session_id: int) -> list[dict]:
        with self._lock:
            conn = self._conn()
            rows = conn.execute(
                "SELECT id, session_id, role, content, sources, created_at FROM messages WHERE session_id = ? ORDER BY id ASC",
                (session_id,),
            ).fetchall()
            conn.close()
            return [{"id": r[0], "session_id": r[1], "role": r[2], "content": r[3], "sources": r[4], "created_at": r[5]} for r in rows]

    def clear_messages(self, session_id: int) -> None:
        with self._lock:
            conn = self._conn()
            conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
            conn.commit()
            conn.close()

    # ── Code Projects ────────────────────────────────────────────────────────
    def save_code_projects(self, projects: list[dict]) -> None:
        with self._lock:
            conn = self._conn()
            for project in projects:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO code_projects (id, name, local_path, branch, last_synced_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        project.get("id"),
                        project.get("name", ""),
                        project.get("local_path", ""),
                        project.get("git_current_branch", ""),
                        project.get("last_synced_at", ""),
                    ),
                )
            conn.commit()
            conn.close()

    def get_code_projects(self) -> list[dict]:
        with self._lock:
            conn = self._conn()
            rows = conn.execute(
                "SELECT id, name, local_path, branch, last_synced_at FROM code_projects ORDER BY id DESC"
            ).fetchall()
            conn.close()
            return [
                {"id": r[0], "name": r[1], "local_path": r[2], "git_current_branch": r[3], "last_synced_at": r[4]}
                for r in rows
            ]

    # ── Snippets ─────────────────────────────────────────────────────────────
    def save_snippets(self, snippets: list[dict]) -> None:
        with self._lock:
            conn = self._conn()
            for snippet in snippets:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO snippets (id, title, content, language, category, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        snippet.get("id"),
                        snippet.get("title", ""),
                        snippet.get("content", ""),
                        snippet.get("language", ""),
                        snippet.get("category", ""),
                        snippet.get("updated_at", ""),
                    ),
                )
            conn.commit()
            conn.close()

    def get_snippets(self) -> list[dict]:
        with self._lock:
            conn = self._conn()
            rows = conn.execute(
                "SELECT id, title, content, language, category, updated_at FROM snippets ORDER BY id DESC"
            ).fetchall()
            conn.close()
            return [
                {
                    "id": r[0],
                    "title": r[1],
                    "content": r[2],
                    "language": r[3],
                    "category": r[4],
                    "updated_at": r[5],
                }
                for r in rows
            ]
