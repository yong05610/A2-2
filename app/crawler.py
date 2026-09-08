"""BeautifulSoup based news crawling."""

from __future__ import annotations

import time
from datetime import datetime
from typing import Any
from urllib.parse import urljoin

from app.config import load_config
from app.database import fill_empty_raw_content_with_title, save_raw_news
from app.logger import get_logger


logger = get_logger(__name__)


def _now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds")


def _extract_items(html: str, base_url: str, limit: int) -> list[dict[str, str | None]]:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    items: list[dict[str, str | None]] = []
    seen_urls: set[str] = set()

    for anchor in soup.select(".titleline > a"):
        title = anchor.get_text(" ", strip=True)
        url = urljoin(base_url, anchor.get("href", ""))
        if title and url and url not in seen_urls:
            items.append({"title": title, "url": url, "summary": ""})
            seen_urls.add(url)
        if len(items) >= limit:
            return items

    for anchor in soup.find_all("a", href=True):
        title = anchor.get_text(" ", strip=True)
        url = urljoin(base_url, anchor["href"])
        if len(title) < 8 or url in seen_urls:
            continue
        items.append({"title": title, "url": url, "summary": ""})
        seen_urls.add(url)
        if len(items) >= limit:
            break

    return items


def crawl_news(limit: int, source: str | None = None, category: str | None = None) -> dict[str, int]:
    """Collect news-like links by crawling one configured page."""
    try:
        import requests
        from bs4 import BeautifulSoup  # noqa: F401
    except ImportError:
        logger.error("requests and beautifulsoup4 packages are required for crawling.")
        return {"fetched": 0, "saved": 0, "skipped": 0, "failed": 1}

    config = load_config()
    fetch_config = config["fetch"]
    crawl_url = source if source and source.startswith(("http://", "https://")) else config["news_sources"]["crawl_url"]
    source_name = source or crawl_url
    duplicate_policy = config["clean"].get("duplicate_policy", "skip")

    logger.info("Crawl news collection started: source=%s, limit=%s", source_name, limit)

    try:
        response = requests.get(
            crawl_url,
            headers={"User-Agent": fetch_config["user_agent"]},
            timeout=fetch_config["timeout"],
        )
        response.raise_for_status()
    except requests.RequestException as error:
        logger.error("Crawl request failed: url=%s error=%s", crawl_url, error)
        return {"fetched": 0, "saved": 0, "skipped": 0, "failed": 1}

    items = _extract_items(response.text, crawl_url, limit)
    saved = 0
    skipped = 0
    failed = 0

    for item in items:
        title = item["title"]
        url = item["url"]
        if not title or not url:
            failed += 1
            logger.warning("Crawled item skipped because title or URL is missing.")
            continue

        raw_summary = item.get("summary") or ""
        if not raw_summary.strip():
            raw_summary = title
            logger.warning("Crawled content fallback applied: url=%s", url)
        news = {
            "title": title,
            "url": url,
            "content": raw_summary,
            "source": source_name,
            "method": "crawl",
            "category": category,
            "published_at": None,
            "collected_at": _now(),
            "raw_payload": {
                "collection_method": "crawl",
                "raw_content": raw_summary,
                "raw_summary": raw_summary,
                "crawl_url": crawl_url,
            },
        }

        row_id = save_raw_news(news, duplicate_policy="upsert")
        if row_id is None:
            skipped += 1
            logger.info("Duplicate crawled news skipped: url=%s", url)
        else:
            saved += 1

        delay = float(fetch_config.get("delay", 0))
        if delay > 0:
            time.sleep(delay)

    backfilled = fill_empty_raw_content_with_title()
    if backfilled:
        logger.warning("Existing raw news rows backfilled with title content: count=%s", backfilled)
    logger.info("Crawl news collection completed: fetched=%s, saved=%s, skipped=%s, failed=%s", len(items), saved, skipped, failed)
    return {"fetched": len(items), "saved": saved, "skipped": skipped, "failed": failed}
