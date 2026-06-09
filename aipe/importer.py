from __future__ import annotations

from pathlib import Path
from typing import Any

from .config import TDB_INDEX_URL, TDB_RAW_DIR
from .repository import DeviceRepository
from .tdb_loader import fetch_tdb_record, load_tdb_index, normalize_tdb_record


def import_tdb_index(
    *,
    repository: DeviceRepository,
    index_url: str = TDB_INDEX_URL,
    raw_dir: Path = TDB_RAW_DIR,
) -> dict[str, Any]:
    urls = load_tdb_index(index_url)
    imported = []
    failed = []
    for url in urls:
        try:
            record, raw_path = fetch_tdb_record(url, raw_dir=raw_dir)
            device = normalize_tdb_record(record, source_url=url, raw_path=raw_path)
            repository.save_device(device)
            imported.append(device["id"])
        except Exception as exc:  # pragma: no cover - exercised only by network/import failures.
            failed.append({"url": url, "error": str(exc)})
    return {
        "index_url": index_url,
        "total_urls": len(urls),
        "imported": len(imported),
        "device_ids": imported,
        "failed": failed,
    }
