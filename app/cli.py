"""Command-line interface skeleton."""

import argparse
import sys

from app.analyzer import analyze_news
from app.cleaner import clean_raw_news
from app.crawler import crawl_news
from app.database import init_db
from app.exporter import export_table
from app.fetcher import fetch_rss_news
from app.reporter import generate_report
from app.summarizer import summarize_news


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


def _handle_clean(args: argparse.Namespace) -> None:
    """Run raw news cleaning."""
    result = clean_raw_news(policy=args.policy, limit=args.limit)
    print(
        "Clean completed: "
        f"inserted={result['inserted']}, "
        f"updated={result['updated']}, "
        f"skipped={result['skipped']}, "
        f"failed={result['failed']}"
    )


def _handle_summarize(args: argparse.Namespace) -> None:
    """Run AI summarization."""
    result = summarize_news(
        news_id=args.id,
        summarize_all=args.all,
        unsummarized=args.unsummarized or not args.all,
        limit=args.limit,
    )
    print("Summarize completed")
    print(f"created_or_updated: {result['created_or_updated']}")
    print(f"skipped_short_content: {result['skipped_short_content']}")
    print(f"failed: {result['failed']}")


def _handle_analyze(args: argparse.Namespace) -> None:
    """Run AI insight analysis."""
    result = analyze_news(
        date_from=args.date_from,
        date_to=args.date_to,
        category=args.category,
        limit=args.limit,
    )
    print("Analyze completed")
    print(f"analysis_id: {result['analysis_id']}")
    print(f"news_count: {result['news_count']}")
    print(f"failed: {result['failed']}")


def _handle_report(args: argparse.Namespace) -> None:
    """Generate report assets."""
    generate_report(report_format=args.format, top_n=args.top_n)


def _handle_export(args: argparse.Namespace) -> None:
    """Export database rows to a file."""
    try:
        export_table(
            table_name=args.table,
            export_format=args.format,
            status=args.status,
            summarized_only=args.summarized,
            category=args.category,
            date_from=args.date_from,
            date_to=args.date_to,
        )
    except ValueError as error:
        print(f"Export failed: {error}")


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
    clean_parser.set_defaults(func=_handle_clean)

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
    summarize_parser.set_defaults(func=_handle_summarize)

    analyze_parser = subparsers.add_parser("analyze", help="Analyze trends and insights with AI.")
    analyze_parser.add_argument("--date-from", help="Start date filter in YYYY-MM-DD format.")
    analyze_parser.add_argument("--date-to", help="End date filter in YYYY-MM-DD format.")
    analyze_parser.add_argument("--category", help="Category filter.")
    analyze_parser.add_argument("--limit", type=int, help="Maximum number of news items to analyze.")
    analyze_parser.set_defaults(func=_handle_analyze)

    report_parser = subparsers.add_parser("report", help="Generate a console and file report.")
    report_parser.add_argument(
        "--format",
        choices=["txt", "md"],
        default="md",
        help="Report file format. Default: md.",
    )
    report_parser.add_argument("--top-n", type=int, default=5, help="Number of top items to include.")
    report_parser.set_defaults(func=_handle_report)

    export_parser = subparsers.add_parser("export", help="Export cleaned news data.")
    export_parser.add_argument(
        "--table",
        choices=["clean_news", "summaries", "analyses"],
        default="clean_news",
        help="Database table to export. Default: clean_news.",
    )
    export_parser.add_argument(
        "--format",
        choices=["csv", "json"],
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
    export_parser.set_defaults(func=_handle_export)

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
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    init_db()
    parser = build_parser()
    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
        return
    parser.print_help()
