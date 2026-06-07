from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.config import REQUIRED_COLUMNS, TARGET_COLUMN


FEATURE_COLUMNS = (
    "daily_return",
    "log_return_1d",
    "return_5d",
    "return_10d",
    "return_20d",
    "intraday_range",
    "open_close_return",
    "volume_change_1d",
    "volume_ratio_20d",
    "sma_5",
    "sma_10",
    "sma_20",
    "sma_60",
    "ma_5_ratio",
    "ma_20_ratio",
    "ma_60_ratio",
    "volatility_5d",
    "volatility_10d",
    "volatility_20d",
    "volatility_60d",
    "past_max_drawdown_10d",
    "past_max_drawdown_20d",
    "past_max_drawdown_60d",
    "return_lag_1",
    "return_lag_2",
    "return_lag_3",
    "return_lag_5",
)

FEATURE_TARGET_COLUMNS = REQUIRED_COLUMNS + FEATURE_COLUMNS + (TARGET_COLUMN,)


def build_features_targets(
    processed_csv_path: Path,
    output_path: Path,
    target_horizon_days: int = 10,
) -> dict[str, Any]:
    data = read_processed_panel(processed_csv_path)
    features = add_drawdown_features(data, target_horizon_days=target_horizon_days)
    modeling_data = prepare_modeling_dataset(features)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    modeling_data.to_csv(output_path, index=False)

    return summarize_features_targets(
        source_rows=len(data),
        output_rows=len(modeling_data),
        target_horizon_days=target_horizon_days,
        data=modeling_data,
    )


def read_processed_panel(processed_csv_path: Path) -> pd.DataFrame:
    data = pd.read_csv(processed_csv_path)
    expected_columns = list(REQUIRED_COLUMNS)
    if list(data.columns) != expected_columns:
        raise ValueError(
            f"Invalid processed columns: {list(data.columns)}. Expected: {expected_columns}"
        )

    data["Date"] = pd.to_datetime(data["Date"], errors="raise")
    numeric_columns = ["Open", "High", "Low", "Close", "Volume"]
    data[numeric_columns] = data[numeric_columns].apply(pd.to_numeric, errors="raise")
    data["Symbol"] = data["Symbol"].astype(str).str.upper().str.strip()
    return data.sort_values(["Symbol", "Date"]).reset_index(drop=True)


def add_drawdown_features(
    df: pd.DataFrame,
    target_horizon_days: int = 10,
) -> pd.DataFrame:
    """Add regression features and the future max drawdown target."""
    data = df.copy()
    grouped = data.groupby("Symbol", group_keys=False)

    data["daily_return"] = grouped["Close"].pct_change()
    data["log_return_1d"] = np.log(data["Close"] / grouped["Close"].shift(1))
    data["return_5d"] = grouped["Close"].pct_change(periods=5)
    data["return_10d"] = grouped["Close"].pct_change(periods=10)
    data["return_20d"] = grouped["Close"].pct_change(periods=20)
    data["intraday_range"] = (data["High"] - data["Low"]) / data["Open"]
    data["open_close_return"] = (data["Close"] - data["Open"]) / data["Open"]
    data["volume_change_1d"] = grouped["Volume"].pct_change()

    rolling_volume_20 = grouped["Volume"].transform(
        lambda series: series.rolling(20, min_periods=20).mean()
    )
    data["volume_ratio_20d"] = data["Volume"] / rolling_volume_20

    for window in (5, 10, 20, 60):
        data[f"sma_{window}"] = grouped["Close"].transform(
            lambda series, w=window: series.rolling(w, min_periods=w).mean()
        )
        data[f"volatility_{window}d"] = grouped["daily_return"].transform(
            lambda series, w=window: series.rolling(w, min_periods=w).std()
        )

    data["ma_5_ratio"] = data["Close"] / data["sma_5"]
    data["ma_20_ratio"] = data["Close"] / data["sma_20"]
    data["ma_60_ratio"] = data["Close"] / data["sma_60"]

    for window in (10, 20, 60):
        data[f"past_max_drawdown_{window}d"] = grouped["Close"].transform(
            lambda series, w=window: _past_max_drawdown(series, w)
        )

    for lag in (1, 2, 3, 5):
        data[f"return_lag_{lag}"] = grouped["daily_return"].shift(lag)

    data[TARGET_COLUMN] = grouped["Close"].transform(
        lambda series: _future_max_drawdown(series, target_horizon_days)
    )
    return data


def prepare_modeling_dataset(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    data["Date"] = pd.to_datetime(data["Date"]).dt.date.astype(str)
    data = data.replace([np.inf, -np.inf], np.nan)
    data = data.dropna(subset=list(FEATURE_COLUMNS) + [TARGET_COLUMN])
    data = data.loc[:, FEATURE_TARGET_COLUMNS]
    return data.sort_values(["Symbol", "Date"]).reset_index(drop=True)


def summarize_features_targets(
    source_rows: int,
    output_rows: int,
    target_horizon_days: int,
    data: pd.DataFrame,
) -> dict[str, Any]:
    rows_by_symbol = (
        data.groupby("Symbol")
        .agg(rows=("Symbol", "size"), first_date=("Date", "min"), last_date=("Date", "max"))
        .sort_index()
        .to_dict(orient="index")
    )

    target = data[TARGET_COLUMN]
    return {
        "source_rows": int(source_rows),
        "rows_output": int(output_rows),
        "rows_dropped_for_features_or_target": int(source_rows - output_rows),
        "target_column": TARGET_COLUMN,
        "target_horizon_days": int(target_horizon_days),
        "feature_columns": list(FEATURE_COLUMNS),
        "rows_by_symbol": rows_by_symbol,
        "target_summary": {
            "min": float(target.min()),
            "mean": float(target.mean()),
            "median": float(target.median()),
            "max": float(target.max()),
            "zero_target_share": float((target == 0).mean()),
        },
    }


def _future_max_drawdown(close: pd.Series, horizon_days: int) -> pd.Series:
    future_returns = [
        close.shift(-day) / close - 1.0 for day in range(1, horizon_days + 1)
    ]
    worst_future_return = pd.concat(future_returns, axis=1).min(axis=1)
    target = (-worst_future_return).clip(lower=0)
    target.iloc[-horizon_days:] = np.nan
    return target


def _past_max_drawdown(close: pd.Series, window: int) -> pd.Series:
    return close.rolling(window, min_periods=window).apply(
        _window_max_drawdown,
        raw=True,
    )


def _window_max_drawdown(values: np.ndarray) -> float:
    running_peak = np.maximum.accumulate(values)
    drawdowns = (running_peak - values) / running_peak
    return float(np.max(drawdowns))
