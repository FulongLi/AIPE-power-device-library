from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml

from .config import DEVICES_DIR


DEVICE_SUFFIXES = {".yaml", ".yml", ".json"}


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return slug or "device"


class DeviceRepository:
    def __init__(self, devices_dir: Path = DEVICES_DIR):
        self.devices_dir = devices_dir
        self.devices_dir.mkdir(parents=True, exist_ok=True)

    def list_paths(self) -> list[Path]:
        paths = [
            path
            for path in self.devices_dir.iterdir()
            if path.is_file() and path.suffix.lower() in DEVICE_SUFFIXES
        ]
        return sorted(paths)

    def list_devices(self) -> list[dict[str, Any]]:
        return [self.load_path(path) for path in self.list_paths()]

    def load(self, device_id: str) -> dict[str, Any]:
        path = self._path_for_id(device_id)
        if path is None:
            raise FileNotFoundError(device_id)
        return self.load_path(path)

    def load_path(self, path: Path) -> dict[str, Any]:
        text = path.read_text(encoding="utf-8")
        if path.suffix.lower() == ".json":
            data = json.loads(text)
        else:
            data = yaml.safe_load(text)
        if not isinstance(data, dict):
            raise ValueError(f"{path.name} does not contain a device object.")
        data.setdefault("_file", path.name)
        return data

    def save(self, record: dict[str, Any]) -> Path:
        device_id = record.get("id") or slugify(
            f"{record.get('manufacturer', '')}-{record.get('part_number', '')}"
        )
        record["id"] = device_id
        path = self.devices_dir / f"{device_id}.yaml"
        clean_record = {k: v for k, v in record.items() if not k.startswith("_")}
        path.write_text(
            yaml.safe_dump(clean_record, sort_keys=False, allow_unicode=False),
            encoding="utf-8",
        )
        return path

    def _path_for_id(self, device_id: str) -> Path | None:
        for suffix in [".yaml", ".yml", ".json"]:
            path = self.devices_dir / f"{device_id}{suffix}"
            if path.exists():
                return path
        for path in self.list_paths():
            try:
                data = self.load_path(path)
            except Exception:
                continue
            if data.get("id") == device_id:
                return path
        return None
