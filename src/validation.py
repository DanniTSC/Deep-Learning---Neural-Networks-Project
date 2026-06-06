from __future__ import annotations

import csv
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd

from src.config import PRICE_COLUMNS, REQUIRED_COLUMNS, TARGET_COLUMN
from src.indicators import FEATURE_COLUMNS, FEATURE_TARGET_COLUMNS


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


def validate_features_targets_csv(
    csv_path: Path,
    expected_symbols: list[str] | tuple[str, ...],
    target_column: str = TARGET_COLUMN,
) -> dict[str, Any]:
    if not csv_path.exists():
        raise FileNotFoundError(f"Features/targets CSV does not exist: {csv_path}")

    data = pd.read_csv(csv_path)
    expected_columns = list(FEATURE_TARGET_COLUMNS)
    if list(data.columns) != expected_columns:
        raise ValueError(
            f"Invalid columns in {csv_path}: {list(data.columns)}. "
            f"Expected: {expected_columns}"
        )

    expected_symbol_set = {symbol.upper().strip() for symbol in expected_symbols}
    actual_symbol_set = set(data["Symbol"].astype(str).str.upper().str.strip())
    unexpected_symbols = sorted(actual_symbol_set - expected_symbol_set)
    if unexpected_symbols:
        raise ValueError(f"Unexpected symbols in features/targets CSV: {unexpected_symbols}")

    missing_symbols = sorted(expected_symbol_set - actual_symbol_set)
    if missing_symbols:
        raise ValueError(f"Missing symbols from features/targets CSV: {missing_symbols}")

    if data.duplicated(["Symbol", "Date"]).any():
        duplicate_rows = data.loc[data.duplicated(["Symbol", "Date"], keep=False), ["Symbol", "Date"]]
        raise ValueError(
            "Duplicate Symbol + Date rows in features/targets CSV: "
            f"{duplicate_rows.head(5).to_dict(orient='records')}"
        )

    data["Date"] = pd.to_datetime(data["Date"], errors="raise")
    numeric_columns = ["Open", "High", "Low", "Close", "Volume", *FEATURE_COLUMNS, target_column]
    numeric_data = data[numeric_columns].apply(pd.to_numeric, errors="raise")
    if numeric_data.isna().any().any():
        columns_with_nan = numeric_data.columns[numeric_data.isna().any()].tolist()
        raise ValueError(f"NaN values found in features/targets columns: {columns_with_nan}")

    if (numeric_data[target_column] < 0).any():
        raise ValueError(f"Negative values found in regression target {target_column!r}")

    rows_by_symbol = data.groupby("Symbol").size().sort_index().to_dict()
    first_date_by_symbol = (
        data.groupby("Symbol")["Date"].min().dt.date.astype(str).sort_index().to_dict()
    )
    last_date_by_symbol = (
        data.groupby("Symbol")["Date"].max().dt.date.astype(str).sort_index().to_dict()
    )
    target = numeric_data[target_column]

    return {
        "status": "passed",
        "rows_validated": int(len(data)),
        "symbols": sorted(actual_symbol_set),
        "rows_by_symbol": {symbol: int(rows) for symbol, rows in rows_by_symbol.items()},
        "first_date_by_symbol": first_date_by_symbol,
        "last_date_by_symbol": last_date_by_symbol,
        "target_column": target_column,
        "target_summary": {
            "min": float(target.min()),
            "mean": float(target.mean()),
            "median": float(target.median()),
            "max": float(target.max()),
            "zero_target_share": float((target == 0).mean()),
        },
        "checks": [
            "columns",
            "expected_symbols",
            "duplicate_symbol_date",
            "iso_date",
            "numeric_features",
            "no_nan_features_or_target",
            "non_negative_regression_target",
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
