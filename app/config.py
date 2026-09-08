"""Configuration helpers for the application."""

import copy
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config.json"

DEFAULT_CONFIG: dict[str, Any] = {
    "database": {
        "path": "data/news.db",
    },
    "news_sources": {
        "rss_urls": [
            "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko",
        ],
        "crawl_url": "https://news.ycombinator.com/news",
    },
    "fetch": {
        "timeout": 10,
        "delay": 1.0,
        "user_agent": "Mozilla/5.0 (compatible; NewsAICLI/1.0)",
    },
    "clean": {
        "duplicate_policy": "skip",
    },
    "paths": {
        "logs": "logs",
    },
}


def _merge_config(default: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Merge user config into defaults without dropping nested defaults."""
    merged = copy.deepcopy(default)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge_config(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config() -> dict[str, Any]:
    """Load config.json and merge it with required defaults."""
    if not CONFIG_PATH.exists():
        return copy.deepcopy(DEFAULT_CONFIG)

    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        loaded_config = json.load(file)

    return _merge_config(DEFAULT_CONFIG, loaded_config)


def resolve_project_path(path_value: str) -> Path:
    """Resolve a config path relative to the project root."""
    path = Path(path_value)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path
