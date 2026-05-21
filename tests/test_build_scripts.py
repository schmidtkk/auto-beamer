#!/usr/bin/env python3
"""
test_build_scripts.py — Tests for build scripts
===============================================

Verifies build script syntax and structure without executing them.

Run: python tests/test_build_scripts.py
"""

import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


class TestBuildCleanPs1(unittest.TestCase):
    """Tests for build_clean.ps1"""

    @classmethod
    def setUpClass(cls):
        cls.script_path = PROJECT_ROOT / "build_clean.ps1"
        cls.content = cls.script_path.read_text(encoding="utf-8")

    def test_file_exists(self):
        """build_clean.ps1 must exist"""
        self.assertTrue(self.script_path.exists(), "build_clean.ps1 not found")

    def test_has_param_block(self):
        """Must have param block for deck name"""
        self.assertIn("param(", self.content, "Missing param block")
        self.assertIn("$Deck", self.content, "Missing $Deck parameter")

    def test_has_xelatex_call(self):
        """Must call xelatex"""
        self.assertIn("xelatex", self.content, "Missing xelatex call")

    def test_has_two_passes(self):
        """Must compile twice (for equal height group)"""
        # Check for loop with 2 passes
        has_loop = "for ($pass = 1; $pass -le 2; $pass++)" in self.content
        pass_count = self.content.count("xelatex")
        self.assertTrue(
            has_loop or pass_count >= 2,
            f"Expected two-pass compilation loop, found {pass_count} xelatex calls"
        )

    def test_has_overfull_check(self):
        """Must check for Overfull \\vbox"""
        self.assertIn("Overfull", self.content,
                      "Missing Overfull \\vbox check")

    def test_has_clean_function(self):
        """Must have clean function"""
        self.assertIn("function Clean-BuildFiles", self.content,
                      "Missing Clean-BuildFiles function")

    def test_has_build_function(self):
        """Must have build function"""
        self.assertIn("function Build-Deck", self.content,
                      "Missing Build-Deck function")

    def test_copies_pdf(self):
        """Must copy PDF to project root"""
        self.assertIn("Copy-Item", self.content,
                      "Missing PDF copy step")


class TestBuildSh(unittest.TestCase):
    """Tests for build.sh"""

    @classmethod
    def setUpClass(cls):
        cls.script_path = PROJECT_ROOT / "build.sh"
        cls.content = cls.script_path.read_text(encoding="utf-8")

    def test_file_exists(self):
        """build.sh must exist"""
        self.assertTrue(self.script_path.exists(), "build.sh not found")

    def test_has_shebang(self):
        """Must have bash shebang"""
        self.assertTrue(
            self.content.startswith("#!/bin/bash") or
            self.content.startswith("#!/usr/bin/env bash"),
            "Missing bash shebang"
        )

    def test_has_xelatex_call(self):
        """Must call xelatex"""
        self.assertIn("xelatex", self.content, "Missing xelatex call")

    def test_has_two_passes(self):
        """Must compile twice"""
        # Check for loop with 2 passes
        self.assertTrue(
            "for pass in 1 2" in self.content or
            self.content.count("xelatex") >= 2,
            "Missing two-pass compilation"
        )

    def test_has_overfull_check(self):
        """Must check for Overfull \\vbox"""
        self.assertIn("Overfull", self.content,
                      "Missing Overfull \\vbox check")

    def test_has_clean_function(self):
        """Must have clean function"""
        self.assertIn("clean_build_files", self.content,
                      "Missing clean_build_files function")

    def test_copies_pdf(self):
        """Must copy PDF to project root"""
        self.assertIn("cp -f", self.content,
                      "Missing PDF copy step")

    def test_checks_xelatex(self):
        """Must check xelatex is available"""
        self.assertIn("command -v xelatex", self.content,
                      "Missing xelatex availability check")

    def test_creates_build_dir(self):
        """Must create build directory"""
        self.assertIn("mkdir -p", self.content,
                      "Missing build directory creation")


class TestInstallLinuxSh(unittest.TestCase):
    """Tests for install-linux.sh"""

    @classmethod
    def setUpClass(cls):
        cls.script_path = PROJECT_ROOT / "install-linux.sh"
        cls.content = cls.script_path.read_text(encoding="utf-8")

    def test_file_exists(self):
        """install-linux.sh must exist"""
        self.assertTrue(self.script_path.exists(), "install-linux.sh not found")

    def test_has_shebang(self):
        """Must have bash shebang"""
        self.assertTrue(
            self.content.startswith("#!/bin/bash") or
            self.content.startswith("#!/usr/bin/env bash"),
            "Missing bash shebang"
        )

    def test_installs_texlive(self):
        """Must install TeX Live packages"""
        self.assertIn("texlive-xetex", self.content,
                      "Missing texlive-xetex installation")
        self.assertIn("texlive-latex-extra", self.content,
                      "Missing texlive-latex-extra installation")

    def test_installs_cjk_fonts(self):
        """Must mention CJK font installation"""
        self.assertIn("fonts-noto-cjk", self.content,
                      "Missing fonts-noto-cjk reference")

    def test_installs_poppler(self):
        """Must install poppler-utils for pdftoppm"""
        self.assertIn("poppler-utils", self.content,
                      "Missing poppler-utils installation")

    def test_installs_python(self):
        """Must install Python"""
        self.assertIn("python3", self.content,
                      "Missing python3 installation")

    def test_verifies_xelatex(self):
        """Must verify xelatex installation"""
        self.assertIn("xelatex --version", self.content,
                      "Missing xelatex version check")

    def test_checks_cjk_fonts(self):
        """Must check CJK fonts after install"""
        self.assertIn("fc-list", self.content,
                      "Missing fc-list CJK font check")

    def test_has_package_manager_detection(self):
        """Must detect package manager"""
        self.assertIn("apt-get", self.content,
                      "Missing apt-get reference")
        self.assertIn("PKG_MANAGER", self.content,
                      "Missing PKG_MANAGER variable")

    def test_sets_executable_bit(self):
        """Must mention chmod +x"""
        self.assertIn("chmod +x", self.content,
                      "Missing chmod +x instruction")


if __name__ == "__main__":
    unittest.main(verbosity=2)
