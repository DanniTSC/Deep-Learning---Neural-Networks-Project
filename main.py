from __future__ import annotations

import argparse
from pathlib import Path

from src.config import (
    DEFAULT_PROCESSED_FILE,
    DEFAULT_RAW_DIR,
    DEFAULT_SUMMARY_FILE,
    FIGURES_DIR,
    SELECTED_SYMBOLS,
)
from src.plots import write_data_quality_figures
from src.preprocessing import (
    preprocess_nasdaq_data,
    validate_processed_rows,
    write_processed_csv,
    write_summary_json,
)
from src.validation import validate_processed_csv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Preprocess daily NASDAQ CSV files for the selected symbols."
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=DEFAULT_RAW_DIR,
        help=f"Directory with raw NASDAQ CSV files. Default: {DEFAULT_RAW_DIR}",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_PROCESSED_FILE,
        help=f"Processed CSV output path. Default: {DEFAULT_PROCESSED_FILE}",
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=DEFAULT_SUMMARY_FILE,
        help=f"Preprocessing summary JSON path. Default: {DEFAULT_SUMMARY_FILE}",
    )
    parser.add_argument(
        "--symbols",
        nargs="+",
        default=list(SELECTED_SYMBOLS),
        help="Symbols to keep from the raw NASDAQ files.",
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
        help="Print progress after this many CSV files. Default: 250",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Run without progress messages.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not args.quiet:
        print("Starting NASDAQ preprocessing...", flush=True)
        print(
            "This reads thousands of daily CSV files and can take around 1-2 minutes.",
            flush=True,
        )

    progress_callback = None if args.quiet else _print_progress
    result = preprocess_nasdaq_data(
        raw_dir=args.raw_dir,
        symbols=args.symbols,
        progress_callback=progress_callback,
        progress_interval_files=args.progress_interval,
    )

    if not args.quiet:
        print("Validating processed rows in memory...", flush=True)
    validate_processed_rows(result.rows, expected_symbols=args.symbols)

    if not args.quiet:
        print(f"Writing processed CSV to {args.output}...", flush=True)
    write_processed_csv(result.rows, args.output)

    if not args.quiet:
        print("Validating written CSV file...", flush=True)
    csv_validation = validate_processed_csv(args.output, args.symbols)

    if not args.quiet:
        print(f"Generating SVG figures in {args.figures_dir}...", flush=True)
    figure_paths = write_data_quality_figures(result.rows, args.figures_dir)

    summary = dict(result.summary)
    summary["processed_csv_validation"] = csv_validation
    summary["output_files"] = {
        "processed_csv": str(args.output),
        "summary_json": str(args.summary_output),
        "figures": [str(path) for path in figure_paths],
    }

    if not args.quiet:
        print(f"Writing summary JSON to {args.summary_output}...", flush=True)
    write_summary_json(summary, args.summary_output)

    print(f"Processed rows: {len(result.rows):,}")
    print(f"Validation: {csv_validation['status']}")
    print(f"Processed CSV: {args.output}")
    print(f"Summary JSON: {args.summary_output}")
    print("Figures:")
    for figure_path in figure_paths:
        print(f"  - {figure_path}")


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
