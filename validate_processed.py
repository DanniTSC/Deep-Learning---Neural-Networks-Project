from __future__ import annotations

import argparse
from pathlib import Path

from src.config import DEFAULT_FEATURES_TARGETS_FILE, DEFAULT_PROCESSED_FILE, SELECTED_SYMBOLS
from src.evaluate import regression_metrics_template
from src.validation import validate_features_targets_csv, validate_processed_csv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate the processed NASDAQ CSV.")
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_PROCESSED_FILE,
        help=f"Processed CSV path. Default: {DEFAULT_PROCESSED_FILE}",
    )
    parser.add_argument(
        "--features-input",
        type=Path,
        default=DEFAULT_FEATURES_TARGETS_FILE,
        help=f"Features + target CSV path. Default: {DEFAULT_FEATURES_TARGETS_FILE}",
    )
    parser.add_argument(
        "--symbols",
        nargs="+",
        default=list(SELECTED_SYMBOLS),
        help="Expected symbols in the processed CSV.",
    )
    parser.add_argument(
        "--features",
        action="store_true",
        help="Validate the features + regression target CSV instead of the processed OHLCV CSV.",
    )
    parser.add_argument(
        "--show-regression-metrics-template",
        action="store_true",
        help="Print regression metric names and meanings for the report/modeling stage.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.features:
        result = validate_features_targets_csv(args.features_input, args.symbols)
        print(f"Features + target validation passed: {result['rows_validated']:,} rows")
        print(f"Target: {result['target_column']}")
        print(f"Symbols: {', '.join(result['symbols'])}")
    else:
        result = validate_processed_csv(args.input, args.symbols)
        print(f"Processed CSV validation passed: {result['rows_validated']:,} rows")
        print(f"Symbols: {', '.join(result['symbols'])}")

    if args.show_regression_metrics_template:
        print("Regression metrics template:")
        for metric, description in regression_metrics_template().items():
            print(f"  - {metric}: {description}")


if __name__ == "__main__":
    main()
