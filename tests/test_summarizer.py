"""Robustness tests for Section 2 telemetry processing."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.summarizer import (
    DeviceSummary,
    aggregate_by_device,
    filter_by_avg_temperature,
    load_telemetry,
    process_telemetry,
)


class TestSummarizer(unittest.TestCase):
    def test_missing_csv_raises_file_not_found(self) -> None:
        with self.assertRaises(FileNotFoundError):
            load_telemetry(Path("data/does_not_exist.csv"))

    def test_bad_temperature_rows_are_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "telemetry.csv"
            csv_path.write_text(
                "device_id,status,temperature\n"
                "DEV_A,ACTIVE,70\n"
                "DEV_A,ERROR,bad\n"
                "DEV_A,WARNING,\n"
                "DEV_B,ACTIVE,90\n",
                encoding="utf-8",
            )
            rows = load_telemetry(csv_path)
            self.assertEqual(len(rows), 2)
            summaries = aggregate_by_device(rows)
            filtered = filter_by_avg_temperature(summaries, max_avg=80.0)
            self.assertEqual([s.device_id for s in filtered], ["DEV_A"])

    def test_process_writes_json_and_filters(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "telemetry.csv"
            json_path = Path(tmp) / "out.json"
            csv_path.write_text(
                "device_id,status,temperature\n"
                "DEV_OK,ACTIVE,50\n"
                "DEV_OK,ERROR,60\n"
                "DEV_HOT,ACTIVE,90\n"
                "DEV_HOT,WARNING,95\n",
                encoding="utf-8",
            )
            result = process_telemetry(csv_path, json_path, max_avg=80.0)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].device_id, "DEV_OK")
            self.assertEqual(result[0].error_count, 1)
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(payload[0]["average_temperature"], 55.0)


if __name__ == "__main__":
    unittest.main()
