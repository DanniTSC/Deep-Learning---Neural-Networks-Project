from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw_sample"
PROCESSED_DIR = DATA_DIR / "processed"

OUTPUTS_DIR = PROJECT_ROOT / "outputs"
FIGURES_DIR = OUTPUTS_DIR / "figures"
PREDICTIONS_DIR = OUTPUTS_DIR / "predictions"
METRICS_DIR = OUTPUTS_DIR / "metrics"

DEFAULT_RAW_DIR = RAW_DATA_DIR
DEFAULT_PROCESSED_FILE = PROCESSED_DIR / "processed_nasdaq.csv"
DEFAULT_SUMMARY_FILE = METRICS_DIR / "preprocessing_summary.json"

SELECTED_SYMBOLS = ("AAPL", "MSFT", "NVDA", "AMZN", "GOOGL")
REQUIRED_COLUMNS = ("Symbol", "Date", "Open", "High", "Low", "Close", "Volume")
PRICE_COLUMNS = ("Open", "High", "Low", "Close")
