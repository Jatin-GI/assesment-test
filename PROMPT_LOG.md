# Prompt Log — Section 3 (AI Prompting & Charting)

This file documents how an AI assistant was used to build the visualization helper, including a first-pass bug and the follow-up fix.

## Initial prompt

```text
Write a Python script that loads output/summary.json (a JSON array of objects with
device_id and average_temperature) and generates a matplotlib bar chart comparing
average temperature per device. Save the chart as output/avg_temp_chart.png.
Include a title, axis labels, and CLI arguments for input/output paths.
```

## Bug / formatting mistake in the first AI attempt

The first draft:

- Rotated x-tick labels but did **not** call `tight_layout()` / `bbox_inches="tight"`.
- Long device IDs overlapped the plot edge and the bottom of the figure was clipped when saved.
- Bars had no value labels, so close averages were hard to compare at a glance.

## Follow-up prompt used to fix it

```text
The saved chart clips the rotated x-axis labels and the title looks cramped.
Please fix layout by using fig.tight_layout(), save with bbox_inches='tight',
add a bit of top headroom on the y-axis, and annotate each bar with its
average temperature value.
```

## Result after review

The final `src/visualize.py` keeps the AI-generated structure but applies the layout fixes above (tight layout, padded y-limit, bar annotations, clear title/labels) instead of copying the flawed first version blindly.
