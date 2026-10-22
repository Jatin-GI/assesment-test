"""Simple test cases for clean_sensor_readings (Section 1 deliverable)."""

from __future__ import annotations

import unittest

from src.sanitize import clean_sensor_readings


class TestCleanSensorReadings(unittest.TestCase):
    def test_mixed_valid_invalid_and_clipping(self) -> None:
        raw = [10, "20.5", None, -3, "bad", 600, 0, "  12 "]
        result = clean_sensor_readings(raw)
        self.assertEqual(result, [10.0, 20.5, 500.0, 0.0, 12.0])

    def test_empty_list_returns_empty(self) -> None:
        self.assertEqual(clean_sensor_readings([]), [])

    def test_all_invalid_returns_empty_without_crash(self) -> None:
        raw = [None, "x", -1, -99.9, {}, [], object()]
        self.assertEqual(clean_sensor_readings(raw), [])

    def test_none_input_returns_empty(self) -> None:
        self.assertEqual(clean_sensor_readings(None), [])


if __name__ == "__main__":
    unittest.main()
