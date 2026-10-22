"""
Section 2: Device telemetry CSV ingestion, aggregation, filtering, and export.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


@dataclass
class DeviceSummary:
    device_id: str
    record_count: int
    average_temperature: float
    error_count: int


def _safe_float(raw: Optional[str]) -> Optional[float]:
    if raw is None:
        return None
    text = str(raw).strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def load_telemetry(csv_path: Path) -> List[Dict[str, str]]:
    """Read CSV rows. Raises FileNotFoundError / ValueError with clear messages."""
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    if csv_path.stat().st_size == 0:
        raise ValueError(f"CSV file is empty: {csv_path}")

    required = {"device_id", "status", "temperature"}
    rows: List[Dict[str, str]] = []

    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"CSV has no header row: {csv_path}")

        headers = {name.strip() for name in reader.fieldnames if name}
        missing = required - headers
        if missing:
            raise ValueError(
                f"CSV missing required columns {sorted(missing)}. "
                f"Found: {sorted(headers)}"
            )

        for line_no, row in enumerate(reader, start=2):
            device_id = (row.get("device_id") or "").strip()
            status = (row.get("status") or "").strip().upper()
            temperature = _safe_float(row.get("temperature"))

            if not device_id:
                print(
                    f"Warning: skipping row {line_no} — missing device_id",
                    file=sys.stderr,
                )
                continue

            if temperature is None:
                print(
                    f"Warning: skipping row {line_no} for {device_id} — "
                    f"invalid temperature {row.get('temperature')!r}",
                    file=sys.stderr,
                )
                continue

            rows.append(
                {
                    "device_id": device_id,
                    "status": status or "UNKNOWN",
                    "temperature": temperature,
                }
            )

    return rows


def aggregate_by_device(rows: Iterable[Dict]) -> List[DeviceSummary]:
    totals: Dict[str, float] = defaultdict(float)
    counts: Dict[str, int] = defaultdict(int)
    errors: Dict[str, int] = defaultdict(int)

    for row in rows:
        device_id = row["device_id"]
        totals[device_id] += float(row["temperature"])
        counts[device_id] += 1
        if row["status"] == "ERROR":
            errors[device_id] += 1

    summaries: List[DeviceSummary] = []
    for device_id in sorted(counts):
        record_count = counts[device_id]
        average = totals[device_id] / record_count
        summaries.append(
            DeviceSummary(
                device_id=device_id,
                record_count=record_count,
                average_temperature=round(average, 2),
                error_count=errors[device_id],
            )
        )
    return summaries


def filter_by_avg_temperature(
    summaries: List[DeviceSummary], max_avg: float = 80.0
) -> List[DeviceSummary]:
    """Keep devices whose average temperature is <= max_avg."""
    return [item for item in summaries if item.average_temperature <= max_avg]


def export_json(summaries: List[DeviceSummary], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = [asdict(item) for item in summaries]
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")


def print_summary_table(summaries: List[DeviceSummary]) -> None:
    if not summaries:
        print("No devices passed the average-temperature filter.")
        return

    headers = ("device_id", "records", "avg_temp", "errors")
    rows: List[Tuple[str, str, str, str]] = [
        (
            item.device_id,
            str(item.record_count),
            f"{item.average_temperature:.2f}",
            str(item.error_count),
        )
        for item in summaries
    ]

    widths = [
        max(len(headers[i]), *(len(row[i]) for row in rows))
        for i in range(len(headers))
    ]

    def fmt(cols: Tuple[str, ...]) -> str:
        return "  ".join(col.ljust(widths[i]) for i, col in enumerate(cols))

    print(fmt(headers))
    print(fmt(tuple("-" * w for w in widths)))
    for row in rows:
        print(fmt(row))


def process_telemetry(
    csv_path: Path,
    json_path: Path,
    max_avg: float = 80.0,
) -> List[DeviceSummary]:
    rows = load_telemetry(csv_path)
    if not rows:
        print(
            "Warning: no valid telemetry rows after cleaning.",
            file=sys.stderr,
        )
        export_json([], json_path)
        print_summary_table([])
        return []

    all_summaries = aggregate_by_device(rows)
    filtered = filter_by_avg_temperature(all_summaries, max_avg=max_avg)
    export_json(filtered, json_path)
    print_summary_table(filtered)
    print(f"\nWrote JSON summary to: {json_path}")
    return filtered


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Device Log Summarizer — aggregate and filter telemetry CSV."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/device_telemetry.csv"),
        help="Path to device_telemetry.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/summary.json"),
        help="Path for aggregated JSON output",
    )
    parser.add_argument(
        "--max-avg",
        type=float,
        default=80.0,
        help="Exclude devices with average temperature above this value",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        process_telemetry(args.input, args.output, max_avg=args.max_avg)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"Error reading/writing files: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
