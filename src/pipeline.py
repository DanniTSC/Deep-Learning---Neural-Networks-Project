from __future__ import annotations

from pathlib import Path
from typing import Any

from src.indicators import build_features_targets
from src.plots import write_project_figures
from src.preprocessing import (
    ProgressCallback,
    preprocess_nasdaq_data,
    validate_processed_rows,
    write_processed_csv,
    write_summary_json,
)
from src.validation import validate_features_targets_csv, validate_processed_csv


def build_processed_dataset(
    raw_dir: Path,
    output_path: Path,
    summary_output_path: Path,
    figures_dir: Path,
    symbols: list[str] | tuple[str, ...],
    progress_callback: ProgressCallback | None = None,
    progress_interval_files: int = 250,
) -> dict[str, Any]:
    result = preprocess_nasdaq_data(
        raw_dir=raw_dir,
        symbols=symbols,
        progress_callback=progress_callback,
        progress_interval_files=progress_interval_files,
    )

    validate_processed_rows(result.rows, expected_symbols=symbols)
    write_processed_csv(result.rows, output_path)
    csv_validation = validate_processed_csv(output_path, symbols)

    summary = dict(result.summary)
    summary["processed_csv_validation"] = csv_validation
    summary["output_files"] = {
        "processed_csv": str(output_path),
        "summary_json": str(summary_output_path),
    }
    write_summary_json(summary, summary_output_path)

    return {
        "rows_processed": len(result.rows),
        "validation": csv_validation,
        "summary": summary,
        "figure_paths": [],
    }


def build_features_dataset(
    processed_csv_path: Path,
    output_path: Path,
    summary_output_path: Path,
    figures_dir: Path,
    symbols: list[str] | tuple[str, ...],
    target_horizon_days: int = 10,
) -> dict[str, Any]:
    summary = build_features_targets(
        processed_csv_path=processed_csv_path,
        output_path=output_path,
        target_horizon_days=target_horizon_days,
    )
    validation = validate_features_targets_csv(output_path, symbols)
    figure_paths = write_project_figures(output_path, figures_dir)

    summary["features_targets_csv_validation"] = validation
    summary["output_files"] = {
        "features_targets_csv": str(output_path),
        "features_summary_json": str(summary_output_path),
        "figures": [str(path) for path in figure_paths],
    }
    write_summary_json(summary, summary_output_path)

    return {
        "rows_processed": validation["rows_validated"],
        "validation": validation,
        "summary": summary,
        "figure_paths": figure_paths,
    }
