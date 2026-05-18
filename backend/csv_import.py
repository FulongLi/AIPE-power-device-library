from __future__ import annotations

import csv
import io
from typing import Any


def parse_curve_csv(
    csv_text: str,
    *,
    curve_id: str,
    curve_type: str,
    x_label: str,
    x_unit: str,
    y_label: str,
    y_unit: str,
    source_id: str,
    condition: dict[str, Any] | None = None,
) -> dict[str, Any]:
    reader = csv.reader(io.StringIO(csv_text.strip()))
    points: list[list[float]] = []
    for row in reader:
        if not row or row[0].strip().startswith("#"):
            continue
        if len(row) < 2:
            continue
        try:
            points.append([float(row[0]), float(row[1])])
        except ValueError:
            continue
    return {
        "id": curve_id,
        "type": curve_type,
        "source_id": source_id,
        "condition": condition or {},
        "x": {"label": x_label, "unit": x_unit},
        "y": {"label": y_label, "unit": y_unit},
        "points": points,
        "digitization": {"method": "csv_import"},
    }
