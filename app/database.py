"""SQLite database helpers."""

from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from app.config import load_config, resolve_project_path


logger = logging.getLogger(__name__)


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


def _get_columns(connection: sqlite3.Connection, table_name: str) -> set[str]:
    rows = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    return {row["name"] for row in rows}


def _add_column_if_missing(
    connection: sqlite3.Connection,
    table_name: str,
    column_name: str,
    column_definition: str,
) -> None:
    columns = _get_columns(connection, table_name)
    if column_name not in columns:
        connection.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}")


def migrate_db() -> None:
    """Apply additive migrations without deleting existing data."""
    with get_connection() as connection:
        _add_column_if_missing(connection, "summaries", "prompt_version", "TEXT")
        _add_column_if_missing(connection, "summaries", "status", "TEXT DEFAULT 'completed'")
        _add_column_if_missing(connection, "summaries", "error_message", "TEXT")


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
                prompt_version TEXT,
                status TEXT DEFAULT 'completed',
                error_message TEXT,
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
    migrate_db()


def _serialize_payload(payload: Any) -> str | None:
    """Serialize raw payload data for SQLite storage."""
    if payload is None:
        return None
    if isinstance(payload, str):
        return payload
    return json.dumps(payload, ensure_ascii=False)


def _prepare_raw_news(news: dict[str, Any]) -> dict[str, Any]:
    """Ensure raw news has non-empty content before database writes."""
    prepared = dict(news)
    title = str(prepared.get("title") or "").strip()
    content = str(prepared.get("content") or "").strip()

    if not content:
        content = title
        logger.warning("Raw news content fallback applied: url=%s", prepared.get("url"))

    prepared["content"] = content

    raw_payload = prepared.get("raw_payload")
    if isinstance(raw_payload, dict):
        raw_payload = dict(raw_payload)
        if not str(raw_payload.get("raw_content") or "").strip():
            raw_payload["raw_content"] = content
        if not str(raw_payload.get("raw_summary") or "").strip():
            raw_payload["raw_summary"] = content
        prepared["raw_payload"] = raw_payload

    return prepared


def save_raw_news(news: dict[str, Any], duplicate_policy: str = "skip") -> int | None:
    """Save a raw news item and return its row ID."""
    news = _prepare_raw_news(news)
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


def fill_empty_raw_content_with_title() -> int:
    """Backfill old raw rows that have empty content using their title."""
    now = _utc_now()
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, url
            FROM raw_news
            WHERE content IS NULL OR trim(content) = ''
            """
        ).fetchall()

        for row in rows:
            logger.warning("Existing raw news content fallback applied: url=%s", row["url"])

        connection.execute(
            """
            UPDATE raw_news
            SET content = title,
                updated_at = ?
            WHERE content IS NULL OR trim(content) = ''
            """,
            (now,),
        )
        return len(rows)


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


def save_summary(
    clean_news_id: int,
    summary: str,
    model: str | None = None,
    prompt_version: str | None = None,
    status: str = "completed",
    error_message: str | None = None,
) -> int:
    """Save or replace a summary for a cleaned news item."""
    now = _utc_now()
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO summaries (
                clean_news_id, summary, model, prompt_version, status,
                error_message, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(clean_news_id) DO UPDATE SET
                summary = excluded.summary,
                model = excluded.model,
                prompt_version = excluded.prompt_version,
                status = excluded.status,
                error_message = excluded.error_message,
                updated_at = excluded.updated_at
            """,
            (clean_news_id, summary, model, prompt_version, status, error_message, now, now),
        )
        row = connection.execute("SELECT id FROM summaries WHERE clean_news_id = ?", (clean_news_id,)).fetchone()
        return int(row["id"])


def update_clean_news_status(clean_news_id: int, status: str) -> None:
    """Update clean_news processing status."""
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE clean_news
            SET status = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (status, _utc_now(), clean_news_id),
        )


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


def get_news_for_analysis(
    date_from: str | None = None,
    date_to: str | None = None,
    category: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    """Return clean news rows joined with summaries for AI analysis."""
    where_clauses: list[str] = []
    values: list[Any] = []

    if date_from:
        where_clauses.append("clean_news.published_at >= ?")
        values.append(date_from)
    if date_to:
        where_clauses.append("clean_news.published_at <= ?")
        values.append(date_to)
    if category:
        where_clauses.append("clean_news.category = ?")
        values.append(category)

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    limit_sql = ""
    if limit is not None:
        limit_sql = "LIMIT ?"
        values.append(limit)

    with get_connection() as connection:
        rows = connection.execute(
            f"""
            SELECT
                clean_news.id,
                clean_news.title,
                clean_news.content,
                clean_news.category,
                clean_news.published_at,
                summaries.summary
            FROM clean_news
            LEFT JOIN summaries ON summaries.clean_news_id = clean_news.id
            {where_sql}
            ORDER BY clean_news.published_at DESC, clean_news.id DESC
            {limit_sql}
            """,
            values,
        ).fetchall()
    return [dict(row) for row in rows]


def get_category_counts() -> list[dict[str, Any]]:
    """Return clean news counts grouped by category."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT COALESCE(NULLIF(trim(category), ''), '기타') AS category,
                   COUNT(*) AS news_count
            FROM clean_news
            GROUP BY COALESCE(NULLIF(trim(category), ''), '기타')
            ORDER BY news_count DESC, category ASC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def get_source_counts(limit: int | None = None) -> list[dict[str, Any]]:
    """Return clean news counts grouped by source."""
    values: list[Any] = []
    limit_sql = ""
    if limit is not None:
        limit_sql = "LIMIT ?"
        values.append(limit)

    with get_connection() as connection:
        rows = connection.execute(
            f"""
            SELECT COALESCE(NULLIF(trim(source), ''), 'unknown') AS source,
                   COUNT(*) AS news_count
            FROM clean_news
            GROUP BY COALESCE(NULLIF(trim(source), ''), 'unknown')
            ORDER BY news_count DESC, source ASC
            {limit_sql}
            """,
            values,
        ).fetchall()
    return [dict(row) for row in rows]


def get_report_metrics() -> dict[str, Any]:
    """Return aggregate metrics for reports."""
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM clean_news) AS total_news,
                (SELECT COUNT(*) FROM summaries WHERE status = 'completed') AS summarized_news,
                (SELECT AVG(content_length) FROM clean_news) AS average_content_length
            """
        ).fetchone()

    metrics = dict(row)
    total_news = int(metrics["total_news"] or 0)
    summarized_news = int(metrics["summarized_news"] or 0)
    metrics["total_news"] = total_news
    metrics["summarized_news"] = summarized_news
    metrics["summary_rate"] = (summarized_news / total_news * 100) if total_news else 0.0
    metrics["average_content_length"] = float(metrics["average_content_length"] or 0)
    return metrics


def get_latest_analysis() -> dict[str, Any] | None:
    """Return the latest AI analysis result."""
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM analyses
            ORDER BY created_at DESC, id DESC
            LIMIT 1
            """
        ).fetchone()
    return dict(row) if row else None


def get_daily_counts() -> list[dict[str, Any]]:
    """Return daily news counts using clean published_at or raw collected_at."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT substr(COALESCE(clean_news.published_at, raw_news.collected_at, clean_news.created_at), 1, 10) AS news_date,
                   COUNT(*) AS news_count
            FROM clean_news
            LEFT JOIN raw_news ON raw_news.id = clean_news.raw_news_id
            GROUP BY substr(COALESCE(clean_news.published_at, raw_news.collected_at, clean_news.created_at), 1, 10)
            ORDER BY news_date ASC
            """
        ).fetchall()
    return [dict(row) for row in rows if row["news_date"]]


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


def get_news_detail(news_id: int) -> dict[str, Any] | None:
    """Return one cleaned news item with summary text for the show command."""
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                clean_news.id,
                clean_news.title,
                clean_news.url,
                clean_news.source,
                clean_news.category,
                clean_news.published_at,
                clean_news.status,
                clean_news.content_length,
                clean_news.content,
                summaries.summary AS summary_text
            FROM clean_news
            LEFT JOIN summaries ON summaries.clean_news_id = clean_news.id
            WHERE clean_news.id = ?
            """,
            (news_id,),
        ).fetchone()
    return dict(row) if row else None


def list_raw_news(limit: int | None = None) -> list[dict[str, Any]]:
    """Return raw news rows for cleaning."""
    values: list[Any] = []
    limit_sql = ""
    if limit is not None:
        limit_sql = "LIMIT ?"
        values.append(limit)

    with get_connection() as connection:
        rows = connection.execute(
            f"""
            SELECT *
            FROM raw_news
            ORDER BY id ASC
            {limit_sql}
            """,
            values,
        ).fetchall()
    return [dict(row) for row in rows]


def clean_news_exists_by_url(url: str) -> bool:
    """Return whether a cleaned news row already exists for the URL."""
    with get_connection() as connection:
        row = connection.execute("SELECT 1 FROM clean_news WHERE url = ?", (url,)).fetchone()
    return row is not None


def get_clean_news_for_summary(
    news_id: int | None = None,
    include_summarized: bool = False,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    """Return clean news rows selected for summarization."""
    where_clauses: list[str] = []
    values: list[Any] = []

    if news_id is not None:
        where_clauses.append("clean_news.id = ?")
        values.append(news_id)
    elif not include_summarized:
        where_clauses.append("summaries.id IS NULL")
        where_clauses.append("clean_news.status != 'skipped_short_content'")

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    limit_sql = ""
    if limit is not None:
        limit_sql = "LIMIT ?"
        values.append(limit)

    with get_connection() as connection:
        rows = connection.execute(
            f"""
            SELECT
                clean_news.id,
                clean_news.title,
                clean_news.url,
                clean_news.content,
                clean_news.content_length,
                clean_news.status,
                summaries.id AS summary_id
            FROM clean_news
            LEFT JOIN summaries ON summaries.clean_news_id = clean_news.id
            {where_sql}
            ORDER BY clean_news.id ASC
            {limit_sql}
            """,
            values,
        ).fetchall()
    return [dict(row) for row in rows]


def _build_list_news_filters(
    status: str | None = None,
    category: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    keyword: str | None = None,
) -> tuple[str, list[Any]]:
    """Build safe WHERE SQL and bound values for list queries."""
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
        where_clauses.append(
            "(clean_news.title LIKE ? OR clean_news.content LIKE ? OR summaries.summary LIKE ?)"
        )
        keyword_value = f"%{keyword}%"
        values.extend([keyword_value, keyword_value, keyword_value])

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    return where_sql, values


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
    where_sql, values = _build_list_news_filters(
        status=status,
        category=category,
        date_from=date_from,
        date_to=date_to,
        keyword=keyword,
    )
    values.extend([limit, offset])

    with get_connection() as connection:
        rows = connection.execute(
            f"""
            SELECT clean_news.*,
                   summaries.summary,
                   CASE WHEN summaries.id IS NULL THEN 0 ELSE 1 END AS summarized
            FROM clean_news
            LEFT JOIN summaries ON summaries.clean_news_id = clean_news.id
            {where_sql}
            ORDER BY clean_news.published_at DESC, clean_news.id DESC
            LIMIT ? OFFSET ?
            """,
            values,
        ).fetchall()
    return [dict(row) for row in rows]


def count_news(
    status: str | None = None,
    category: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    keyword: str | None = None,
) -> int:
    """Return the number of cleaned news rows matching list filters."""
    where_sql, values = _build_list_news_filters(
        status=status,
        category=category,
        date_from=date_from,
        date_to=date_to,
        keyword=keyword,
    )
    with get_connection() as connection:
        row = connection.execute(
            f"""
            SELECT COUNT(*) AS news_count
            FROM clean_news
            LEFT JOIN summaries ON summaries.clean_news_id = clean_news.id
            {where_sql}
            """,
            values,
        ).fetchone()
    return int(row["news_count"] or 0)


def get_export_rows(
    table_name: str,
    status: str | None = None,
    category: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    summarized_only: bool = False,
) -> list[dict[str, Any]]:
    """Return rows from an allowed table for file export."""
    allowed_tables = {"clean_news", "summaries", "analyses"}
    if table_name not in allowed_tables:
        raise ValueError(f"Unsupported export table: {table_name}")

    where_clauses: list[str] = []
    values: list[Any] = []

    if table_name == "clean_news":
        if summarized_only or status == "summarized":
            where_clauses.append("summaries.id IS NOT NULL")
        elif status and status != "all":
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
    elif table_name == "summaries":
        if status and status != "all":
            where_clauses.append("status = ?")
            values.append(status)
        if date_from:
            where_clauses.append("created_at >= ?")
            values.append(date_from)
        if date_to:
            where_clauses.append("created_at <= ?")
            values.append(date_to)
    elif table_name == "analyses":
        if category:
            where_clauses.append("category = ?")
            values.append(category)
        if date_from:
            where_clauses.append("created_at >= ?")
            values.append(date_from)
        if date_to:
            where_clauses.append("created_at <= ?")
            values.append(date_to)

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    if table_name == "clean_news":
        sql = f"""
            SELECT
                clean_news.*,
                summaries.summary AS summary,
                summaries.model AS summary_model,
                summaries.status AS summary_status,
                summaries.created_at AS summary_created_at,
                summaries.updated_at AS summary_updated_at
            FROM clean_news
            LEFT JOIN summaries ON summaries.clean_news_id = clean_news.id
            {where_sql}
            ORDER BY clean_news.id ASC
            """
    else:
        sql = f"""
            SELECT *
            FROM {table_name}
            {where_sql}
            ORDER BY id ASC
            """

    with get_connection() as connection:
        rows = connection.execute(sql, values).fetchall()
    return [dict(row) for row in rows]
