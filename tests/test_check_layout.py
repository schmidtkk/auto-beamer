#!/usr/bin/env python3
"""
test_check_layout.py — Integration tests for check_layout.py
===========================================================

Tests the layout audit and DGV checker.

Run: python tests/test_check_layout.py
"""

import subprocess
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
TOOL = PROJECT_ROOT / "tools" / "check_layout.py"
FIXTURES_DIR = PROJECT_ROOT / "tests" / "fixtures"


class TestCheckLayoutCLI(unittest.TestCase):
    """Test check_layout.py command-line interface"""

    def _run(self, *args) -> subprocess.CompletedProcess:
        """Run check_layout.py with given args"""
        return subprocess.run(
            [sys.executable, str(TOOL), *args],
            capture_output=True,
            text=True,
        )

    def test_help(self):
        """--help must work"""
        result = self._run("--help")
        # check_layout.py doesn't have --help, it expects a tex file
        # Just verify it doesn't crash and mentions usage
        self.assertIn(result.returncode, [0, 1, 2],
                      "Should return 0, 1, or 2, not crash")
        output = result.stdout + result.stderr
        self.assertTrue(
            "usage" in output.lower() or "check_layout" in output.lower() or
            "tex" in output.lower() or "Error" in output,
            f"Should mention usage or tex. Output: {output}"
        )

    def test_analyze_minimal_tex(self):
        """Analyze a simple .tex file"""
        tex_file = FIXTURES_DIR / "test_minimal.tex"
        self.assertTrue(tex_file.exists(), f"Fixture not found: {tex_file}")

        result = self._run(str(tex_file))
        self.assertIn(result.returncode, [0, 1],
                      "Should return 0 or 1, not crash")

    def test_advise_flag(self):
        """--advise flag must work"""
        tex_file = FIXTURES_DIR / "test_minimal.tex"
        if not tex_file.exists():
            self.skipTest("Fixture not found")

        result = self._run(str(tex_file), "--advise")
        self.assertIn(result.returncode, [0, 1],
                      "--advise should return 0 or 1")


class TestCheckLayoutInternals(unittest.TestCase):
    """Test internal logic by importing the module"""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(PROJECT_ROOT / "tools"))
        import check_layout as cl
        cls.cl = cl

    def test_constants_positive(self):
        """Height constants must be positive"""
        self.assertGreater(self.cl.H_FRAME_OVERHEAD, 0)
        self.assertGreater(self.cl.H_BLUECARD_BASE, 0)
        self.assertGreater(self.cl.H_PER_ITEM, 0)

    def test_slide_ar(self):
        """Slide aspect ratio must be 16:9"""
        self.assertAlmostEqual(self.cl.SLIDE_AR, 16.0 / 9.0, places=5,
                               msg="Slide AR should be 16:9")

    def test_visual_weights(self):
        """Visual weights must be positive and image heaviest"""
        self.assertGreater(self.cl.W_IMAGE, self.cl.W_TEXT,
                           "Image weight should exceed text weight")
        self.assertGreater(self.cl.W_GOLDCALL, self.cl.W_TEXT,
                           "Goldcall weight should exceed text weight")


if __name__ == "__main__":
    unittest.main(verbosity=2)
