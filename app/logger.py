"""Logging setup for the application."""

import logging
import sys

from app.config import load_config, resolve_project_path


_CONFIGURED = False


def configure_logging() -> None:
    """Configure console and file logging once."""
    global _CONFIGURED
    if _CONFIGURED:
        return

    config = load_config()
    logging_config = config.get("logging", {})
    log_level_name = str(logging_config.get("level", "INFO")).upper()
    log_level = getattr(logging, log_level_name, logging.INFO)
    log_file = resolve_project_path(str(logging_config.get("file", "logs/app.log")))
    log_file.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stderr),
            logging.FileHandler(log_file, encoding="utf-8"),
        ],
        force=True,
    )
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Return a module logger."""
    configure_logging()
    return logging.getLogger(name)
