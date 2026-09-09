"""Configuration helpers for the application."""

import copy
import json
import os
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config.json"
ENV_PATH = PROJECT_ROOT / ".env"

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

if load_dotenv is not None:
    load_dotenv(ENV_PATH)

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

DEFAULT_CONFIG: dict[str, Any] = {
    "database": {
        "db_path": "data/news.db",
        "path": "data/news.db",
    },
    "gemini": {
        "api_key_env": "GEMINI_API_KEY",
        "model": GEMINI_MODEL,
    },
    "ai": {
        "provider": "gemini",
        "api_key_env": "GEMINI_API_KEY",
        "model": GEMINI_MODEL,
    },
    "news": {
        "sources": [
            "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko",
        ],
        "rss_url": "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko",
        "crawl_url": "https://news.ycombinator.com/news",
        "duplicate_policy": "skip",
    },
    "news_sources": {
        "rss_urls": [
            "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko",
        ],
        "crawl_url": "https://news.ycombinator.com/news",
    },
    "request": {
        "timeout": 10,
        "delay": 1.0,
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
        "reports_dir": "data/reports",
        "exports_dir": "data/exports",
        "charts_dir": "data/charts",
        "logs_dir": "logs",
        "charts": "data/charts",
        "exports": "data/exports",
        "reports": "data/reports",
        "logs": "logs",
    },
    "logging": {
        "level": "INFO",
        "file": "logs/app.log",
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


def _first_value(*values: Any) -> Any:
    """Return the first non-empty value from aliases."""
    for value in values:
        if value not in (None, "", [], {}):
            return value
    return None


def _normalize_config(config: dict[str, Any]) -> dict[str, Any]:
    """Populate legacy and Phase 12 config aliases from one canonical structure."""
    database = config.setdefault("database", {})
    db_path = _first_value(database.get("db_path"), database.get("path"), "data/news.db")
    database["db_path"] = db_path
    database["path"] = db_path

    gemini = config.setdefault("gemini", {})
    ai = config.setdefault("ai", {})
    api_key_env = _first_value(gemini.get("api_key_env"), ai.get("api_key_env"), "GEMINI_API_KEY")
    model = _first_value(gemini.get("model"), ai.get("model"), os.getenv("GEMINI_MODEL"), GEMINI_MODEL)
    gemini["api_key_env"] = api_key_env
    gemini["model"] = model
    ai["provider"] = ai.get("provider", "gemini")
    ai["api_key_env"] = api_key_env
    ai["model"] = model

    news = config.setdefault("news", {})
    news_sources = config.setdefault("news_sources", {})
    rss_sources = _first_value(news.get("sources"), news_sources.get("rss_urls"))
    if not rss_sources:
        rss_url = _first_value(news.get("rss_url"), news_sources.get("rss_url"))
        rss_sources = [rss_url] if rss_url else DEFAULT_CONFIG["news"]["sources"]
    if isinstance(rss_sources, str):
        rss_sources = [rss_sources]
    crawl_url = _first_value(news.get("crawl_url"), news_sources.get("crawl_url"), DEFAULT_CONFIG["news"]["crawl_url"])
    duplicate_policy = _first_value(news.get("duplicate_policy"), config.get("clean", {}).get("duplicate_policy"), "skip")
    news["sources"] = rss_sources
    news["rss_url"] = rss_sources[0] if rss_sources else DEFAULT_CONFIG["news"]["rss_url"]
    news["crawl_url"] = crawl_url
    news["duplicate_policy"] = duplicate_policy
    news_sources["rss_urls"] = rss_sources
    news_sources["rss_url"] = news["rss_url"]
    news_sources["crawl_url"] = crawl_url
    config.setdefault("clean", {})["duplicate_policy"] = duplicate_policy

    request = config.setdefault("request", {})
    fetch = config.setdefault("fetch", {})
    timeout = _first_value(request.get("timeout"), fetch.get("timeout"), 10)
    delay = _first_value(request.get("delay"), fetch.get("delay"), 1.0)
    request["timeout"] = timeout
    request["delay"] = delay
    fetch["timeout"] = timeout
    fetch["delay"] = delay
    fetch["user_agent"] = fetch.get("user_agent", DEFAULT_CONFIG["fetch"]["user_agent"])

    paths = config.setdefault("paths", {})
    reports = _first_value(paths.get("reports_dir"), paths.get("reports"), "data/reports")
    exports = _first_value(paths.get("exports_dir"), paths.get("exports"), "data/exports")
    charts = _first_value(paths.get("charts_dir"), paths.get("charts"), "data/charts")
    logs = _first_value(paths.get("logs_dir"), paths.get("logs"), "logs")
    paths["reports_dir"] = reports
    paths["exports_dir"] = exports
    paths["charts_dir"] = charts
    paths["logs_dir"] = logs
    paths["reports"] = reports
    paths["exports"] = exports
    paths["charts"] = charts
    paths["logs"] = logs

    logging_config = config.setdefault("logging", {})
    logging_config["level"] = _first_value(logging_config.get("level"), "INFO")
    logging_config["file"] = _first_value(logging_config.get("file"), str(Path(logs) / "app.log"))
    return config


def load_config() -> dict[str, Any]:
    """Load config.json and merge it with required defaults."""
    if not CONFIG_PATH.exists():
        config = copy.deepcopy(DEFAULT_CONFIG)
        return _normalize_config(config)

    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        loaded_config = json.load(file)

    config = _merge_config(DEFAULT_CONFIG, loaded_config)
    return _normalize_config(config)


def resolve_project_path(path_value: str) -> Path:
    """Resolve a config path relative to the project root."""
    path = Path(path_value)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path
