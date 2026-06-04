"""Unit tests for tools/doctor.py (environment preflight + dep gating)."""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("doctor", ROOT / "tools" / "doctor.py")
doctor = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(doctor)


def _deps(xelatex=True, pdftoppm=True, pdfinfo=True,
          pymupdf=False, markitdown=False, cjk=True):
    avail = {"xelatex": xelatex, "pdftoppm": pdftoppm, "pdfinfo": pdfinfo,
             "pymupdf": pymupdf, "markitdown": markitdown, "cjk_fonts": cjk}
    kind = {"xelatex": "hard", "pdftoppm": "hard", "pdfinfo": "hard",
            "pymupdf": "soft", "markitdown": "soft", "cjk_fonts": "soft"}
    return {k: {"kind": kind[k], "available": v, "version": "",
                "hint": "" if v else "install it"} for k, v in avail.items()}


class ModelCapabilityTableTest(unittest.TestCase):
    def test_known_multimodal_models_have_vision(self):
        for mid in ("claude-opus-4-8", "claude-sonnet-4-6", "gpt-4o", "gpt-5",
                    "gemini-2.0-flash"):
            with self.subTest(model=mid):
                self.assertTrue(doctor.model_has_vision(mid))

    def test_unknown_or_empty_model_has_no_vision(self):
        for mid in ("", None, "some-random-llm", "llama-3-8b"):
            with self.subTest(model=mid):
                self.assertFalse(doctor.model_has_vision(mid))


class ProfileTest(unittest.TestCase):
    def test_no_blockers_when_hard_deps_present(self):
        prof = doctor.derive_profile(_deps(), doctor._default_capabilities())
        self.assertEqual(prof["blockers"], [])
        self.assertTrue(prof["can_compile"])
        self.assertTrue(prof["can_render_pdf"])
        self.assertFalse(prof["can_extract_pdf"])   # pymupdf missing
        self.assertFalse(prof["can_caption_md"])    # markitdown missing

    def test_missing_hard_dep_becomes_blocker(self):
        prof = doctor.derive_profile(_deps(xelatex=False),
                                     doctor._default_capabilities())
        self.assertIn("xelatex", prof["blockers"])


class CheckCommandTest(unittest.TestCase):
    def setUp(self):
        self.path = str(Path(tempfile.mkdtemp()) / "env_state.json")

    def test_check_passes_when_hard_deps_present(self):
        with mock.patch.object(doctor, "probe_deps", return_value=_deps()):
            rc = doctor.main(["check", "--path", self.path])
        self.assertEqual(rc, 0)
        state = json.loads(Path(self.path).read_text())
        self.assertEqual(state["profile"]["blockers"], [])

    def test_check_blocks_when_hard_dep_missing(self):
        with mock.patch.object(doctor, "probe_deps",
                               return_value=_deps(pdftoppm=False)):
            rc = doctor.main(["check", "--path", self.path])
        self.assertEqual(rc, 1)
        state = json.loads(Path(self.path).read_text())
        self.assertIn("pdftoppm", state["profile"]["blockers"])


class SetCapabilityTest(unittest.TestCase):
    def setUp(self):
        self.path = str(Path(tempfile.mkdtemp()) / "env_state.json")
        with mock.patch.object(doctor, "probe_deps", return_value=_deps()):
            doctor.main(["check", "--path", self.path])

    def _method(self):
        return json.loads(Path(self.path).read_text())["profile"]["visual_check_method"]

    def test_multimodal_model_gets_direct_vision(self):
        doctor.main(["set-capability", "--model", "claude-opus-4-8", "--path", self.path])
        self.assertEqual(self._method(), "direct-vision")

    def test_unknown_model_is_text_only(self):
        doctor.main(["set-capability", "--model", "mystery-llm", "--path", self.path])
        self.assertEqual(self._method(), "text-only")

    def test_mcp_vision_flag_when_model_blind(self):
        doctor.main(["set-capability", "--model", "mystery-llm",
                     "--mcp-vision", "--path", self.path])
        self.assertEqual(self._method(), "mcp")

    def test_check_preserves_capability(self):
        doctor.main(["set-capability", "--model", "claude-opus-4-8", "--path", self.path])
        with mock.patch.object(doctor, "probe_deps", return_value=_deps()):
            doctor.main(["check", "--path", self.path])
        # re-running check must not wipe a previously set capability
        self.assertEqual(self._method(), "direct-vision")


if __name__ == "__main__":
    unittest.main()
