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


def export_table(
    table_name: str = "clean_news",
    export_format: str = "csv",
    status: str | None = None,
    summarized_only: bool = False,
    category: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> dict[str, object]:
    """Export selected database table to CSV or JSON."""
    if export_format not in {"csv", "json"}:
        raise ValueError("Only csv and json export formats are implemented in Phase 10.")

    logger.info("Export started: table=%s, format=%s", table_name, export_format)
    rows = get_export_rows(
        table_name=table_name,
        status=status,
        category=category,
        date_from=date_from,
        date_to=date_to,
        summarized_only=summarized_only,
    )

    output_path = _export_dir() / f"export_{table_name}_{_timestamp()}.{export_format}"
    if export_format == "csv":
        _write_csv(output_path, rows)
    else:
        _write_json(output_path, rows)

    logger.info("Export completed: path=%s, rows=%s", output_path, len(rows))
    print(f"Export completed: table={table_name}, format={export_format}, rows={len(rows)}")
    print(f"Export saved: {output_path}")

    return {
        "export_path": output_path,
        "row_count": len(rows),
        "table": table_name,
        "format": export_format,
    }
