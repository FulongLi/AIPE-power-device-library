import tempfile
import unittest
from pathlib import Path

import yaml

from backend.index import DeviceIndex
from backend.repository import DeviceRepository
from backend.validation import validate_device_record


ROOT = Path(__file__).resolve().parents[1]


class ValidationTests(unittest.TestCase):
    def load_device(self, name):
        with (ROOT / "devices" / name).open(encoding="utf-8") as handle:
            return yaml.safe_load(handle)

    def test_sample_devices_are_valid(self):
        for path in sorted((ROOT / "devices").glob("*.yaml")):
            with self.subTest(path=path.name):
                record = yaml.safe_load(path.read_text(encoding="utf-8"))
                result = validate_device_record(record)
                self.assertEqual([], result["errors"])

    def test_missing_source_is_error(self):
        record = self.load_device("infineon-imza65r048m1h.yaml")
        record["ratings"]["voltage"]["source_id"] = "missing"
        result = validate_device_record(record)
        self.assertTrue(
            any("does not match a source" in error for error in result["errors"])
        )

    def test_unknown_source_category_is_error(self):
        record = self.load_device("epc-gan-hemt-example.yaml")
        record["sources"][1]["category"] = "spreadsheet_somewhere"
        result = validate_device_record(record)
        self.assertTrue(any("category" in error for error in result["errors"]))

    def test_raw_data_package_source_must_exist(self):
        record = self.load_device("epc-gan-hemt-example.yaml")
        record["raw_data_packages"][0]["source_id"] = "missing"
        result = validate_device_record(record)
        self.assertTrue(any("raw_data_packages" in error for error in result["errors"]))

    def test_gan_requires_gan_object(self):
        record = self.load_device("epc-gan-hemt-example.yaml")
        del record["gan"]
        result = validate_device_record(record)
        self.assertIn("GaN devices must include a gan object.", result["errors"])

    def test_curve_points_warn_when_not_monotonic(self):
        record = self.load_device("cree-sic-sbd-example.yaml")
        record["curves"][0]["points"] = [[1.0, 1.0], [0.5, 2.0]]
        result = validate_device_record(record)
        self.assertTrue(any("not monotonic" in warning for warning in result["warnings"]))


class IndexTests(unittest.TestCase):
    def test_rebuild_and_search_index(self):
        with tempfile.TemporaryDirectory() as devices_dir, tempfile.TemporaryDirectory() as db_dir:
            source = ROOT / "devices" / "epc-gan-hemt-example.yaml"
            target = Path(devices_dir) / source.name
            target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
            repository = DeviceRepository(Path(devices_dir))
            index = DeviceIndex(Path(db_dir) / "index.sqlite3")

            result = index.rebuild(repository)
            rows = index.search({"technology": "GaN"})

            self.assertEqual({"indexed": 1}, result)
            self.assertEqual(1, len(rows))
            self.assertEqual("EPC-GAN-EXAMPLE", rows[0]["part_number"])


if __name__ == "__main__":
    unittest.main()
