from __future__ import annotations

import json
import unittest
from pathlib import Path

from aipe.aipe_pdl_loader import normalize_aipe_pdl_record


ROOT = Path(__file__).resolve().parents[1]


class AipePdlLoaderTests(unittest.TestCase):
    def test_normalize_aipe_pdl_record_extracts_v1_summary(self):
        record = json.loads((ROOT / "tests" / "fixtures" / "aipe_pdl_sample.json").read_text(encoding="utf-8"))
        summary = normalize_aipe_pdl_record(
            record,
            imported_at="2026-06-09T00:00:00+00:00",
        )

        self.assertEqual("aipe-pdl-gan650-ref", summary["id"])
        self.assertEqual("GaN", summary["technology"])
        self.assertEqual(650.0, summary["ratings"]["voltage_v"])
        self.assertEqual(18.0, summary["ratings"]["continuous_current_a"])
        self.assertTrue(summary["curve_families"]["capacitance"])
        self.assertTrue(summary["curve_families"]["switch_channel"])
        self.assertTrue(summary["curve_families"]["switching_energy"])
        self.assertEqual("aipe_pdl_record", summary["model_assets"][0]["kind"])
        self.assertEqual("aipe_pdl", summary["origin"]["source"])
