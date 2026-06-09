from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from .config import DEVICE_SUMMARY_DIR, MODEL_ASSET_DIR
from .models import compare_projection


class DeviceRepository:
    def __init__(
        self,
        device_dir: Path = DEVICE_SUMMARY_DIR,
        model_asset_dir: Path = MODEL_ASSET_DIR,
    ):
        self.device_dir = device_dir
        self.model_asset_dir = model_asset_dir
        self.device_dir.mkdir(parents=True, exist_ok=True)
        self.model_asset_dir.mkdir(parents=True, exist_ok=True)

    def save_device(self, device: dict[str, Any]) -> Path:
        path = self.device_dir / f"{device['id']}.json"
        path.write_text(json.dumps(device, indent=2, sort_keys=True), encoding="utf-8")
        return path

    def list_devices(self) -> list[dict[str, Any]]:
        return [self.load_device_path(path) for path in sorted(self.device_dir.glob("*.json"))]

    def load_device(self, device_id: str) -> dict[str, Any]:
        path = self.device_dir / f"{device_id}.json"
        if not path.exists():
            raise FileNotFoundError(device_id)
        return self.load_device_path(path)

    def load_device_path(self, path: Path) -> dict[str, Any]:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError(f"{path} is not a JSON object.")
        return data

    def search_devices(
        self,
        *,
        q: Optional[str] = None,
        device_type: Optional[str] = None,
        manufacturer: Optional[str] = None,
        min_voltage: Optional[float] = None,
        min_current: Optional[float] = None,
    ) -> list[dict[str, Any]]:
        rows = []
        query = q.lower() if q else None
        for device in self.list_devices():
            if query and query not in search_text(device):
                continue
            if device_type and device.get("device_type") != device_type:
                continue
            if manufacturer and device.get("manufacturer") != manufacturer:
                continue
            voltage = device.get("ratings", {}).get("voltage_v")
            current = device.get("ratings", {}).get("continuous_current_a")
            if min_voltage is not None and (voltage is None or voltage < min_voltage):
                continue
            if min_current is not None and (current is None or current < min_current):
                continue
            rows.append(device)
        return sorted(rows, key=lambda item: (item.get("manufacturer", ""), item.get("name", "")))

    def list_model_assets(self, device_id: str) -> list[dict[str, Any]]:
        device = self.load_device(device_id)
        assets = list(device.get("model_assets", []))
        for path in sorted(self.model_asset_dir.glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            items = data if isinstance(data, list) else [data]
            for item in items:
                if isinstance(item, dict) and item.get("device_id") == device_id:
                    assets.append(item)
        return dedupe_assets(assets)

    def compare_devices(self, device_ids: list[str]) -> dict[str, Any]:
        rows = []
        missing = []
        for device_id in device_ids:
            try:
                rows.append(compare_projection(self.load_device(device_id)))
            except FileNotFoundError:
                missing.append(device_id)
        return {"device_ids": device_ids, "rows": rows, "missing_device_ids": missing}


def search_text(device: dict[str, Any]) -> str:
    values = [
        device.get("id", ""),
        device.get("name", ""),
        device.get("manufacturer", ""),
        device.get("part_number", ""),
        device.get("device_type", ""),
        device.get("technology", ""),
    ]
    return " ".join(str(value) for value in values).lower()


def dedupe_assets(assets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    result = []
    for asset in assets:
        asset_id = asset.get("asset_id")
        if asset_id in seen:
            continue
        seen.add(asset_id)
        result.append(asset)
    return result
