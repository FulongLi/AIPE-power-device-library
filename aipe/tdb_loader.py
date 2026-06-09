from __future__ import annotations

import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional

from .config import ROOT_DIR, TDB_INDEX_URL, TDB_RAW_DIR
from .models import make_model_asset


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return slug or "device"


def load_tdb_index(index_url: str = TDB_INDEX_URL) -> list[str]:
    with urllib.request.urlopen(index_url, timeout=30) as response:
        text = response.read().decode("utf-8")
    return [line.strip() for line in text.splitlines() if line.strip() and not line.startswith("#")]


def fetch_tdb_record(url: str, raw_dir: Path = TDB_RAW_DIR) -> tuple[dict[str, Any], Path]:
    raw_dir.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=60) as response:
        payload = response.read().decode("utf-8")
    data = json.loads(payload)
    if not isinstance(data, dict):
        raise ValueError(f"TDB record at {url} is not a JSON object.")
    file_name = Path(url).name
    raw_path = raw_dir / file_name
    raw_path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    return data, raw_path


def load_tdb_record(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object.")
    return data


def normalize_tdb_record(
    record: dict[str, Any],
    *,
    source_url: Optional[str] = None,
    raw_path: Optional[Path] = None,
    imported_at: Optional[str] = None,
) -> dict[str, Any]:
    name = str(record.get("name") or "unknown")
    device_id = slugify(name)
    datasheet_url = str(record.get("datasheet_hyperlink") or "")
    raw_reference = display_path(raw_path) if raw_path else (source_url or "")
    model_assets = [
        make_model_asset(
            asset_id=f"{device_id}-tdb-json",
            device_id=device_id,
            kind="tdb_json",
            status="available",
            source="TDB public File Exchange",
            path_or_url=raw_reference,
            notes="Raw public TDB JSON. This is a data asset, not a validated simulator model.",
        )
    ]
    if datasheet_url:
        model_assets.append(
            make_model_asset(
                asset_id=f"{device_id}-datasheet",
                device_id=device_id,
                kind="datasheet",
                status="external",
                source="Manufacturer datasheet link via TDB",
                path_or_url=datasheet_url,
                notes="External datasheet URL recorded by the TDB public sample.",
            )
        )

    return {
        "id": device_id,
        "name": name,
        "manufacturer": record.get("manufacturer") or "",
        "part_number": infer_part_number(name, record.get("manufacturer")),
        "device_type": record.get("type") or "",
        "technology": infer_technology(record),
        "ratings": {
            "voltage_v": numeric_or_none(record.get("v_abs_max")),
            "absolute_current_a": numeric_or_none(record.get("i_abs_max")),
            "continuous_current_a": numeric_or_none(record.get("i_cont")),
        },
        "package": {
            "housing_type": record.get("housing_type") or "",
            "housing_area_m2": numeric_or_none(record.get("housing_area")),
            "cooling_area_m2": numeric_or_none(record.get("cooling_area")),
        },
        "datasheet": {
            "url": datasheet_url,
            "date": record.get("datasheet_date") or "",
            "version": record.get("datasheet_version") or "",
        },
        "curve_families": detect_curve_families(record),
        "model_assets": model_assets,
        "origin": {
            "source": "tdb_file_exchange",
            "source_url": source_url or "",
            "raw_path": display_path(raw_path) if raw_path else "",
            "imported_at": imported_at or datetime.now(timezone.utc).isoformat(),
            "license_note": "TDB public sample; upstream license status should be reviewed before commercial distribution.",
        },
    }


def infer_part_number(name: str, manufacturer: Any) -> str:
    if "_" in name:
        return name.split("_", 1)[1]
    if manufacturer and str(name).lower().startswith(str(manufacturer).lower()):
        return str(name)[len(str(manufacturer)) :].strip("_- ")
    return name


def infer_technology(record: dict[str, Any]) -> str:
    values = " ".join(
        str(value)
        for value in [record.get("type"), record.get("technology"), record.get("name")]
        if value
    ).lower()
    if "sic" in values:
        return "SiC"
    if "gan" in values:
        return "GaN"
    if "igbt" in values or "si-mosfet" in values or "silicon" in values:
        return "Si"
    return ""


def numeric_or_none(value: Any) -> Optional[float]:
    if isinstance(value, (int, float)):
        return float(value)
    return None


def detect_curve_families(record: dict[str, Any]) -> dict[str, bool]:
    return {
        "capacitance": any(has_items(record.get(key)) for key in ["c_oss", "c_iss", "c_rss"]),
        "eoss": has_items(record.get("graph_v_ecoss")),
        "switch_channel": nested_has_items(record, ["switch", "channel"]),
        "diode_channel": nested_has_items(record, ["diode", "channel"]),
        "switching_energy": any(
            nested_has_items(record, ["switch", key])
            for key in ["e_on", "e_off", "e_on_meas", "e_off_meas"]
        ),
        "reverse_recovery": nested_has_items(record, ["diode", "e_rr"]),
        "thermal": any(
            nested_has_items(record, path)
            for path in [
                ["switch", "thermal_foster", "graph_t_rthjc"],
                ["diode", "thermal_foster", "graph_t_rthjc"],
            ]
        ),
        "gate_charge": nested_has_items(record, ["switch", "charge_curve"]),
        "soa": any(nested_has_items(record, [node, "soa"]) for node in ["switch", "diode"]),
        "raw_measurement": has_items(record.get("raw_measurement_data")),
    }


def nested_has_items(record: dict[str, Any], path: Iterable[str]) -> bool:
    value: Any = record
    for key in path:
        if not isinstance(value, dict):
            return False
        value = value.get(key)
    return has_items(value)


def has_items(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, list):
        return len(value) > 0
    if isinstance(value, dict):
        if "graph_v_c" in value or "graph_v_i" in value or "graph_i_e" in value:
            return True
        return any(has_items(item) for item in value.values())
    return bool(value)


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT_DIR))
    except ValueError:
        return str(path)
