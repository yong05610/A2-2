"""Gemini based news insight analysis."""

from __future__ import annotations

import os
from typing import Any

from app.config import GEMINI_MODEL, load_config
from app.database import get_news_for_analysis, save_analysis
from app.logger import get_logger


logger = get_logger(__name__)


def _create_gemini_client(api_key: str) -> Any:
    try:
        from google import genai
    except ImportError as error:
        raise RuntimeError("google-genai package is not installed. Run: python -m pip install -r requirements.txt") from error
    return genai.Client(api_key=api_key)


def _build_analysis_input(news_items: list[dict[str, Any]]) -> str:
    blocks: list[str] = []
    for index, item in enumerate(news_items, start=1):
        title = str(item.get("title") or "").strip()
        content = str(item.get("content") or "").strip()
        summary = str(item.get("summary") or "").strip()
        category = str(item.get("category") or "").strip()
        published_at = str(item.get("published_at") or "").strip()

        blocks.append(
            "\n".join(
                [
                    f"[뉴스 {index}]",
                    f"제목: {title}",
                    f"카테고리: {category or '미분류'}",
                    f"게시일: {published_at or '없음'}",
                    f"요약: {summary or '없음'}",
                    f"본문: {content}",
                ]
            )
        )
    return "\n\n".join(blocks)


def _build_prompt(news_items: list[dict[str, Any]]) -> str:
    analysis_input = _build_analysis_input(news_items)
    return f"""아래 여러 뉴스의 제목, 본문, 기존 요약을 종합해서 한국어로 인사이트 분석을 작성해줘.

반드시 다음 네 개 항목명을 그대로 포함해줘.

## 주요 트렌드
## 핵심 키워드
## 시사점
## 공통점과 차이점

규칙:
- 원문에 없는 내용을 추측하지 마.
- 과장하지 말고 근거가 약한 내용은 단정하지 마.
- 핵심 내용을 간결하게 정리해.
- 각 항목은 2~5개 bullet로 작성해.

분석 대상 뉴스:
{analysis_input}
"""


def _generate_analysis(client: Any, model: str, news_items: list[dict[str, Any]]) -> str:
    response = client.models.generate_content(model=model, contents=_build_prompt(news_items))
    result = str(getattr(response, "text", "") or "").strip()
    if not result:
        raise RuntimeError("Gemini returned an empty analysis response.")
    return result


def analyze_news(
    date_from: str | None = None,
    date_to: str | None = None,
    category: str | None = None,
    limit: int | None = None,
) -> dict[str, int | None]:
    """Analyze selected news with Gemini and persist the result."""
    config = load_config()
    ai_config = config.get("ai", {})
    api_key_env = ai_config.get("api_key_env", "GEMINI_API_KEY")
    model = ai_config.get("model", GEMINI_MODEL)

    logger.info("Analyze started")
    logger.info("Using Gemini model: %s", model)
    logger.info("Analyze filters: date_from=%s, date_to=%s, category=%s, limit=%s", date_from, date_to, category, limit)

    news_items = get_news_for_analysis(
        date_from=date_from,
        date_to=date_to,
        category=category,
        limit=limit,
    )
    logger.info("Target news count: %s", len(news_items))

    if not news_items:
        print("[INFO] No news to analyze.")
        logger.info("No news to analyze.")
        return {"analysis_id": None, "news_count": 0, "failed": 0}

    api_key = os.getenv(api_key_env)
    if not api_key:
        logger.error("Gemini API key environment variable is missing: %s", api_key_env)
        print(f"[ERROR] Missing Gemini API key. Set the {api_key_env} environment variable.")
        return {"analysis_id": None, "news_count": len(news_items), "failed": 1}

    try:
        client = _create_gemini_client(api_key)
    except RuntimeError as error:
        logger.error("%s", error)
        print(f"[ERROR] {error}")
        return {"analysis_id": None, "news_count": len(news_items), "failed": 1}

    try:
        result = _generate_analysis(client, model, news_items)
        analysis_id = save_analysis(
            result=result,
            date_from=date_from,
            date_to=date_to,
            category=category,
            news_count=len(news_items),
            model=model,
        )
    except Exception as error:
        logger.error('Gemini analysis failed error="%s"', error)
        print(f'[ERROR] Gemini analysis failed error="{error}"')
        return {"analysis_id": None, "news_count": len(news_items), "failed": 1}
    finally:
        close = getattr(client, "close", None)
        if callable(close):
            close()

    logger.info("Analyze completed: analysis_id=%s", analysis_id)
    print(result)
    return {"analysis_id": analysis_id, "news_count": len(news_items), "failed": 0}
