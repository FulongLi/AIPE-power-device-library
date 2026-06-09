from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from aipe.repository import DeviceRepository
from aipe.tdb_loader import normalize_tdb_record


ROOT = Path(__file__).resolve().parents[1]


class RepositoryTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        base = Path(self.temp_dir.name)
        self.repository = DeviceRepository(base / "devices", base / "model_assets")
        record = json.loads((ROOT / "tests" / "fixtures" / "tdb_sample.json").read_text(encoding="utf-8"))
        self.device = normalize_tdb_record(record, imported_at="2026-06-09T00:00:00+00:00")
        self.repository.save_device(self.device)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_search_filters_by_type_and_voltage(self):
        rows = self.repository.search_devices(device_type="GaN-Transistor", min_voltage=600)
        self.assertEqual(1, len(rows))
        self.assertEqual("gansystems-gs66506t", rows[0]["id"])

    def test_model_assets_include_tdb_json_and_datasheet(self):
        assets = self.repository.list_model_assets("gansystems-gs66506t")
        self.assertEqual(["tdb_json", "datasheet"], [asset["kind"] for asset in assets])

    def test_compare_projects_stable_fields(self):
        payload = self.repository.compare_devices(["gansystems-gs66506t", "missing"])
        self.assertEqual(["missing"], payload["missing_device_ids"])
        self.assertEqual("gansystems-gs66506t", payload["rows"][0]["device_id"])


if __name__ == "__main__":
    unittest.main()
