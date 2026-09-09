"""Data export helpers."""

from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from app.config import load_config, resolve_project_path
from app.database import get_export_rows
from app.logger import get_logger


logger = get_logger(__name__)


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")


def _export_dir() -> Path:
    config = load_config()
    export_path = config.get("paths", {}).get("exports", "data/exports")
    path = resolve_project_path(export_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = list(rows[0].keys()) if rows else ["message"]
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        if rows:
            writer.writerows(rows)
        else:
            writer.writerow({"message": "No data"})


def _write_json(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as file:
        json.dump(rows, file, ensure_ascii=False, indent=2)
        file.write("\n")


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as file:
        if not rows:
            file.write(json.dumps({"message": "No data"}, ensure_ascii=False))
            file.write("\n")
            return
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False))
            file.write("\n")


def _write_excel(path: Path, rows: list[dict[str, Any]]) -> None:
    try:
        import pandas as pd
    except ImportError as error:
        raise RuntimeError("pandas and openpyxl are required for Excel export.") from error

    data = rows if rows else [{"message": "No data"}]
    dataframe = pd.DataFrame(data)
    dataframe.to_excel(path, index=False, engine="openpyxl")


def export_table(
    table_name: str = "clean_news",
    export_format: str = "csv",
    status: str | None = None,
    summarized_only: bool = False,
    category: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> dict[str, object]:
    """Export selected database table to CSV, JSON, JSONL, or Excel."""
    supported_formats = {"csv", "json", "jsonl", "excel"}
    if export_format not in supported_formats:
        raise ValueError(f"Unsupported export format: {export_format}")

    logger.info("Export started: table=%s, format=%s", table_name, export_format)
    rows = get_export_rows(
        table_name=table_name,
        status=status,
        category=category,
        date_from=date_from,
        date_to=date_to,
        summarized_only=summarized_only,
    )

    extension = "xlsx" if export_format == "excel" else export_format
    output_path = _export_dir() / f"export_{table_name}_{_timestamp()}.{extension}"
    if export_format == "csv":
        _write_csv(output_path, rows)
    elif export_format == "json":
        _write_json(output_path, rows)
    elif export_format == "jsonl":
        _write_jsonl(output_path, rows)
    else:
        _write_excel(output_path, rows)

    logger.info("Export completed: path=%s, rows=%s", output_path, len(rows))
    print(f"Export completed: table={table_name}, format={export_format}, rows={len(rows)}")
    print(f"Export saved: {output_path}")

    return {
        "export_path": output_path,
        "row_count": len(rows),
        "table": table_name,
        "format": export_format,
    }
