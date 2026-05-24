from __future__ import annotations

import csv
from collections.abc import Iterator
from pathlib import Path

from src.config import REQUIRED_COLUMNS


def iter_csv_files(raw_dir: Path) -> list[Path]:
    """Return all daily CSV files under the raw NASDAQ directory."""
    if not raw_dir.exists():
        raise FileNotFoundError(f"Raw data directory does not exist: {raw_dir}")
    if not raw_dir.is_dir():
        raise NotADirectoryError(f"Raw data path is not a directory: {raw_dir}")

    return sorted(path for path in raw_dir.rglob("*.csv") if path.is_file())


def read_daily_csv(csv_path: Path) -> Iterator[dict[str, str]]:
    """Yield raw rows from one daily CSV after checking its header."""
    with csv_path.open(
        "r",
        encoding="utf-8-sig",
        errors="replace",
        newline="",
    ) as file:
        reader = csv.DictReader(file)
        fieldnames = tuple(reader.fieldnames or ())
        if fieldnames != REQUIRED_COLUMNS:
            raise ValueError(
                f"Unexpected header in {csv_path}: {fieldnames}. "
                f"Expected: {REQUIRED_COLUMNS}"
            )

        yield from reader
