from __future__ import annotations


def add_technical_indicators(df):
    """Add basic technical indicators used by the modeling team."""
    data = df.copy()
    grouped = data.groupby("Symbol", group_keys=False)

    data["daily_return"] = grouped["Close"].pct_change()
    data["log_return"] = grouped["Close"].transform(
        lambda series: (series / series.shift(1)).map(_safe_log)
    )
    data["intraday_range"] = (data["High"] - data["Low"]) / data["Open"]
    data["close_open_change"] = (data["Close"] - data["Open"]) / data["Open"]
    data["volume_change"] = grouped["Volume"].pct_change()

    for window in (5, 10, 20):
        data[f"sma_{window}"] = grouped["Close"].transform(
            lambda series, w=window: series.rolling(w).mean()
        )
        data[f"volatility_{window}"] = grouped["daily_return"].transform(
            lambda series, w=window: series.rolling(w).std()
        )

    for lag in (1, 2, 3, 5):
        data[f"return_lag_{lag}"] = grouped["daily_return"].shift(lag)

    next_close = grouped["Close"].shift(-1)
    data["target_next_day"] = next_close.gt(data["Close"]).astype("Int64")
    data.loc[next_close.isna(), "target_next_day"] = None
    return data


def _safe_log(value):
    import math

    if value is None or value <= 0:
        return None
    return math.log(value)
