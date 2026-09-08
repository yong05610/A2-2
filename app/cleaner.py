"""Raw news cleaning logic."""

from __future__ import annotations

import html
import re
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from app.database import clean_news_exists_by_url, list_raw_news, save_clean_news
from app.logger import get_logger


logger = get_logger(__name__)


def _normalize_text(value: Any) -> str:
    """Remove HTML tags and normalize whitespace."""
    if value is None:
        return ""
    text = html.unescape(str(value))
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _normalize_url(value: Any) -> str:
    """Normalize URL text while preserving query strings."""
    url = _normalize_text(value)
    if not url:
        return ""

    parsed = urlsplit(url)
    if not parsed.scheme or not parsed.netloc:
        return url

    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path or ""
    return urlunsplit((scheme, netloc, path, parsed.query, ""))


def _normalize_date(value: Any) -> str | None:
    """Normalize common date strings to ISO-8601 text."""
    if not value:
        return None

    text = _normalize_text(value)
    if not text:
        return None

    try:
        parsed = parsedate_to_datetime(text)
        return parsed.isoformat()
    except (TypeError, ValueError):
        pass

    for date_format in ("%Y-%m-%d", "%Y.%m.%d", "%Y/%m/%d", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(text, date_format).isoformat()
        except ValueError:
            continue

    try:
        return datetime.fromisoformat(text).isoformat()
    except ValueError:
        logger.warning("Could not normalize published_at value: %s", text)
        return text


def _clean_raw_news(raw_news: dict[str, Any]) -> dict[str, Any] | None:
    title = _normalize_text(raw_news.get("title"))
    url = _normalize_url(raw_news.get("url"))
    content = _normalize_text(raw_news.get("content"))

    if not title or not url:
        logger.warning("Raw news skipped because required fields are missing: id=%s", raw_news.get("id"))
        return None

    category = _normalize_text(raw_news.get("category")) or "기타"

    return {
        "raw_news_id": raw_news["id"],
        "title": title,
        "url": url,
        "content": content,
        "source": _normalize_text(raw_news.get("source")) or None,
        "category": category,
        "published_at": _normalize_date(raw_news.get("published_at")),
        "content_length": len(content),
        "status": "cleaned",
    }


def clean_raw_news(policy: str = "skip", limit: int | None = None) -> dict[str, int]:
    """Clean raw_news rows and save them into clean_news."""
    logger.info("News cleaning started: policy=%s, limit=%s", policy, limit)

    inserted = 0
    updated = 0
    skipped = 0
    failed = 0

    try:
        raw_items = list_raw_news(limit=limit)
    except Exception as error:
        logger.error("Failed to load raw news: %s", error)
        return {"inserted": 0, "updated": 0, "skipped": 0, "failed": 1}

    for raw_item in raw_items:
        try:
            cleaned = _clean_raw_news(raw_item)
            if cleaned is None:
                failed += 1
                continue

            exists = clean_news_exists_by_url(cleaned["url"])
            if exists and policy == "skip":
                skipped += 1
                logger.info("Duplicate clean news skipped: url=%s", cleaned["url"])
                continue

            row_id = save_clean_news(cleaned, duplicate_policy=policy)
            if row_id is None:
                skipped += 1
                logger.info("Duplicate clean news skipped: url=%s", cleaned["url"])
            elif exists:
                updated += 1
            else:
                inserted += 1
        except Exception as error:
            failed += 1
            logger.error("Failed to clean raw news id=%s: %s", raw_item.get("id"), error)

    logger.info(
        "News cleaning completed: inserted=%s, updated=%s, skipped=%s, failed=%s",
        inserted,
        updated,
        skipped,
        failed,
    )
    return {"inserted": inserted, "updated": updated, "skipped": skipped, "failed": failed}
