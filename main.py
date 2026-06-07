from __future__ import annotations

import argparse
from pathlib import Path

from src.config import (
    DEFAULT_FEATURES_SUMMARY_FILE,
    DEFAULT_FEATURES_TARGETS_FILE,
    DEFAULT_PROCESSED_FILE,
    DEFAULT_RAW_DIR,
    DEFAULT_SUMMARY_FILE,
    FIGURES_DIR,
    SELECTED_SYMBOLS,
)
from src.pipeline import build_features_dataset, build_processed_dataset
from src.validation import validate_features_targets_csv, validate_processed_csv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the NASDAQ drawdown data pipeline."
    )
    parser.add_argument(
        "--step",
        choices=("all", "preprocess", "features"),
        default="all",
        help="Pipeline step to run. Default: all",
    )
    parser.add_argument(
        "--processed-mode",
        choices=("reuse", "regenerate"),
        default="reuse",
        help="Reuse existing processed CSV or regenerate it from raw CSV files. Default: reuse",
    )
    parser.add_argument(
        "--features-mode",
        choices=("reuse", "regenerate"),
        default="regenerate",
        help="Reuse existing features CSV or regenerate it from the processed CSV. Default: regenerate",
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=DEFAULT_RAW_DIR,
        help=f"Directory with raw NASDAQ CSV files. Default: {DEFAULT_RAW_DIR}",
    )
    parser.add_argument(
        "--processed-output",
        type=Path,
        default=DEFAULT_PROCESSED_FILE,
        help=f"Processed CSV path. Default: {DEFAULT_PROCESSED_FILE}",
    )
    parser.add_argument(
        "--processed-summary-output",
        type=Path,
        default=DEFAULT_SUMMARY_FILE,
        help=f"Preprocessing summary JSON path. Default: {DEFAULT_SUMMARY_FILE}",
    )
    parser.add_argument(
        "--features-output",
        type=Path,
        default=DEFAULT_FEATURES_TARGETS_FILE,
        help=f"Features + regression target CSV path. Default: {DEFAULT_FEATURES_TARGETS_FILE}",
    )
    parser.add_argument(
        "--features-summary-output",
        type=Path,
        default=DEFAULT_FEATURES_SUMMARY_FILE,
        help=f"Features + target summary JSON path. Default: {DEFAULT_FEATURES_SUMMARY_FILE}",
    )
    parser.add_argument(
        "--target-horizon-days",
        type=int,
        default=10,
        help="Future trading days used for max drawdown target. Default: 10",
    )
    parser.add_argument(
        "--symbols",
        nargs="+",
        default=list(SELECTED_SYMBOLS),
        help="Symbols to keep and validate.",
    )
    parser.add_argument(
        "--figures-dir",
        type=Path,
        default=FIGURES_DIR,
        help=f"Directory for generated SVG figures. Default: {FIGURES_DIR}",
    )
    parser.add_argument(
        "--progress-interval",
        type=int,
        default=250,
        help="Print progress after this many raw CSV files. Default: 250",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Run without progress messages.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    processed_validation, processed_rows = _run_processed_step(args)
    if args.step == "preprocess":
        print(f"Processed rows: {processed_rows:,}")
        print(f"Processed validation: {processed_validation['status']}")
        print(f"Processed CSV: {args.processed_output}")
        return

    features_validation = _run_features_step(args)

    print(f"Processed rows: {processed_rows:,}")
    print(f"Processed validation: {processed_validation['status']}")
    print(f"Processed CSV: {args.processed_output}")
    print(f"Features + target rows: {features_validation['rows_validated']:,}")
    print(f"Features + target validation: {features_validation['status']}")
    print(f"Features + target CSV: {args.features_output}")


def _run_processed_step(args: argparse.Namespace) -> tuple[dict, int]:
    if args.step == "features" or args.processed_mode == "reuse":
        if not args.quiet:
            print(f"Reusing processed OHLCV dataset: {args.processed_output}", flush=True)
        validation = validate_processed_csv(args.processed_output, args.symbols)
        return validation, validation["rows_validated"]

    if not args.quiet:
        print("Regenerating processed OHLCV dataset from raw CSV files...", flush=True)
    result = build_processed_dataset(
        raw_dir=args.raw_dir,
        output_path=args.processed_output,
        summary_output_path=args.processed_summary_output,
        figures_dir=args.figures_dir,
        symbols=args.symbols,
        progress_callback=None if args.quiet else _print_progress,
        progress_interval_files=args.progress_interval,
    )
    return result["validation"], result["rows_processed"]


def _run_features_step(args: argparse.Namespace) -> dict:
    if args.features_mode == "reuse":
        if not args.quiet:
            print(f"Reusing features + target dataset: {args.features_output}", flush=True)
        return validate_features_targets_csv(args.features_output, args.symbols)

    if not args.quiet:
        print("Regenerating drawdown regression features...", flush=True)
    result = build_features_dataset(
        processed_csv_path=args.processed_output,
        output_path=args.features_output,
        summary_output_path=args.features_summary_output,
        figures_dir=args.figures_dir,
        symbols=args.symbols,
        target_horizon_days=args.target_horizon_days,
    )
    return result["validation"]


def _print_progress(
    processed_files: int,
    total_files: int,
    csv_path: Path,
    rows_read: int,
    rows_selected: int,
) -> None:
    print(
        f"[{processed_files:,}/{total_files:,}] {csv_path.name} | "
        f"rows read: {rows_read:,} | selected: {rows_selected:,}",
        flush=True,
    )


if __name__ == "__main__":
    main()
