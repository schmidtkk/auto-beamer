#!/usr/bin/env python3
"""
test_smoke.py — Smoke tests for LaTeX compilation
=================================================

Verifies that key .tex files compile without errors.
Requires XeLaTeX to be installed and in PATH.

Run: python tests/test_smoke.py
"""

import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
TESTS_DIR = PROJECT_ROOT / "tests"
FIXTURES_DIR = TESTS_DIR / "fixtures"
BUILD_DIR = TESTS_DIR / "build"


class TestSmokeCompilation(unittest.TestCase):
    """Smoke tests: compile .tex files and verify PDF output"""

    @classmethod
    def setUpClass(cls):
        """Ensure build directory exists and xelatex is available"""
        BUILD_DIR.mkdir(parents=True, exist_ok=True)

        # Check xelatex
        cls.xelatex = shutil.which("xelatex")
        if cls.xelatex is None:
            raise unittest.SkipTest(
                "xelatex not found in PATH. Install TeX Live to run smoke tests."
            )

    def _compile(self, tex_file: Path, passes: int = 2) -> subprocess.CompletedProcess:
        """Compile a .tex file with xelatex"""
        for _ in range(passes):
            result = subprocess.run(
                [
                    self.xelatex,
                    "-output-directory", str(BUILD_DIR),
                    "-interaction=nonstopmode",
                    str(tex_file),
                ],
                capture_output=True,
                text=True,
                cwd=str(tex_file.parent),
            )
        return result

    def _check_pdf(self, stem: str) -> Path:
        """Check that PDF was generated"""
        pdf_path = BUILD_DIR / f"{stem}.pdf"
        self.assertTrue(
            pdf_path.exists(),
            f"PDF not generated: {pdf_path}"
        )
        self.assertGreater(
            pdf_path.stat().st_size,
            1000,
            f"PDF too small (likely failed): {pdf_path}"
        )
        return pdf_path

    def test_xelatex_available(self):
        """XeLaTeX must be available"""
        self.assertIsNotNone(self.xelatex, "xelatex not found")
        result = subprocess.run(
            [self.xelatex, "--version"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, "xelatex --version failed")

    def test_minimal_compiles(self):
        """tests/fixtures/test_minimal.tex must compile"""
        tex_file = FIXTURES_DIR / "test_minimal.tex"
        self.assertTrue(tex_file.exists(), f"Fixture not found: {tex_file}")

        result = self._compile(tex_file, passes=2)

        # Check for fatal errors (non-zero exit is OK for appendixnumberbeamer)
        self.assertNotIn("! Emergency stop", result.stdout + result.stderr,
                         "Compilation failed with emergency stop")
        self.assertNotIn("! LaTeX Error", result.stdout + result.stderr,
                         "Compilation failed with LaTeX error")

        self._check_pdf("test_minimal")

    def test_font_override_compiles(self):
        """tests/fixtures/test_font_override.tex must compile"""
        tex_file = FIXTURES_DIR / "test_font_override.tex"
        self.assertTrue(tex_file.exists(), f"Fixture not found: {tex_file}")

        result = self._compile(tex_file, passes=2)

        self.assertNotIn("! Emergency stop", result.stdout + result.stderr,
                         "Compilation failed with emergency stop")
        self.assertNotIn("! LaTeX Error", result.stdout + result.stderr,
                         "Compilation failed with LaTeX error")

        self._check_pdf("test_font_override")

    def test_template_lib_demo_compiles(self):
        """template-lib-demo.tex must compile"""
        tex_file = PROJECT_ROOT / "template-lib-demo.tex"
        if not tex_file.exists():
            self.skipTest("template-lib-demo.tex not found")

        result = self._compile(tex_file, passes=2)

        self.assertNotIn("! Emergency stop", result.stdout + result.stderr,
                         "Compilation failed with emergency stop")
        self.assertNotIn("! LaTeX Error", result.stdout + result.stderr,
                         "Compilation failed with LaTeX error")

        self._check_pdf("template-lib-demo")


class TestBuildScripts(unittest.TestCase):
    """Test build scripts exist and are executable"""

    def test_build_ps1_exists(self):
        """build_clean.ps1 must exist"""
        script = PROJECT_ROOT / "build_clean.ps1"
        self.assertTrue(script.exists(), "build_clean.ps1 not found")

    def test_build_sh_exists(self):
        """build.sh must exist"""
        script = PROJECT_ROOT / "build.sh"
        self.assertTrue(script.exists(), "build.sh not found")

    def test_install_linux_sh_exists(self):
        """install-linux.sh must exist"""
        script = PROJECT_ROOT / "install-linux.sh"
        self.assertTrue(script.exists(), "install-linux.sh not found")

    def test_build_sh_executable(self):
        """build.sh must have executable permissions (Unix)"""
        script = PROJECT_ROOT / "build.sh"
        if os.name == "nt":
            self.skipTest("Executable check skipped on Windows")
        self.assertTrue(os.access(script, os.X_OK),
                        "build.sh is not executable. Run: chmod +x build.sh")

    def test_install_linux_sh_executable(self):
        """install-linux.sh must have executable permissions (Unix)"""
        script = PROJECT_ROOT / "install-linux.sh"
        if os.name == "nt":
            self.skipTest("Executable check skipped on Windows")
        self.assertTrue(os.access(script, os.X_OK),
                        "install-linux.sh is not executable. Run: chmod +x install-linux.sh")


class TestToolsExist(unittest.TestCase):
    """Test that required tools exist"""

    def test_layout_optimizer_exists(self):
        """tools/layout_optimizer.py must exist"""
        tool = PROJECT_ROOT / "tools" / "layout_optimizer.py"
        self.assertTrue(tool.exists(), "layout_optimizer.py not found")

    def test_check_layout_exists(self):
        """tools/check_layout.py must exist"""
        tool = PROJECT_ROOT / "tools" / "check_layout.py"
        self.assertTrue(tool.exists(), "check_layout.py not found")

    def test_auto_crop_exists(self):
        """tools/auto_crop.py must exist"""
        tool = PROJECT_ROOT / "tools" / "auto_crop.py"
        self.assertTrue(tool.exists(), "auto_crop.py not found")

    def test_layout_optimizer_runnable(self):
        """layout_optimizer.py --help must work"""
        tool = PROJECT_ROOT / "tools" / "layout_optimizer.py"
        result = subprocess.run(
            [sys.executable, str(tool), "--help"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0,
                         f"layout_optimizer.py --help failed: {result.stderr}")

    def test_check_layout_runnable(self):
        """check_layout.py --help must work"""
        tool = PROJECT_ROOT / "tools" / "check_layout.py"
        result = subprocess.run(
            [sys.executable, str(tool), "--help"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0,
                         f"check_layout.py --help failed: {result.stderr}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
