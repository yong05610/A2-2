"""Command-line interface skeleton."""

import argparse

from app.crawler import crawl_news
from app.database import init_db
from app.fetcher import fetch_rss_news


def _handle_placeholder(args: argparse.Namespace) -> None:
    """Print a clear message for commands implemented in later phases."""
    print(f"{args.command} command is not implemented yet.")


def _handle_init_db(args: argparse.Namespace) -> None:
    """Initialize the SQLite database tables."""
    init_db()
    print("Database initialized successfully.")


def _handle_fetch(args: argparse.Namespace) -> None:
    """Run news collection for the selected method."""
    if args.method in {"rss", "api"}:
        result = fetch_rss_news(limit=args.limit, source=args.source, category=args.category)
    else:
        result = crawl_news(limit=args.limit, source=args.source, category=args.category)

    print(
        "Fetch completed: "
        f"fetched={result['fetched']}, "
        f"saved={result['saved']}, "
        f"skipped={result['skipped']}, "
        f"failed={result['failed']}"
    )


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level CLI parser."""
    parser = argparse.ArgumentParser(
        prog="python main.py",
        description="CLI based AI news collection and analysis application.",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="command")

    init_db_parser = subparsers.add_parser("init-db", help="Initialize SQLite database tables.")
    init_db_parser.set_defaults(func=_handle_init_db)

    fetch_parser = subparsers.add_parser("fetch", help="Collect news from RSS/API or crawling.")
    fetch_parser.add_argument(
        "--method",
        choices=["rss", "api", "crawl"],
        default="rss",
        help="News collection method. Default: rss.",
    )
    fetch_parser.add_argument("--source", help="Configured source name or source URL.")
    fetch_parser.add_argument("--limit", type=int, default=10, help="Maximum number of news items.")
    fetch_parser.add_argument("--category", help="Category label to assign or filter.")
    fetch_parser.set_defaults(func=_handle_fetch)

    clean_parser = subparsers.add_parser("clean", help="Clean raw news and save normalized data.")
    clean_parser.add_argument(
        "--policy",
        choices=["skip", "upsert"],
        default="skip",
        help="Duplicate handling policy. Default: skip.",
    )
    clean_parser.add_argument("--limit", type=int, help="Maximum number of raw news items to clean.")
    clean_parser.set_defaults(func=_handle_placeholder)

    summarize_parser = subparsers.add_parser("summarize", help="Summarize cleaned news with AI.")
    summarize_target = summarize_parser.add_mutually_exclusive_group()
    summarize_target.add_argument("--all", action="store_true", help="Summarize all cleaned news.")
    summarize_target.add_argument("--id", type=int, help="Summarize one news item by ID.")
    summarize_target.add_argument(
        "--unsummarized",
        action="store_true",
        help="Summarize only news items without summaries.",
    )
    summarize_parser.add_argument("--limit", type=int, help="Maximum number of news items to summarize.")
    summarize_parser.set_defaults(func=_handle_placeholder)

    analyze_parser = subparsers.add_parser("analyze", help="Analyze trends and insights with AI.")
    analyze_parser.add_argument("--date-from", help="Start date filter in YYYY-MM-DD format.")
    analyze_parser.add_argument("--date-to", help="End date filter in YYYY-MM-DD format.")
    analyze_parser.add_argument("--category", help="Category filter.")
    analyze_parser.add_argument("--limit", type=int, help="Maximum number of news items to analyze.")
    analyze_parser.set_defaults(func=_handle_placeholder)

    report_parser = subparsers.add_parser("report", help="Generate a console and file report.")
    report_parser.add_argument(
        "--format",
        choices=["txt", "md"],
        default="md",
        help="Report file format. Default: md.",
    )
    report_parser.add_argument("--top-n", type=int, default=5, help="Number of top items to include.")
    report_parser.set_defaults(func=_handle_placeholder)

    export_parser = subparsers.add_parser("export", help="Export cleaned news data.")
    export_parser.add_argument(
        "--format",
        choices=["csv", "jsonl", "excel"],
        default="csv",
        help="Export file format. Default: csv.",
    )
    export_parser.add_argument(
        "--status",
        choices=["all", "cleaned", "summarized"],
        default="all",
        help="Status filter. Default: all.",
    )
    export_parser.add_argument(
        "--summarized",
        action="store_true",
        help="Shortcut for exporting summarized news only.",
    )
    export_parser.add_argument("--category", help="Category filter.")
    export_parser.add_argument("--date-from", help="Start date filter in YYYY-MM-DD format.")
    export_parser.add_argument("--date-to", help="End date filter in YYYY-MM-DD format.")
    export_parser.set_defaults(func=_handle_placeholder)

    list_parser = subparsers.add_parser("list", help="List stored news items.")
    list_parser.add_argument("--category", help="Category filter.")
    list_parser.add_argument("--date-from", help="Start date filter in YYYY-MM-DD format.")
    list_parser.add_argument("--date-to", help="End date filter in YYYY-MM-DD format.")
    list_parser.add_argument("--keyword", help="Keyword filter.")
    list_parser.add_argument("--page", type=int, default=1, help="Page number. Default: 1.")
    list_parser.add_argument("--page-size", type=int, default=10, help="Items per page. Default: 10.")
    list_parser.set_defaults(func=_handle_placeholder)

    show_parser = subparsers.add_parser("show", help="Show one stored news item.")
    show_parser.add_argument("--id", type=int, required=True, help="News item ID.")
    show_parser.set_defaults(func=_handle_placeholder)

    return parser


def main() -> None:
    """Run the CLI application."""
    init_db()
    parser = build_parser()
    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
        return
    parser.print_help()
