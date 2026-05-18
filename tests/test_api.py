import unittest

from fastapi.testclient import TestClient

from backend.main import app


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.client.post("/api/index/rebuild")

    def test_taxonomy_endpoint(self):
        response = self.client.get("/api/taxonomy")
        self.assertEqual(200, response.status_code)
        self.assertIn("GaN", response.json()["technologies"])

    def test_devices_endpoint(self):
        response = self.client.get("/api/devices?technology=GaN")
        self.assertEqual(200, response.status_code)
        rows = response.json()
        self.assertEqual(1, len(rows))
        self.assertEqual("EPC-GAN-EXAMPLE", rows[0]["part_number"])

    def test_devices_endpoint_filters_by_manufacturer(self):
        response = self.client.get("/api/devices?manufacturer=Infineon")
        self.assertEqual(200, response.status_code)
        rows = response.json()
        self.assertEqual(2, len(rows))
        self.assertTrue(all(row["manufacturer"] == "Infineon" for row in rows))

    def test_device_detail_includes_validation(self):
        response = self.client.get("/api/devices/epc-gan-hemt-example")
        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertEqual([], payload["validation"]["errors"])
        self.assertEqual("GaN", payload["device"]["technology"])
        self.assertEqual("third_party_characterization", payload["device"]["sources"][1]["category"])

    def test_curve_csv_import(self):
        response = self.client.post(
            "/api/curves/import-csv",
            json={
                "csv_text": "0,0\n1,2\n2,4",
                "curve_id": "test",
                "curve_type": "iv_output",
                "x_label": "Voltage",
                "x_unit": "V",
                "y_label": "Current",
                "y_unit": "A",
                "source_id": "ds",
            },
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(3, response.json()["points"])


if __name__ == "__main__":
    unittest.main()
