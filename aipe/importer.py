from __future__ import annotations

from pathlib import Path
from typing import Any

from .aipe_pdl_loader import load_aipe_pdl_record, normalize_aipe_pdl_record
from .config import AIPE_PDL_SEED_DIR
from .repository import DeviceRepository


def import_aipe_pdl_seeds(
    *,
    repository: DeviceRepository,
    seed_dir: Path = AIPE_PDL_SEED_DIR,
) -> dict[str, Any]:
    seed_dir.mkdir(parents=True, exist_ok=True)
    paths = sorted(seed_dir.glob("*.json"))
    imported = []
    failed = []
    for path in paths:
        try:
            record = load_aipe_pdl_record(path)
            device = normalize_aipe_pdl_record(record, seed_path=path)
            repository.save_device(device)
            imported.append(device["id"])
        except Exception as exc:  # pragma: no cover - exercised only by network/import failures.
            failed.append({"path": str(path), "error": str(exc)})
    return {
        "seed_dir": str(seed_dir),
        "total_records": len(paths),
        "imported": len(imported),
        "device_ids": imported,
        "failed": failed,
    }
