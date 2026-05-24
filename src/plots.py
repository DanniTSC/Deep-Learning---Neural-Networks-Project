from __future__ import annotations

from collections import defaultdict
from datetime import date
from html import escape
from pathlib import Path
from typing import Any


COLORS = {
    "AAPL": "#2563eb",
    "MSFT": "#16a34a",
    "NVDA": "#9333ea",
    "AMZN": "#ea580c",
    "GOOGL": "#dc2626",
}


def write_data_quality_figures(rows: list[dict[str, Any]], output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)

    figure_paths = [
        output_dir / "close_price_evolution.svg",
        output_dir / "average_volume_by_symbol.svg",
        output_dir / "observations_by_symbol.svg",
    ]

    _write_close_price_evolution(rows, figure_paths[0])
    _write_average_volume_by_symbol(rows, figure_paths[1])
    _write_observations_by_symbol(rows, figure_paths[2])

    return figure_paths


def _write_close_price_evolution(rows: list[dict[str, Any]], output_path: Path) -> None:
    grouped: dict[str, list[tuple[date, float]]] = defaultdict(list)
    for row in rows:
        grouped[row["Symbol"]].append((date.fromisoformat(row["Date"]), float(row["Close"])))

    all_dates = [point_date for points in grouped.values() for point_date, _ in points]
    all_values = [close for points in grouped.values() for _, close in points]
    min_date, max_date = min(all_dates), max(all_dates)
    min_close, max_close = min(all_values), max(all_values)

    width, height = 1100, 650
    left, top, plot_width, plot_height = 85, 60, 880, 480
    bottom = top + plot_height

    lines = [_svg_header(width, height, "Evolutia pretului Close")]
    lines.append(_axis(left, top, plot_width, plot_height))
    lines.append(_text(35, 38, "Evolutia pretului Close", 24, "bold"))
    lines.append(_text(left, bottom + 45, min_date.isoformat(), 13))
    lines.append(_text(left + plot_width - 80, bottom + 45, max_date.isoformat(), 13))
    lines.append(_text(18, top + 12, f"{max_close:,.2f}", 12))
    lines.append(_text(18, bottom, f"{min_close:,.2f}", 12))

    for index, (symbol, points) in enumerate(sorted(grouped.items())):
        color = COLORS.get(symbol, "#334155")
        point_pairs = []
        for point_date, close in points:
            x = _scale(point_date.toordinal(), min_date.toordinal(), max_date.toordinal(), left, left + plot_width)
            y = _scale(close, min_close, max_close, bottom, top)
            point_pairs.append(f"{x:.2f},{y:.2f}")

        lines.append(
            f'<polyline fill="none" stroke="{color}" stroke-width="1.5" '
            f'points="{" ".join(point_pairs)}" />'
        )
        legend_y = top + 8 + index * 25
        lines.append(f'<rect x="990" y="{legend_y - 10}" width="14" height="14" fill="{color}" />')
        lines.append(_text(1012, legend_y + 2, symbol, 14))

    lines.append("</svg>")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def _write_average_volume_by_symbol(rows: list[dict[str, Any]], output_path: Path) -> None:
    totals: dict[str, int] = defaultdict(int)
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        symbol = row["Symbol"]
        totals[symbol] += int(row["Volume"])
        counts[symbol] += 1

    averages = {symbol: totals[symbol] / counts[symbol] for symbol in counts}
    _write_bar_chart(
        output_path=output_path,
        title="Volum mediu tranzactionat pe simbol",
        values=averages,
        value_suffix="",
    )


def _write_observations_by_symbol(rows: list[dict[str, Any]], output_path: Path) -> None:
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        counts[row["Symbol"]] += 1

    _write_bar_chart(
        output_path=output_path,
        title="Numar de observatii pe simbol",
        values=dict(counts),
        value_suffix=" randuri",
    )


def _write_bar_chart(
    output_path: Path,
    title: str,
    values: dict[str, float | int],
    value_suffix: str,
) -> None:
    width, height = 950, 560
    left, top, plot_width, plot_height = 85, 65, 760, 380
    bottom = top + plot_height
    max_value = max(values.values()) if values else 1
    symbols = sorted(values)
    bar_gap = 28
    bar_width = (plot_width - bar_gap * (len(symbols) + 1)) / max(len(symbols), 1)

    lines = [_svg_header(width, height, title)]
    lines.append(_axis(left, top, plot_width, plot_height))
    lines.append(_text(35, 38, title, 24, "bold"))
    lines.append(_text(18, top + 12, _format_number(max_value), 12))
    lines.append(_text(42, bottom, "0", 12))

    for index, symbol in enumerate(symbols):
        value = values[symbol]
        x = left + bar_gap + index * (bar_width + bar_gap)
        bar_height = _scale(value, 0, max_value, 0, plot_height)
        y = bottom - bar_height
        color = COLORS.get(symbol, "#334155")
        lines.append(
            f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_width:.2f}" '
            f'height="{bar_height:.2f}" fill="{color}" />'
        )
        lines.append(_text(x + bar_width / 2 - 18, bottom + 28, symbol, 14))
        lines.append(
            _text(
                x + bar_width / 2 - 42,
                y - 10,
                f"{_format_number(value)}{value_suffix}",
                12,
            )
        )

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


def plot_close_prices(df, output_dir: Path) -> list[Path]:
    import matplotlib.pyplot as plt

    output_dir.mkdir(parents=True, exist_ok=True)
    saved_paths: list[Path] = []

    for symbol, symbol_df in df.groupby("Symbol"):
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(symbol_df["Date"], symbol_df["Close"])
        ax.set_title(f"Close price - {symbol}")
        ax.set_xlabel("Date")
        ax.set_ylabel("Close")
        ax.grid(True, alpha=0.3)
        fig.autofmt_xdate()

        output_path = output_dir / f"{symbol.lower()}_close_price.png"
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        saved_paths.append(output_path)

    return saved_paths
