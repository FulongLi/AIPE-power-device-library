from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import aipe.api as api
from aipe.aipe_pdl_loader import normalize_aipe_pdl_record
from aipe.repository import DeviceRepository


ROOT = Path(__file__).resolve().parents[1]


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        base = Path(self.temp_dir.name)
        api.repository = DeviceRepository(base / "devices", base / "model_assets")
        record = json.loads((ROOT / "tests" / "fixtures" / "aipe_pdl_sample.json").read_text(encoding="utf-8"))
        api.repository.save_device(normalize_aipe_pdl_record(record, imported_at="2026-06-09T00:00:00+00:00"))
        self.client = TestClient(api.app)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_health(self):
        response = self.client.get("/api/health")
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, response.json()["device_count"])

    def test_search_filters(self):
        response = self.client.get("/api/devices?type=GaN%20HEMT&min_voltage=600&min_current=10")
        self.assertEqual(200, response.status_code)
        self.assertEqual("aipe-pdl-gan650-ref", response.json()[0]["id"])

    def test_detail_contains_aipe_pdl_origin(self):
        response = self.client.get("/api/devices/aipe-pdl-gan650-ref")
        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertEqual("aipe_pdl", payload["origin"]["source"])
        self.assertEqual("", payload["datasheet"]["url"])

    def test_compare(self):
        response = self.client.post("/api/devices/compare", json={"device_ids": ["aipe-pdl-gan650-ref"]})
        self.assertEqual(200, response.status_code)
        self.assertEqual("aipe-pdl-gan650-ref", response.json()["rows"][0]["device_id"])

    def test_model_assets(self):
        response = self.client.get("/api/devices/aipe-pdl-gan650-ref/model-assets")
        self.assertEqual(200, response.status_code)
        self.assertEqual(["aipe_pdl_record", "spice"], [asset["kind"] for asset in response.json()])


if __name__ == "__main__":
    unittest.main()
