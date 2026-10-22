#!/usr/bin/env python3
"""
Device Log Summarizer CLI

Commands:
  sanitize   Section 1 — clean mixed sensor readings
  summarize  Section 2 — aggregate telemetry CSV → JSON + table
  chart      Section 3 — bar chart from summary JSON
  all        Run summarize then chart
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.sanitize import clean_sensor_readings
from src.summarizer import main as summarize_main
from src.visualize import main as chart_main


def cmd_sanitize(_: argparse.Namespace) -> int:
    demos = [
        [10, "20.5", None, -3, "bad", 600, 0],
        [],
        [None, "x", -1, -99.9],
    ]
    print("Section 1 — clean_sensor_readings demos\n")
    for demo in demos:
        print(f"  {demo!r}")
        print(f"  -> {clean_sensor_readings(demo)}\n")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="device-log-summarizer",
        description="Device Log Summarizer — clean, aggregate, and chart telemetry.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("sanitize", help="Run Section 1 sensor cleaning demos")

    summarize = sub.add_parser("summarize", help="Run Section 2 CSV summarizer")
    summarize.add_argument("--input", type=Path, default=Path("data/device_telemetry.csv"))
    summarize.add_argument("--output", type=Path, default=Path("output/summary.json"))
    summarize.add_argument("--max-avg", type=float, default=80.0)

    chart = sub.add_parser("chart", help="Run Section 3 visualization")
    chart.add_argument("--input", type=Path, default=Path("output/summary.json"))
    chart.add_argument("--output", type=Path, default=Path("output/avg_temp_chart.png"))

    all_cmd = sub.add_parser("all", help="Run summarize then chart")
    all_cmd.add_argument("--input", type=Path, default=Path("data/device_telemetry.csv"))
    all_cmd.add_argument("--json", type=Path, default=Path("output/summary.json"))
    all_cmd.add_argument("--chart", type=Path, default=Path("output/avg_temp_chart.png"))
    all_cmd.add_argument("--max-avg", type=float, default=80.0)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "sanitize":
        return cmd_sanitize(args)

    if args.command == "summarize":
        return summarize_main(
            [
                "--input",
                str(args.input),
                "--output",
                str(args.output),
                "--max-avg",
                str(args.max_avg),
            ]
        )

    if args.command == "chart":
        return chart_main(["--input", str(args.input), "--output", str(args.output)])

    if args.command == "all":
        code = summarize_main(
            [
                "--input",
                str(args.input),
                "--output",
                str(args.json),
                "--max-avg",
                str(args.max_avg),
            ]
        )
        if code != 0:
            return code
        return chart_main(["--input", str(args.json), "--output", str(args.chart)])

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
