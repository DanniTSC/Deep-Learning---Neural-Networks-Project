from __future__ import annotations

import argparse
from pathlib import Path

from src.config import DEFAULT_PROCESSED_FILE, SELECTED_SYMBOLS
from src.validation import validate_processed_csv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate the processed NASDAQ CSV.")
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_PROCESSED_FILE,
        help=f"Processed CSV path. Default: {DEFAULT_PROCESSED_FILE}",
    )
    parser.add_argument(
        "--symbols",
        nargs="+",
        default=list(SELECTED_SYMBOLS),
        help="Expected symbols in the processed CSV.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = validate_processed_csv(args.input, args.symbols)
    print(f"Validation passed: {result['rows_validated']:,} rows")
    print(f"Symbols: {', '.join(result['symbols'])}")


if __name__ == "__main__":
    main()
