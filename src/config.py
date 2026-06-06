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
DEFAULT_FEATURES_TARGETS_FILE = PROCESSED_DIR / "features_targets_nasdaq.csv"
DEFAULT_SUMMARY_FILE = METRICS_DIR / "preprocessing_summary.json"
DEFAULT_FEATURES_SUMMARY_FILE = METRICS_DIR / "features_targets_summary.json"

SELECTED_SYMBOLS = (
    "NVDA",
    "AAPL",
    "MSFT",
    "AMZN",
    "GOOGL",
    "GOOG",
    "AVGO",
    "META",
    "TSLA",
    "MU",
    "WMT",
    "AMD",
    "ASML",
    "INTC",
    "CSCO",
    "COST",
    "LRCX",
    "ARM",
    "AMAT",
    "NFLX",
    "PLTR",
    "TXN",
    "KLAC",
    "LIN",
    "SNDK",
    "MRVL",
    "QCOM",
    "PANW",
    "ADI",
    "PEP",
    "TMUS",
    "STX",
    "AMGN",
    "APP",
    "WDC",
    "CRWD",
    "GILD",
    "ISRG",
    "SHOP",
    "HON",
    "BKNG",
    "PDD",
    "VRTX",
    "SBUX",
    "FTNT",
    "CDNS",
    "MAR",
    "ADBE",
    "ADP",
    "CEG",
)
REQUIRED_COLUMNS = ("Symbol", "Date", "Open", "High", "Low", "Close", "Volume")
PRICE_COLUMNS = ("Open", "High", "Low", "Close")
TARGET_COLUMN = "future_max_drawdown_10d"
