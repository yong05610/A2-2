"""Logging setup for the application."""

import logging

from app.config import load_config, resolve_project_path


_CONFIGURED = False


def configure_logging() -> None:
    """Configure console and file logging once."""
    global _CONFIGURED
    if _CONFIGURED:
        return

    config = load_config()
    log_dir = resolve_project_path(config["paths"]["logs"])
    log_dir.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_dir / "app.log", encoding="utf-8"),
        ],
    )
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Return a module logger."""
    configure_logging()
    return logging.getLogger(name)
