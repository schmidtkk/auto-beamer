"""Unit tests for tools/image_index.py (per-deck figure index)."""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "image_index", ROOT / "tools" / "image_index.py")
image_index = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(image_index)


class ConfidencePolicyTest(unittest.TestCase):
    def _rec(self, conf, method, verified):
        rec = image_index._new_record("x", "x.png")
        rec["confidence"] = conf
        rec["visual_check"] = {"method": method, "verified": verified, "notes": ""}
        image_index.apply_confidence_policy(rec)
        return rec["confidence"]

    def test_text_only_capped(self):
        self.assertEqual(self._rec(0.95, "text-only", False),
                         image_index.TEXT_ONLY_CONF_CAP)

    def test_unverified_vision_capped(self):
        self.assertEqual(self._rec(0.9, "direct-vision", False),
                         image_index.TEXT_ONLY_CONF_CAP)

    def test_verified_vision_allows_high(self):
        self.assertEqual(self._rec(0.9, "direct-vision", True), 0.9)

    def test_clamped_to_unit_interval(self):
        self.assertLessEqual(self._rec(1.5, "mcp", True), 1.0)


class IndexRoundTripTest(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.path = str(self.dir / "image_index.json")
        self.paper = self.dir / "paper.json"
        self.paper.write_text(json.dumps({
            "source_pdf": "/x/ot.pdf",
            "images": [
                {"filename": "fig_p3_monge.png", "page": 3, "width_px": 800,
                 "height_px": 600, "aspect_ratio": 1.33, "xref": 1,
                 "bbox_x0": 1.0, "bbox_y0": 2.0, "bbox_x1": 3.0, "bbox_y1": 4.0},
                {"filename": "fig_p7_coupling.png", "page": 7, "width_px": 1200,
                 "height_px": 500, "aspect_ratio": 2.4, "xref": 2},
            ],
        }), encoding="utf-8")

    def _run(self, *args):
        return image_index.main([*args, "--path", self.path])

    def test_import_parser_seeds_records(self):
        self._run("init", "--deck", "OT")
        self._run("import-parser", str(self.paper), "--document", "ot.pdf")
        data = json.loads(Path(self.path).read_text())
        self.assertEqual(len(data["images"]), 2)
        rec = next(i for i in data["images"] if i["id"] == "fig_p3_monge")
        self.assertEqual(rec["source"]["page"], 3)
        self.assertIn("bbox", rec["source"]["region"])
        self.assertEqual(rec["aspect_ratio"], 1.33)

    def test_query_matches_key_idea(self):
        self._run("init")
        self._run("import-parser", str(self.paper))
        self._run("set", "fig_p7_coupling", "--key-idea",
                  "coupling joint distribution with marginals",
                  "--visual", "direct-vision", "--verified", "--confidence", "0.8")
        # query returns 0 and prints the matching id; assert via the index state
        rc = self._run("query", "--key-idea", "coupling of marginals")
        self.assertEqual(rc, 0)

    def test_validate_passes_and_render_md(self):
        self._run("init")
        self._run("import-parser", str(self.paper))
        self._run("set", "fig_p3_monge", "--key-idea", "Monge map",
                  "--visual", "direct-vision", "--verified", "--confidence", "0.7")
        self._run("set", "fig_p7_coupling", "--key-idea", "coupling",
                  "--confidence", "0.4")  # text-only stays under cap
        self.assertEqual(self._run("validate"), 0)
        out = self.dir / "idx.md"
        self.assertEqual(self._run("render-md", "--out", str(out)), 0)
        self.assertIn("Image Index", out.read_text())

    def test_request_resolution_updates_adoption(self):
        self._run("init")
        self._run("import-parser", str(self.paper))
        self._run("request-add", "--slide", "Monge problem", "--need",
                  "show transport", "--id", "req-001")
        self._run("request-resolve", "--request", "req-001", "--image",
                  "fig_p3_monge", "--status", "adopted")
        data = json.loads(Path(self.path).read_text())
        rec = next(i for i in data["images"] if i["id"] == "fig_p3_monge")
        self.assertTrue(rec["adoption"])
        self.assertEqual(rec["adoption"][0]["status"], "adopted")


if __name__ == "__main__":
    unittest.main()
