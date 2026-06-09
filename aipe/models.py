from __future__ import annotations

from typing import Any


MODEL_ASSET_KINDS = {"aipe_pdl_record", "spice", "plecs", "matlab", "simulink", "datasheet"}
MODEL_ASSET_STATUSES = {"available", "external", "planned", "missing"}


def make_model_asset(
    *,
    asset_id: str,
    device_id: str,
    kind: str,
    status: str,
    source: str,
    path_or_url: str,
    notes: str,
) -> dict[str, str]:
    if kind not in MODEL_ASSET_KINDS:
        raise ValueError(f"Unsupported model asset kind: {kind}")
    if status not in MODEL_ASSET_STATUSES:
        raise ValueError(f"Unsupported model asset status: {status}")
    return {
        "asset_id": asset_id,
        "device_id": device_id,
        "kind": kind,
        "status": status,
        "source": source,
        "path_or_url": path_or_url,
        "notes": notes,
    }


def compare_projection(device: dict[str, Any]) -> dict[str, Any]:
    return {
        "device_id": device["id"],
        "name": device["name"],
        "manufacturer": device.get("manufacturer"),
        "part_number": device.get("part_number"),
        "device_type": device.get("device_type"),
        "technology": device.get("technology"),
        "ratings": device.get("ratings", {}),
        "package": device.get("package", {}),
        "curve_families": device.get("curve_families", {}),
        "model_assets": [
            {
                "kind": asset.get("kind"),
                "status": asset.get("status"),
                "source": asset.get("source"),
            }
            for asset in device.get("model_assets", [])
        ],
    }
