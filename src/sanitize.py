"""
Section 1: Clean and normalize mixed sensor readings.
"""

from __future__ import annotations

from typing import Any, Iterable, List


def clean_sensor_readings(values: Iterable[Any]) -> List[float]:
    """
    Convert mixed sensor inputs into a cleaned list of non-negative floats.

    Rules:
    1. Convert to float where possible; drop None, non-numeric, and negative values.
    2. Clip any value above 500.0 to 500.0.
    3. Empty or fully-invalid inputs return [] without raising.
    """
    cleaned: List[float] = []

    if values is None:
        return cleaned

    for item in values:
        if item is None:
            continue

        try:
            number = float(item)
        except (TypeError, ValueError):
            continue

        if number < 0:
            continue

        if number > 500.0:
            number = 500.0

        cleaned.append(number)

    return cleaned


if __name__ == "__main__":
    # Simple manual checks (formal tests live in tests/test_sanitize.py)
    examples = [
        [10, "20.5", None, -3, "bad", 600, 0],
        [],
        [None, "x", -1, -99.9],
    ]
    for example in examples:
        print(f"input={example!r} -> {clean_sensor_readings(example)}")
