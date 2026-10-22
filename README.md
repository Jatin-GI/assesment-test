# Device Log Summarizer

CLI tool for a Software Engineering Intern coding assessment.

It cleans mixed sensor readings, aggregates device telemetry from CSV, exports JSON, prints a terminal summary table, and charts average temperatures.

## Project structure

```text
assement/
├── main.py                 # Unified CLI entrypoint
├── requirements.txt
├── PROMPT_LOG.md           # Section 3 AI collaboration log
├── README.md
├── data/
│   └── device_telemetry.csv
├── src/
│   ├── sanitize.py         # Section 1 — sensor cleaning
│   ├── summarizer.py       # Section 2 — CSV → aggregate → JSON
│   └── visualize.py        # Section 3 — matplotlib bar chart
├── tests/
│   └── test_sanitize.py
├── output/                 # Generated at runtime
│   ├── summary.json
│   └── avg_temp_chart.png
└── sample_output/
    ├── summary.json        # Checked-in sample deliverable
    └── avg_temp_chart.png
```

## Setup

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
```

## Run

```bash
# Section 1 demos
python main.py sanitize

# Section 1 unit tests
python -m unittest tests.test_sanitize -v

# Section 2 — summarize telemetry
python main.py summarize

# Section 3 — chart from JSON
python main.py chart

# Full pipeline
python main.py all
```

### Robustness checks

```bash
# Missing CSV → clear error, non-zero exit (does not crash)
python main.py summarize --input data/missing.csv

# Bad rows in the provided CSV are skipped with warnings; valid rows still process
python main.py summarize
```

## Section checklist

| Section | Deliverable | Location |
|--------|-------------|----------|
| 1 | `clean_sensor_readings` + tests | `src/sanitize.py`, `tests/test_sanitize.py` |
| 2 | CSV ingest, aggregate, filter ≤80°C avg, JSON + table | `src/summarizer.py`, `data/device_telemetry.csv` |
| 3 | Chart + AI prompt log | `src/visualize.py`, `PROMPT_LOG.md` |
| Submission | Sample output | `sample_output/` |

## Evaluation criteria mapping

- **Readability** — clear module split, typed helpers, descriptive names.
- **Robustness** — missing/empty CSV, bad headers, invalid temperatures handled without uncaught crashes.
- **AI collaboration** — `PROMPT_LOG.md` records the initial prompt, a real layout bug, and the fix prompt.
