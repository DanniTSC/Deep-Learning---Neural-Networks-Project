from __future__ import annotations

from html import escape
from pathlib import Path

import pandas as pd

from src.config import TARGET_COLUMN


def write_project_figures(
    features_csv_path: Path,
    output_dir: Path,
    target_column: str = TARGET_COLUMN,
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    data = pd.read_csv(features_csv_path, parse_dates=["Date"])

    figure_paths = [
        output_dir / "data_quality_observations_by_symbol.svg",
        output_dir / "target_future_drawdown_distribution.svg",
        output_dir / "target_average_drawdown_by_symbol.svg",
        output_dir / "target_drawdown_over_time.svg",
    ]

    _write_observations_by_symbol(data, figure_paths[0])
    _write_target_distribution(data, target_column, figure_paths[1])
    _write_average_drawdown_by_symbol(data, target_column, figure_paths[2])
    _write_target_over_time(data, target_column, figure_paths[3])

    return figure_paths


def _write_observations_by_symbol(data: pd.DataFrame, output_path: Path) -> None:
    values = data.groupby("Symbol").size().sort_values(ascending=True)
    _write_horizontal_bar_chart(
        output_path=output_path,
        title="Observatii disponibile pentru modelare pe simbol",
        values=values,
        value_formatter=lambda value: _format_number(value),
        color="#2563eb",
    )


def _write_average_drawdown_by_symbol(
    data: pd.DataFrame,
    target_column: str,
    output_path: Path,
) -> None:
    values = (data.groupby("Symbol")[target_column].mean() * 100).sort_values(ascending=True)
    _write_horizontal_bar_chart(
        output_path=output_path,
        title="Drawdown viitor mediu pe simbol",
        values=values,
        value_formatter=lambda value: f"{value:.2f}%",
        color="#dc2626",
    )


def _write_target_distribution(
    data: pd.DataFrame,
    target_column: str,
    output_path: Path,
) -> None:
    target_pct = data[target_column] * 100
    bins = 30
    counts = pd.cut(target_pct, bins=bins).value_counts(sort=False)
    max_count = int(counts.max())

    width, height = 1050, 620
    left, top, plot_width, plot_height = 90, 70, 850, 410
    bottom = top + plot_height
    bar_gap = 3
    bar_width = (plot_width - bar_gap * (bins - 1)) / bins

    lines = [_svg_header(width, height, "Distributia targetului future max drawdown 10d")]
    lines.append(_axis(left, top, plot_width, plot_height))
    lines.append(_text(35, 42, "Distributia targetului future max drawdown 10d", 24, "bold"))
    lines.append(_text(left, bottom + 46, f"{target_pct.min():.1f}%", 13))
    lines.append(_text(left + plot_width - 55, bottom + 46, f"{target_pct.max():.1f}%", 13))
    lines.append(_text(25, top + 10, _format_number(max_count), 12))
    lines.append(_text(42, bottom, "0", 12))
    lines.append(_text(left + 300, height - 34, "Drawdown maxim viitor pe 10 zile (%)", 14))

    for index, count in enumerate(counts):
        x = left + index * (bar_width + bar_gap)
        bar_height = _scale(float(count), 0, max_count, 0, plot_height)
        y = bottom - bar_height
        lines.append(
            f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_width:.2f}" '
            f'height="{bar_height:.2f}" fill="#0f766e" />'
        )

    lines.append("</svg>")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def _write_target_over_time(
    data: pd.DataFrame,
    target_column: str,
    output_path: Path,
) -> None:
    series = (data.groupby("Date")[target_column].mean() * 100).sort_index()
    dates = series.index
    values = series.to_numpy()
    min_date, max_date = dates.min(), dates.max()
    min_value, max_value = float(values.min()), float(values.max())

    width, height = 1100, 650
    left, top, plot_width, plot_height = 90, 70, 860, 430
    bottom = top + plot_height

    lines = [_svg_header(width, height, "Drawdown viitor mediu in timp")]
    lines.append(_axis(left, top, plot_width, plot_height))
    lines.append(_text(35, 42, "Drawdown viitor mediu in timp", 24, "bold"))
    lines.append(_text(left, bottom + 46, min_date.date().isoformat(), 13))
    lines.append(_text(left + plot_width - 85, bottom + 46, max_date.date().isoformat(), 13))
    lines.append(_text(20, top + 10, f"{max_value:.2f}%", 12))
    lines.append(_text(20, bottom, f"{min_value:.2f}%", 12))
    lines.append(_text(left + 315, height - 34, "Data observatiei", 14))

    points = []
    for point_date, value in series.items():
        x = _scale(
            float(point_date.toordinal()),
            float(min_date.toordinal()),
            float(max_date.toordinal()),
            left,
            left + plot_width,
        )
        y = _scale(float(value), min_value, max_value, bottom, top)
        points.append(f"{x:.2f},{y:.2f}")

    lines.append(
        f'<polyline fill="none" stroke="#7c3aed" stroke-width="1.8" '
        f'points="{" ".join(points)}" />'
    )

    lines.append("</svg>")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def _write_horizontal_bar_chart(
    output_path: Path,
    title: str,
    values: pd.Series,
    value_formatter,
    color: str,
) -> None:
    row_height = 22
    width = 1120
    height = 115 + len(values) * row_height
    left, top, plot_width = 145, 65, 780
    max_value = float(values.max()) if len(values) else 1.0

    lines = [_svg_header(width, height, title)]
    lines.append(_text(35, 42, title, 24, "bold"))
    lines.append(
        f'<line x1="{left}" y1="{top - 10}" x2="{left}" y2="{height - 50}" stroke="#334155" />'
    )

    for index, (symbol, value) in enumerate(values.items()):
        y = top + index * row_height
        bar_width = _scale(float(value), 0, max_value, 0, plot_width)
        lines.append(_text(35, y + 13, str(symbol), 12))
        lines.append(
            f'<rect x="{left}" y="{y:.2f}" width="{bar_width:.2f}" '
            f'height="14" fill="{color}" />'
        )
        lines.append(_text(left + bar_width + 8, y + 12, value_formatter(float(value)), 11))

    lines.append("</svg>")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def _svg_header(width: int, height: int, title: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}">'
        '<rect width="100%" height="100%" fill="#ffffff" />'
    )


def _axis(left: int, top: int, plot_width: int, plot_height: int) -> str:
    bottom = top + plot_height
    right = left + plot_width
    return (
        f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="#334155" />'
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" stroke="#334155" />'
        f'<line x1="{left}" y1="{top}" x2="{right}" y2="{top}" stroke="#e2e8f0" />'
        f'<line x1="{right}" y1="{top}" x2="{right}" y2="{bottom}" stroke="#e2e8f0" />'
    )


def _text(x: float, y: float, value: str, size: int, weight: str = "normal") -> str:
    return (
        f'<text x="{x:.2f}" y="{y:.2f}" font-family="Arial, sans-serif" '
        f'font-size="{size}" font-weight="{weight}" fill="#0f172a">{escape(value)}</text>'
    )


def _scale(
    value: float,
    source_min: float,
    source_max: float,
    target_min: float,
    target_max: float,
) -> float:
    if source_max == source_min:
        return (target_min + target_max) / 2
    return target_min + (value - source_min) * (target_max - target_min) / (source_max - source_min)


def _format_number(value: float | int) -> str:
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if abs(value) >= 1_000:
        return f"{value / 1_000:.1f}K"
    return f"{value:,.0f}"
