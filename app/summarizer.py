"""Gemini based news summarization."""

from __future__ import annotations

import os
from typing import Any

from app.config import GEMINI_MODEL, load_config
from app.database import get_clean_news_for_summary, save_summary, update_clean_news_status
from app.logger import get_logger


logger = get_logger(__name__)
PROMPT_VERSION = "ko-news-summary-v1"
DEFAULT_MIN_CONTENT_LENGTH = 50


def _build_prompt(title: str, content: str) -> str:
    return f"""다음 뉴스 내용을 한국어로 3~5문장으로 요약해줘.
핵심 내용과 의미를 간결하게 설명하고, 원문에 없는 내용은 추측하지 마.

제목:
{title}

본문:
{content}
"""


def _get_content_length(news: dict[str, Any]) -> int:
    content = str(news.get("content") or "").strip()
    stored_length = news.get("content_length")
    if isinstance(stored_length, int) and stored_length > 0:
        return stored_length
    return len(content)


def _create_gemini_client(api_key: str) -> Any:
    try:
        from google import genai
    except ImportError as error:
        raise RuntimeError("google-genai package is not installed. Run: python -m pip install -r requirements.txt") from error
    return genai.Client(api_key=api_key)


def _generate_summary(client: Any, model: str, title: str, content: str) -> str:
    prompt = _build_prompt(title, content)
    response = client.models.generate_content(model=model, contents=prompt)
    summary = str(getattr(response, "text", "") or "").strip()
    if not summary:
        raise RuntimeError("Gemini returned an empty response.")
    return summary


def summarize_news(
    news_id: int | None = None,
    summarize_all: bool = False,
    unsummarized: bool = True,
    limit: int | None = None,
    min_content_length: int = DEFAULT_MIN_CONTENT_LENGTH,
) -> dict[str, int]:
    """Summarize clean_news rows with Gemini and persist results."""
    del unsummarized

    config = load_config()
    ai_config = config.get("ai", {})
    api_key_env = ai_config.get("api_key_env", "GEMINI_API_KEY")
    model = ai_config.get("model", GEMINI_MODEL)

    include_summarized = summarize_all or news_id is not None
    targets = get_clean_news_for_summary(
        news_id=news_id,
        include_summarized=include_summarized,
        limit=limit,
    )

    logger.info("Summarize started")
    logger.info("Using Gemini model: %s", model)
    logger.info("Target news count: %s", len(targets))

    result = {
        "created_or_updated": 0,
        "skipped_short_content": 0,
        "failed": 0,
    }

    if not targets:
        logger.info("No news to summarize.")
        print("[INFO] No news to summarize.")
        return result

    api_key = os.getenv(api_key_env)
    if not api_key:
        logger.error("Gemini API key environment variable is missing: %s", api_key_env)
        print(f"[ERROR] Missing Gemini API key. Set the {api_key_env} environment variable.")
        result["failed"] = 1 if targets else 0
        return result

    try:
        client = _create_gemini_client(api_key)
    except RuntimeError as error:
        logger.error("%s", error)
        print(f"[ERROR] {error}")
        result["failed"] = 1 if targets else 0
        return result

    try:
        for news in targets:
            clean_news_id = int(news["id"])
            title = str(news.get("title") or "").strip()
            content = str(news.get("content") or "").strip()
            content_length = _get_content_length(news)

            if not content or content_length < min_content_length:
                update_clean_news_status(clean_news_id, "skipped_short_content")
                result["skipped_short_content"] += 1
                logger.info("[SKIP] Short content clean_news_id=%s content_length=%s", clean_news_id, content_length)
                print(f"[SKIP] Short content clean_news_id={clean_news_id} content_length={content_length}")
                continue

            logger.info('Summarizing clean_news_id=%s title="%s"', clean_news_id, title[:80])

            try:
                summary = _generate_summary(client, model, title, content)
                save_summary(
                    clean_news_id=clean_news_id,
                    summary=summary,
                    model=model,
                    prompt_version=PROMPT_VERSION,
                    status="completed",
                    error_message=None,
                )
                update_clean_news_status(clean_news_id, "summarized")
                result["created_or_updated"] += 1
                logger.info("[OK] Summary saved clean_news_id=%s", clean_news_id)
                print(f"[OK] Summary saved clean_news_id={clean_news_id}")
            except Exception as error:
                update_clean_news_status(clean_news_id, "summary_failed")
                result["failed"] += 1
                logger.error('Gemini failed clean_news_id=%s error="%s"', clean_news_id, error)
                print(f'[ERROR] Gemini failed clean_news_id={clean_news_id} error="{error}"')
    finally:
        close = getattr(client, "close", None)
        if callable(close):
            close()

    logger.info("Summarize completed")
    return result
