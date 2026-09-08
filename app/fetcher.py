"""RSS news collection."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from app.config import load_config
from app.database import fill_empty_raw_content_with_title, save_raw_news
from app.logger import get_logger


logger = get_logger(__name__)


def _now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds")


def _get_rss_urls(config: dict[str, Any], source: str | None) -> list[str]:
    if source and source.startswith(("http://", "https://")):
        return [source]

    sources = config.get("news_sources", {})
    rss_urls = sources.get("rss_urls")
    if isinstance(rss_urls, list) and rss_urls:
        return [str(url) for url in rss_urls]

    rss_url = sources.get("rss_url")
    if rss_url:
        return [str(rss_url)]

    return ["https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"]


def fetch_rss_news(limit: int, source: str | None = None, category: str | None = None) -> dict[str, int]:
    """Collect RSS news and save rows into raw_news."""
    try:
        import feedparser
    except ImportError:
        logger.error("feedparser package is required for RSS collection.")
        return {"fetched": 0, "saved": 0, "skipped": 0, "failed": 1}

    config = load_config()
    duplicate_policy = config["clean"].get("duplicate_policy", "skip")
    urls = _get_rss_urls(config, source)
    source_name = source or "rss"

    logger.info("RSS news collection started: source=%s, limit=%s", source_name, limit)

    fetched = 0
    saved = 0
    skipped = 0
    failed = 0

    for rss_url in urls:
        if fetched >= limit:
            break

        feed = feedparser.parse(rss_url)
        if getattr(feed, "bozo", False):
            logger.error("RSS parse failed: url=%s error=%s", rss_url, getattr(feed, "bozo_exception", "unknown"))
            failed += 1
            continue

        feed_source = source or getattr(feed.feed, "title", None) or rss_url
        for entry in feed.entries:
            if fetched >= limit:
                break

            title = getattr(entry, "title", "").strip()
            url = getattr(entry, "link", "").strip()
            if not title or not url:
                failed += 1
                logger.warning("RSS item skipped because title or URL is missing.")
                continue

            raw_summary = getattr(entry, "summary", "") or getattr(entry, "description", "")
            raw_content = raw_summary.strip() if isinstance(raw_summary, str) else str(raw_summary or "").strip()
            if not raw_content:
                raw_content = title
                raw_summary = title
                logger.warning("RSS content fallback applied: url=%s", url)
            news = {
                "title": title,
                "url": url,
                "content": raw_content,
                "source": feed_source,
                "method": "rss",
                "category": category,
                "published_at": getattr(entry, "published", None) or getattr(entry, "updated", None),
                "collected_at": _now(),
                "raw_payload": {
                    "collection_method": "rss",
                    "raw_content": raw_content,
                    "raw_summary": raw_summary,
                    "rss_url": rss_url,
                },
            }

            row_id = save_raw_news(news, duplicate_policy="upsert")
            fetched += 1
            if row_id is None:
                skipped += 1
                logger.info("Duplicate RSS news skipped: url=%s", url)
            else:
                saved += 1

    backfilled = fill_empty_raw_content_with_title()
    if backfilled:
        logger.warning("Existing raw news rows backfilled with title content: count=%s", backfilled)
    logger.info("RSS news collection completed: fetched=%s, saved=%s, skipped=%s, failed=%s", fetched, saved, skipped, failed)
    return {"fetched": fetched, "saved": saved, "skipped": skipped, "failed": failed}
