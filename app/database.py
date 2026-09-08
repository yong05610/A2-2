"""SQLite database helpers."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from app.config import load_config, resolve_project_path


def _utc_now() -> str:
    """Return a stable timestamp string for database records."""
    return datetime.utcnow().isoformat(timespec="seconds")


def get_db_path() -> Path:
    """Read and resolve the SQLite database path from config.json."""
    config = load_config()
    return resolve_project_path(config["database"]["path"])


def get_connection() -> sqlite3.Connection:
    """Open a SQLite connection, creating the parent directory if needed."""
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db() -> None:
    """Create required tables if they do not already exist."""
    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS raw_news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                content TEXT,
                source TEXT,
                method TEXT NOT NULL,
                category TEXT,
                published_at TEXT,
                collected_at TEXT NOT NULL,
                raw_payload TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS clean_news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                raw_news_id INTEGER,
                title TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                content TEXT,
                source TEXT,
                category TEXT,
                published_at TEXT,
                content_length INTEGER DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'cleaned',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (raw_news_id) REFERENCES raw_news (id)
            );

            CREATE TABLE IF NOT EXISTS summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                clean_news_id INTEGER NOT NULL UNIQUE,
                summary TEXT NOT NULL,
                model TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (clean_news_id) REFERENCES clean_news (id)
            );

            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_from TEXT,
                date_to TEXT,
                category TEXT,
                news_count INTEGER DEFAULT 0,
                result TEXT NOT NULL,
                model TEXT,
                created_at TEXT NOT NULL
            );
            """
        )


def _serialize_payload(payload: Any) -> str | None:
    """Serialize raw payload data for SQLite storage."""
    if payload is None:
        return None
    if isinstance(payload, str):
        return payload
    return json.dumps(payload, ensure_ascii=False)


def save_raw_news(news: dict[str, Any], duplicate_policy: str = "skip") -> int | None:
    """Save a raw news item and return its row ID."""
    now = _utc_now()
    sql = (
        """
        INSERT INTO raw_news (
            title, url, content, source, method, category, published_at,
            collected_at, raw_payload, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
    )
    values = (
        news["title"],
        news["url"],
        news.get("content"),
        news.get("source"),
        news.get("method", "unknown"),
        news.get("category"),
        news.get("published_at"),
        news.get("collected_at", now),
        _serialize_payload(news.get("raw_payload")),
        now,
        now,
    )

    with get_connection() as connection:
        try:
            cursor = connection.execute(sql, values)
            return int(cursor.lastrowid)
        except sqlite3.IntegrityError:
            if duplicate_policy != "upsert":
                return None
            connection.execute(
                """
                UPDATE raw_news
                SET title = ?, content = ?, source = ?, method = ?, category = ?,
                    published_at = ?, collected_at = ?, raw_payload = ?, updated_at = ?
                WHERE url = ?
                """,
                (
                    news["title"],
                    news.get("content"),
                    news.get("source"),
                    news.get("method", "unknown"),
                    news.get("category"),
                    news.get("published_at"),
                    news.get("collected_at", now),
                    _serialize_payload(news.get("raw_payload")),
                    now,
                    news["url"],
                ),
            )
            row = connection.execute("SELECT id FROM raw_news WHERE url = ?", (news["url"],)).fetchone()
            return int(row["id"]) if row else None


def save_clean_news(news: dict[str, Any], duplicate_policy: str = "skip") -> int | None:
    """Save a cleaned news item and return its row ID."""
    now = _utc_now()
    content = news.get("content") or ""
    values = (
        news.get("raw_news_id"),
        news["title"],
        news["url"],
        content,
        news.get("source"),
        news.get("category"),
        news.get("published_at"),
        news.get("content_length", len(content)),
        news.get("status", "cleaned"),
        now,
        now,
    )

    with get_connection() as connection:
        try:
            cursor = connection.execute(
                """
                INSERT INTO clean_news (
                    raw_news_id, title, url, content, source, category,
                    published_at, content_length, status, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                values,
            )
            return int(cursor.lastrowid)
        except sqlite3.IntegrityError:
            if duplicate_policy != "upsert":
                return None
            connection.execute(
                """
                UPDATE clean_news
                SET raw_news_id = ?, title = ?, content = ?, source = ?, category = ?,
                    published_at = ?, content_length = ?, status = ?, updated_at = ?
                WHERE url = ?
                """,
                (
                    news.get("raw_news_id"),
                    news["title"],
                    content,
                    news.get("source"),
                    news.get("category"),
                    news.get("published_at"),
                    news.get("content_length", len(content)),
                    news.get("status", "cleaned"),
                    now,
                    news["url"],
                ),
            )
            row = connection.execute("SELECT id FROM clean_news WHERE url = ?", (news["url"],)).fetchone()
            return int(row["id"]) if row else None


def save_summary(clean_news_id: int, summary: str, model: str | None = None) -> int:
    """Save or replace a summary for a cleaned news item."""
    now = _utc_now()
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO summaries (clean_news_id, summary, model, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(clean_news_id) DO UPDATE SET
                summary = excluded.summary,
                model = excluded.model,
                updated_at = excluded.updated_at
            """,
            (clean_news_id, summary, model, now, now),
        )
        row = connection.execute("SELECT id FROM summaries WHERE clean_news_id = ?", (clean_news_id,)).fetchone()
        return int(row["id"])


def save_analysis(
    result: str,
    date_from: str | None = None,
    date_to: str | None = None,
    category: str | None = None,
    news_count: int = 0,
    model: str | None = None,
) -> int:
    """Save an AI analysis result and return its row ID."""
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO analyses (date_from, date_to, category, news_count, result, model, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (date_from, date_to, category, news_count, result, model, _utc_now()),
        )
        return int(cursor.lastrowid)


def get_news_by_id(news_id: int) -> dict[str, Any] | None:
    """Return one cleaned news item with its summary, if available."""
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT clean_news.*, summaries.summary
            FROM clean_news
            LEFT JOIN summaries ON summaries.clean_news_id = clean_news.id
            WHERE clean_news.id = ?
            """,
            (news_id,),
        ).fetchone()
    return dict(row) if row else None


def list_news(
    status: str | None = None,
    category: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    keyword: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """Return cleaned news rows using optional filters."""
    where_clauses: list[str] = []
    values: list[Any] = []

    if status and status != "all":
        where_clauses.append("clean_news.status = ?")
        values.append(status)
    if category:
        where_clauses.append("clean_news.category = ?")
        values.append(category)
    if date_from:
        where_clauses.append("clean_news.published_at >= ?")
        values.append(date_from)
    if date_to:
        where_clauses.append("clean_news.published_at <= ?")
        values.append(date_to)
    if keyword:
        where_clauses.append("(clean_news.title LIKE ? OR clean_news.content LIKE ?)")
        keyword_value = f"%{keyword}%"
        values.extend([keyword_value, keyword_value])

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    values.extend([limit, offset])

    with get_connection() as connection:
        rows = connection.execute(
            f"""
            SELECT clean_news.*, summaries.summary
            FROM clean_news
            LEFT JOIN summaries ON summaries.clean_news_id = clean_news.id
            {where_sql}
            ORDER BY clean_news.published_at DESC, clean_news.id DESC
            LIMIT ? OFFSET ?
            """,
            values,
        ).fetchall()
    return [dict(row) for row in rows]
