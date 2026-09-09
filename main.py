"""Application entry point for the news AI CLI."""

from app.cli import main as cli_main
from app.logger import get_logger


logger = get_logger(__name__)


if __name__ == "__main__":
    try:
        logger.info("Application started")
        cli_main()
    except Exception:
        logger.exception("Unexpected application error")
        print("Unexpected error occurred. Check logs/app.log for details.")
        raise
    finally:
        logger.info("Application finished")
