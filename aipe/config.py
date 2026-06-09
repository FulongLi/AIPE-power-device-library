from __future__ import annotations

import os
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
TDB_RAW_DIR = DATA_DIR / "tdb_raw"
DEVICE_SUMMARY_DIR = DATA_DIR / "devices"
MODEL_ASSET_DIR = DATA_DIR / "model_assets"

TDB_INDEX_URL = "https://raw.githubusercontent.com/upb-lea/transistordatabase_File_Exchange/main/index.txt"


def require_api_key() -> bool:
    return os.getenv("AIPE_REQUIRE_API_KEY", "").lower() in {"1", "true", "yes", "on"}


def expected_api_key() -> str | None:
    return os.getenv("AIPE_API_KEY")
