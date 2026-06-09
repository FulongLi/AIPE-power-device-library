from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from .config import ROOT_DIR
from .models import make_model_asset


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return slug or "device"


def load_aipe_pdl_record(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not an AIPE PDL JSON object.")
    return data


def normalize_aipe_pdl_record(
    record: dict[str, Any],
    *,
    seed_path: Optional[Path] = None,
    imported_at: Optional[str] = None,
) -> dict[str, Any]:
    name = str(record.get("name") or record.get("part_number") or "unknown")
    device_id = slugify(str(record.get("id") or name))
    seed_reference = display_path(seed_path) if seed_path else ""
    source = record.get("source", {})
    assets = [
        make_model_asset(
            asset_id=f"{device_id}-aipe-pdl-record",
            device_id=device_id,
            kind="aipe_pdl_record",
            status="available",
            source="AIPE PDL",
            path_or_url=seed_reference,
            notes="Native AIPE PDL seed record. This is a curated data record, not a simulator model.",
        )
    ]
    for asset in record.get("model_assets", []):
        if not isinstance(asset, dict):
            continue
        assets.append(
            make_model_asset(
                asset_id=str(asset.get("asset_id") or f"{device_id}-{asset.get('kind', 'asset')}"),
                device_id=device_id,
                kind=str(asset.get("kind") or "spice"),
                status=str(asset.get("status") or "planned"),
                source=str(asset.get("source") or "AIPE PDL"),
                path_or_url=str(asset.get("path_or_url") or ""),
                notes=str(asset.get("notes") or ""),
            )
        )

    return {
        "id": device_id,
        "name": name,
        "manufacturer": record.get("manufacturer") or "AIPE PDL",
        "part_number": record.get("part_number") or name,
        "device_type": record.get("device_type") or "",
        "technology": record.get("technology") or "",
        "ratings": {
            "voltage_v": numeric_or_none(record.get("ratings", {}).get("voltage_v")),
            "absolute_current_a": numeric_or_none(record.get("ratings", {}).get("absolute_current_a")),
            "continuous_current_a": numeric_or_none(record.get("ratings", {}).get("continuous_current_a")),
        },
        "package": record.get("package") or {},
        "datasheet": {
            "url": "",
            "date": str(record.get("datasheet", {}).get("date") or ""),
            "version": str(record.get("datasheet", {}).get("version") or ""),
        },
        "curve_families": normalize_curve_families(record.get("curve_families", {})),
        "model_assets": assets,
        "origin": {
            "source": "aipe_pdl",
            "source_url": "",
            "raw_path": seed_reference,
            "imported_at": imported_at or datetime.now(timezone.utc).isoformat(),
            "document_id": str(source.get("document_id") or ""),
            "revision": str(source.get("revision") or ""),
            "notes": str(source.get("notes") or "AIPE PDL native record."),
        },
    }


def normalize_curve_families(value: Any) -> dict[str, bool]:
    defaults = {
        "capacitance": False,
        "eoss": False,
        "switch_channel": False,
        "diode_channel": False,
        "switching_energy": False,
        "reverse_recovery": False,
        "thermal": False,
        "gate_charge": False,
        "soa": False,
        "raw_measurement": False,
    }
    if isinstance(value, dict):
        for key in defaults:
            defaults[key] = bool(value.get(key, defaults[key]))
    return defaults


def numeric_or_none(value: Any) -> Optional[float]:
    if isinstance(value, (int, float)):
        return float(value)
    return None


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT_DIR))
    except ValueError:
        return str(path)
