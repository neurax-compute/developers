import os, sys, json, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from neurax import prices_from_csv, compact_evidence, Client


class T(unittest.TestCase):
    def test_csv_italian(self):
        n, d, p = prices_from_csv("date;BTC;Stock XY\n2024-01-02;41.250,5;52,10\n2024-01-03;42.010,0;52,35\n")
        self.assertEqual(n, ["BTC", "Stock XY"])
        self.assertEqual(p, [[41250.5, 52.10], [42010.0, 52.35]])

    def test_csv_comma(self):
        n, d, p = prices_from_csv("date,BTC,XY\n2024-01-02,41250.5,52.1\n2024-01-03,42010,52.35\n")
        self.assertEqual(d, ["2024-01-02", "2024-01-03"])

    def test_csv_bad(self):
        with self.assertRaises(ValueError):
            prices_from_csv("date;A\n2024-01-01;-3\n")

    def test_compact(self):
        f = '{\n  "evidence": {\n    "a": "x y",\n    "b": [\n      1,\n      2\n    ]\n  },\n  "signature": "s"\n}\n'
        self.assertEqual(compact_evidence(f), b'{"a":"x y","b":[1,2]}')

    def test_job_body(self):
        self.assertEqual(Client._job("w", {}, region="CH", sovereign=True), {"workload": "w", "params": {}, "region": "CH", "sovereign": True})


if __name__ == "__main__":
    unittest.main()
