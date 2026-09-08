"""Report generation."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from app.config import load_config, resolve_project_path
from app.database import get_category_counts, get_latest_analysis, get_report_metrics, get_source_counts
from app.logger import get_logger
from app.visualizer import create_charts


logger = get_logger(__name__)

REPORT_TITLE = "\ub274\uc2a4 \ubd84\uc11d \ub9ac\ud3ec\ud2b8"
CREATED_AT_LABEL = "\uc0dd\uc131 \uc2dc\uac01"
TOP_N_LABEL = "TOP N \uae30\uc900"
QUALITY_METRICS = "\ud488\uc9c8 \uc9c0\ud45c"
TOTAL_NEWS = "\ucd1d \ub274\uc2a4 \uc218"
SUMMARIZED_NEWS = "\uc694\uc57d \uc644\ub8cc \ub274\uc2a4 \uc218"
SUMMARY_RATE = "\uc694\uc57d \uc644\ub8cc \ube44\uc728"
AVERAGE_CONTENT_LENGTH = "\ud3c9\uade0 \ubcf8\ubb38 \uae38\uc774"
CATEGORY_TOP_N = "\uce74\ud14c\uace0\ub9ac\ubcc4 TOP N"
SOURCE_TOP_N = "\uc18c\uc2a4\ubcc4 TOP N"
LATEST_ANALYSIS = "\ucd5c\uc2e0 AI \uc778\uc0ac\uc774\ud2b8 \ubd84\uc11d"
CHART_PATHS = "\uc0dd\uc131\ub41c \ucc28\ud2b8 \uacbd\ub85c"
NO_DATA = "\ub370\uc774\ud130 \uc5c6\uc74c"
NO_ANALYSIS = "\ubd84\uc11d \uacb0\uacfc \uc5c6\uc74c"
NO_CHARTS = "\uc0dd\uc131\ub41c \ucc28\ud2b8 \uc5c6\uc74c"
NO_NEWS_MESSAGE = "\uc218\uc9d1/\uc815\uc81c\ub41c \ub274\uc2a4 \ub370\uc774\ud130\uac00 \uc5c6\uc2b5\ub2c8\ub2e4."
NOTICE = "\uc548\ub0b4"


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")


def _report_dir() -> Path:
    config = load_config()
    report_path = config.get("paths", {}).get("reports", "data/reports")
    path = resolve_project_path(report_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _format_table(rows: list[dict[str, Any]], label_key: str, count_key: str = "news_count") -> list[str]:
    if not rows:
        return [f"- {NO_DATA}"]
    return [f"- {row[label_key]}: {row[count_key]}\uac74" for row in rows]


def _analysis_lines(analysis: dict[str, Any] | None) -> list[str]:
    if analysis is None:
        return [NO_ANALYSIS]

    header = (
        f"analysis_id={analysis['id']}, "
        f"news_count={analysis['news_count']}, "
        f"model={analysis['model'] or 'unknown'}, "
        f"created_at={analysis['created_at']}"
    )
    return [header, "", str(analysis["result"]).strip()]


def _build_markdown_report(
    metrics: dict[str, Any],
    category_counts: list[dict[str, Any]],
    source_counts: list[dict[str, Any]],
    latest_analysis: dict[str, Any] | None,
    chart_paths: list[Path],
    top_n: int,
) -> str:
    lines: list[str] = [
        f"# {REPORT_TITLE}",
        "",
        f"- {CREATED_AT_LABEL}: {datetime.now().isoformat(timespec='seconds')}",
        f"- {TOP_N_LABEL}: {top_n}",
        "",
        f"## {QUALITY_METRICS}",
        "",
        f"- {TOTAL_NEWS}: {metrics['total_news']}\uac74",
        f"- {SUMMARIZED_NEWS}: {metrics['summarized_news']}\uac74",
        f"- {SUMMARY_RATE}: {metrics['summary_rate']:.1f}%",
        f"- {AVERAGE_CONTENT_LENGTH}: {metrics['average_content_length']:.1f}\uc790",
        "",
    ]

    if metrics["total_news"] == 0:
        lines.extend([f"## {NOTICE}", "", NO_NEWS_MESSAGE, ""])

    lines.extend([f"## {CATEGORY_TOP_N}", ""])
    lines.extend(_format_table(category_counts[:top_n], "category"))
    lines.extend(["", f"## {SOURCE_TOP_N}", ""])
    lines.extend(_format_table(source_counts[:top_n], "source"))
    lines.extend(["", f"## {LATEST_ANALYSIS}", ""])
    lines.extend(_analysis_lines(latest_analysis))
    lines.extend(["", f"## {CHART_PATHS}", ""])
    if chart_paths:
        lines.extend([f"- {path}" for path in chart_paths])
    else:
        lines.append(f"- {NO_CHARTS}")
    lines.append("")
    return "\n".join(lines)


def _build_text_report(
    metrics: dict[str, Any],
    category_counts: list[dict[str, Any]],
    source_counts: list[dict[str, Any]],
    latest_analysis: dict[str, Any] | None,
    chart_paths: list[Path],
    top_n: int,
) -> str:
    lines: list[str] = [
        REPORT_TITLE,
        "=" * 20,
        f"{CREATED_AT_LABEL}: {datetime.now().isoformat(timespec='seconds')}",
        f"{TOP_N_LABEL}: {top_n}",
        "",
        f"[{QUALITY_METRICS}]",
        f"{TOTAL_NEWS}: {metrics['total_news']}\uac74",
        f"{SUMMARIZED_NEWS}: {metrics['summarized_news']}\uac74",
        f"{SUMMARY_RATE}: {metrics['summary_rate']:.1f}%",
        f"{AVERAGE_CONTENT_LENGTH}: {metrics['average_content_length']:.1f}\uc790",
        "",
    ]

    if metrics["total_news"] == 0:
        lines.extend([f"[{NOTICE}]", NO_NEWS_MESSAGE, ""])

    lines.extend([f"[{CATEGORY_TOP_N}]"])
    lines.extend(_format_table(category_counts[:top_n], "category"))
    lines.extend(["", f"[{SOURCE_TOP_N}]"])
    lines.extend(_format_table(source_counts[:top_n], "source"))
    lines.extend(["", f"[{LATEST_ANALYSIS}]"])
    lines.extend(_analysis_lines(latest_analysis))
    lines.extend(["", f"[{CHART_PATHS}]"])
    if chart_paths:
        lines.extend([f"- {path}" for path in chart_paths])
    else:
        lines.append(f"- {NO_CHARTS}")
    lines.append("")
    return "\n".join(lines)


def generate_report(report_format: str = "md", top_n: int = 5) -> dict[str, object]:
    """Generate a console and file report."""
    logger.info("Report generation started: format=%s, top_n=%s", report_format, top_n)

    metrics = get_report_metrics()
    category_counts = get_category_counts()
    source_counts = get_source_counts(limit=top_n)
    latest_analysis = get_latest_analysis()
    chart_paths = create_charts()

    if report_format == "txt":
        report = _build_text_report(metrics, category_counts, source_counts, latest_analysis, chart_paths, top_n)
        extension = "txt"
    else:
        report = _build_markdown_report(metrics, category_counts, source_counts, latest_analysis, chart_paths, top_n)
        extension = "md"

    output_path = _report_dir() / f"news_report_{_timestamp()}.{extension}"
    output_path.write_text(report, encoding="utf-8-sig")

    print(report)
    print(f"Report saved: {output_path}")
    logger.info("Report saved: %s", output_path)

    return {
        "report_path": output_path,
        "chart_paths": chart_paths,
        "metrics": metrics,
    }
