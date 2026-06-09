from __future__ import annotations

import json
import unittest
from pathlib import Path

from aipe.tdb_loader import normalize_tdb_record


ROOT = Path(__file__).resolve().parents[1]


class TdbLoaderTests(unittest.TestCase):
    def test_normalize_tdb_record_extracts_v1_summary(self):
        record = json.loads((ROOT / "tests" / "fixtures" / "tdb_sample.json").read_text(encoding="utf-8"))
        summary = normalize_tdb_record(
            record,
            source_url="https://example.test/GaNSystems_GS66506T.json",
            imported_at="2026-06-09T00:00:00+00:00",
        )

        self.assertEqual("gansystems-gs66506t", summary["id"])
        self.assertEqual("GaN", summary["technology"])
        self.assertEqual(650.0, summary["ratings"]["voltage_v"])
        self.assertEqual(18.0, summary["ratings"]["continuous_current_a"])
        self.assertTrue(summary["curve_families"]["capacitance"])
        self.assertTrue(summary["curve_families"]["switch_channel"])
        self.assertTrue(summary["curve_families"]["switching_energy"])
        self.assertEqual(["tdb_json", "datasheet"], [asset["kind"] for asset in summary["model_assets"]])
        self.assertEqual("tdb_file_exchange", summary["origin"]["source"])


if __name__ == "__main__":
    unittest.main()
