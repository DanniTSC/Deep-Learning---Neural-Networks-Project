from __future__ import annotations

import csv
import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from src.config import PRICE_COLUMNS, REQUIRED_COLUMNS
from src.load_data import iter_csv_files, read_daily_csv


DATE_FORMAT = "%d-%b-%Y"


@dataclass(frozen=True)
class PreprocessingResult:
    rows: list[dict[str, Any]]
    summary: dict[str, Any]


ProgressCallback = Callable[[int, int, Path, int, int], None]


def preprocess_nasdaq_data(
    raw_dir: Path,
    symbols: list[str] | tuple[str, ...],
    progress_callback: ProgressCallback | None = None,
    progress_interval_files: int = 250,
) -> PreprocessingResult:
    selected_symbols = tuple(symbol.upper().strip() for symbol in symbols)
    selected_set = set(selected_symbols)
    csv_files = iter_csv_files(raw_dir)

    rows: list[dict[str, Any]] = []
    seen_keys: set[tuple[str, str]] = set()
    dropped_by_reason = {
        "missing_required_value": 0,
        "invalid_date": 0,
        "invalid_numeric_value": 0,
        "invalid_price_or_volume": 0,
        "duplicate_symbol_date": 0,
    }
    rows_read = 0
    rows_selected = 0

    total_files = len(csv_files)
    progress_interval_files = max(progress_interval_files, 1)

    for file_index, csv_file in enumerate(csv_files, start=1):
        for raw_row in read_daily_csv(csv_file):
            rows_read += 1
            symbol = raw_row.get("Symbol", "").strip().upper()

            if symbol not in selected_set:
                continue

            rows_selected += 1
            cleaned_row, reason = _clean_row(raw_row, symbol)
            if cleaned_row is None:
                dropped_by_reason[reason] += 1
                continue

            key = (cleaned_row["Symbol"], cleaned_row["Date"])
            if key in seen_keys:
                dropped_by_reason["duplicate_symbol_date"] += 1
                continue

            seen_keys.add(key)
            rows.append(cleaned_row)

        if progress_callback and (
            file_index == 1
            or file_index % progress_interval_files == 0
            or file_index == total_files
        ):
            progress_callback(file_index, total_files, csv_file, rows_read, rows_selected)

    rows.sort(key=lambda row: (row["Symbol"], row["Date"]))
    summary = _build_summary(
        raw_dir=raw_dir,
        csv_files=csv_files,
        symbols=selected_symbols,
        rows_read=rows_read,
        rows_selected=rows_selected,
        rows=rows,
        dropped_by_reason=dropped_by_reason,
    )
    return PreprocessingResult(rows=rows, summary=summary)


def validate_processed_rows(
    rows: list[dict[str, Any]],
    expected_symbols: list[str] | tuple[str, ...],
) -> None:
    expected_set = {symbol.upper().strip() for symbol in expected_symbols}
    seen_keys: set[tuple[str, str]] = set()

    for row in rows:
        row_columns = tuple(row.keys())
        if row_columns != REQUIRED_COLUMNS:
            raise ValueError(f"Invalid processed columns: {row_columns}")

        symbol = row["Symbol"]
        if symbol not in expected_set:
            raise ValueError(f"Unexpected symbol in processed data: {symbol}")

        key = (symbol, row["Date"])
        if key in seen_keys:
            raise ValueError(f"Duplicate Symbol + Date found: {key}")
        seen_keys.add(key)

        for column in PRICE_COLUMNS:
            if row[column] <= 0:
                raise ValueError(f"Invalid non-positive {column} value in row: {row}")

        if row["High"] < row["Low"]:
            raise ValueError(f"Invalid row where High < Low: {row}")

        if row["Volume"] < 0:
            raise ValueError(f"Invalid negative Volume in row: {row}")


def write_processed_csv(rows: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=REQUIRED_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def write_summary_json(summary: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2, ensure_ascii=False)
        file.write("\n")


def _clean_row(raw_row: dict[str, str], symbol: str) -> tuple[dict[str, Any] | None, str]:
    if any(_is_missing(raw_row.get(column)) for column in REQUIRED_COLUMNS):
        return None, "missing_required_value"

    try:
        date = datetime.strptime(raw_row["Date"].strip(), DATE_FORMAT).date()
    except ValueError:
        return None, "invalid_date"

    try:
        open_price = float(raw_row["Open"])
        high_price = float(raw_row["High"])
        low_price = float(raw_row["Low"])
        close_price = float(raw_row["Close"])
        volume = int(float(raw_row["Volume"]))
    except ValueError:
        return None, "invalid_numeric_value"

    if (
        open_price <= 0
        or high_price <= 0
        or low_price <= 0
        or close_price <= 0
        or high_price < low_price
        or volume < 0
    ):
        return None, "invalid_price_or_volume"

    return (
        {
            "Symbol": symbol,
            "Date": date.isoformat(),
            "Open": open_price,
            "High": high_price,
            "Low": low_price,
            "Close": close_price,
            "Volume": volume,
        },
        "",
    )


def _is_missing(value: str | None) -> bool:
    return value is None or value.strip() == ""


def _build_summary(
    raw_dir: Path,
    csv_files: list[Path],
    symbols: tuple[str, ...],
    rows_read: int,
    rows_selected: int,
    rows: list[dict[str, Any]],
    dropped_by_reason: dict[str, int],
) -> dict[str, Any]:
    rows_by_symbol: dict[str, dict[str, Any]] = {
        symbol: {"rows": 0, "first_date": None, "last_date": None} for symbol in symbols
    }

    for row in rows:
        symbol_summary = rows_by_symbol[row["Symbol"]]
        symbol_summary["rows"] += 1
        symbol_summary["first_date"] = symbol_summary["first_date"] or row["Date"]
        symbol_summary["last_date"] = row["Date"]

    rows_dropped_total = sum(dropped_by_reason.values())

    return {
        "raw_dir": str(raw_dir),
        "csv_files_processed": len(csv_files),
        "symbols": list(symbols),
        "columns": list(REQUIRED_COLUMNS),
        "rows_read": rows_read,
        "rows_matching_symbols_before_cleaning": rows_selected,
        "rows_output": len(rows),
        "rows_dropped_total": rows_dropped_total,
        "dropped_by_reason": dropped_by_reason,
        "rows_by_symbol": rows_by_symbol,
    }
