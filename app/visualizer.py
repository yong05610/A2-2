"""Chart generation with matplotlib."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

from app.config import load_config, resolve_project_path
from app.database import get_category_counts, get_daily_counts
from app.logger import get_logger


logger = get_logger(__name__)


def _configure_matplotlib() -> None:
    mpl_config_dir = resolve_project_path(".matplotlib")
    mpl_config_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(mpl_config_dir))

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams["font.family"] = ["Malgun Gothic", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False


def _chart_dir() -> Path:
    config = load_config()
    chart_path = config.get("paths", {}).get("charts", "data/charts")
    path = resolve_project_path(chart_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")


def create_category_chart() -> Path | None:
    """Create a category count bar chart and return the PNG path."""
    rows = get_category_counts()
    if not rows:
        logger.warning("No clean_news data available for category chart.")
        print("[INFO] No data available for category chart.")
        return None

    _configure_matplotlib()
    import matplotlib.pyplot as plt

    categories = [row["category"] for row in rows]
    counts = [row["news_count"] for row in rows]
    output_path = _chart_dir() / f"category_counts_{_timestamp()}.png"

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(categories, counts, color="#3B82F6")
    ax.set_title("\uce74\ud14c\uace0\ub9ac\ubcc4 \ub274\uc2a4 \uc218")
    ax.set_xlabel("\uce74\ud14c\uace0\ub9ac")
    ax.set_ylabel("\ub274\uc2a4 \uc218")
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)

    logger.info("Category chart saved: %s", output_path)
    return output_path


def create_daily_chart() -> Path | None:
    """Create a daily count chart and return the PNG path."""
    rows = get_daily_counts()
    if not rows:
        logger.warning("No news data available for daily chart.")
        print("[INFO] No data available for daily chart.")
        return None

    _configure_matplotlib()
    import matplotlib.dates as mdates
    import matplotlib.pyplot as plt

    dates = [datetime.strptime(row["news_date"], "%Y-%m-%d") for row in rows]
    counts = [row["news_count"] for row in rows]
    output_path = _chart_dir() / f"daily_counts_{_timestamp()}.png"

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(dates, counts, marker="o", color="#10B981")
    ax.set_title("\uc77c\uc790\ubcc4 \uc218\uc9d1 \ucd94\uc774")
    ax.set_xlabel("\uc77c\uc790")
    ax.set_ylabel("\ub274\uc2a4 \uc218")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    ax.tick_params(axis="x", rotation=30)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)

    logger.info("Daily chart saved: %s", output_path)
    return output_path


def create_charts() -> list[Path]:
    """Create all required charts and return generated paths."""
    chart_paths = []
    for chart_path in (create_category_chart(), create_daily_chart()):
        if chart_path is not None:
            chart_paths.append(chart_path)
    return chart_paths
