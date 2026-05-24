from __future__ import annotations

import csv
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

from src.config import PRICE_COLUMNS, REQUIRED_COLUMNS


def validate_processed_csv(
    csv_path: Path,
    expected_symbols: list[str] | tuple[str, ...],
) -> dict[str, Any]:
    if not csv_path.exists():
        raise FileNotFoundError(f"Processed CSV does not exist: {csv_path}")

    expected_symbol_set = {symbol.upper().strip() for symbol in expected_symbols}
    seen_keys: set[tuple[str, str]] = set()
    rows_by_symbol: Counter[str] = Counter()
    first_date_by_symbol: dict[str, str] = {}
    last_date_by_symbol: dict[str, str] = {}
    row_count = 0

    with csv_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        if tuple(reader.fieldnames or ()) != REQUIRED_COLUMNS:
            raise ValueError(
                f"Invalid columns in {csv_path}: {reader.fieldnames}. "
                f"Expected: {REQUIRED_COLUMNS}"
            )

        for line_number, row in enumerate(reader, start=2):
            row_count += 1
            _validate_required_values(row, line_number)

            symbol = row["Symbol"].strip().upper()
            if symbol not in expected_symbol_set:
                raise ValueError(f"Unexpected symbol {symbol!r} on line {line_number}")

            _validate_iso_date(row["Date"], line_number)
            key = (symbol, row["Date"])
            if key in seen_keys:
                raise ValueError(f"Duplicate Symbol + Date {key} on line {line_number}")
            seen_keys.add(key)

            prices = _validate_prices(row, line_number)
            if prices["High"] < prices["Low"]:
                raise ValueError(f"High < Low on line {line_number}: {row}")

            volume = _parse_int(row["Volume"], "Volume", line_number)
            if volume < 0:
                raise ValueError(f"Negative Volume on line {line_number}: {row}")

            rows_by_symbol[symbol] += 1
            first_date_by_symbol.setdefault(symbol, row["Date"])
            last_date_by_symbol[symbol] = row["Date"]

    missing_symbols = sorted(expected_symbol_set - set(rows_by_symbol))
    if missing_symbols:
        raise ValueError(f"Missing symbols from processed CSV: {missing_symbols}")

    return {
        "status": "passed",
        "rows_validated": row_count,
        "symbols": sorted(rows_by_symbol),
        "rows_by_symbol": dict(sorted(rows_by_symbol.items())),
        "first_date_by_symbol": dict(sorted(first_date_by_symbol.items())),
        "last_date_by_symbol": dict(sorted(last_date_by_symbol.items())),
        "checks": [
            "columns",
            "required_values",
            "expected_symbols",
            "duplicate_symbol_date",
            "iso_date",
            "positive_prices",
            "high_greater_or_equal_low",
            "non_negative_volume",
        ],
    }


def _validate_required_values(row: dict[str, str], line_number: int) -> None:
    missing_columns = [
        column for column in REQUIRED_COLUMNS if row.get(column) is None or row[column].strip() == ""
    ]
    if missing_columns:
        raise ValueError(f"Missing values on line {line_number}: {missing_columns}")


def _validate_iso_date(value: str, line_number: int) -> None:
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"Invalid ISO date on line {line_number}: {value!r}") from exc


def _validate_prices(row: dict[str, str], line_number: int) -> dict[str, float]:
    prices = {
        column: _parse_float(row[column], column, line_number) for column in PRICE_COLUMNS
    }
    invalid_columns = [column for column, value in prices.items() if value <= 0]
    if invalid_columns:
        raise ValueError(f"Non-positive prices on line {line_number}: {invalid_columns}")
    return prices


def _parse_float(value: str, column: str, line_number: int) -> float:
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(
            f"Invalid numeric value for {column} on line {line_number}: {value!r}"
        ) from exc


def _parse_int(value: str, column: str, line_number: int) -> int:
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(
            f"Invalid integer value for {column} on line {line_number}: {value!r}"
        ) from exc
