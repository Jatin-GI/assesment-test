"""
Section 3: Load Section 2 JSON and render a bar chart of average temperature.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional, Tuple


def load_summaries(json_path: Path) -> List[dict]:
    if not json_path.exists():
        raise FileNotFoundError(f"JSON file not found: {json_path}")

    with json_path.open(encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, list):
        raise ValueError("Expected a JSON array of device summaries.")

    return data


def extract_chart_series(summaries: List[dict]) -> Tuple[List[str], List[float]]:
    device_ids: List[str] = []
    averages: List[float] = []

    for item in summaries:
        device_id = item.get("device_id")
        avg = item.get("average_temperature")
        if device_id is None or avg is None:
            continue
        try:
            averages.append(float(avg))
        except (TypeError, ValueError):
            continue
        device_ids.append(str(device_id))

    return device_ids, averages


def create_bar_chart(
    device_ids: List[str],
    averages: List[float],
    output_path: Path,
    title: str = "Average Temperature by Device",
) -> Path:
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise ImportError(
            "matplotlib is required. Install with: pip install matplotlib"
        ) from exc

    if not device_ids:
        raise ValueError("No device data available to chart.")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(device_ids, averages, color="#2F6FED", edgecolor="white")

    ax.set_title(title, fontsize=14, pad=16)
    ax.set_xlabel("Device ID", fontsize=11)
    ax.set_ylabel("Average Temperature (°C)", fontsize=11)
    ax.set_ylim(0, max(averages) * 1.15 if averages else 1)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.tick_params(axis="x", labelrotation=30)

    for bar, value in zip(bars, averages):
        ax.annotate(
            f"{value:.1f}",
            xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    fig.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return output_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Plot average temperature per device from summary JSON."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("output/summary.json"),
        help="Path to Section 2 JSON output",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/avg_temp_chart.png"),
        help="Path for the generated bar chart image",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        summaries = load_summaries(args.input)
        device_ids, averages = extract_chart_series(summaries)
        chart_path = create_bar_chart(device_ids, averages, args.output)
    except (FileNotFoundError, ValueError, ImportError, OSError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Chart saved to: {chart_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
