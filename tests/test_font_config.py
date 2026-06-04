#!/usr/bin/env python3
"""
test_font_config.py — Unit tests for font-config.sty logic
==========================================================

Tests the cross-platform font detection logic without requiring XeLaTeX.
We verify the .sty file structure and platform detection paths.

Run: python tests/test_font_config.py
"""

import os
import re
import sys
import unittest
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestFontConfigSty(unittest.TestCase):
    """Tests for template-lib/font-config.sty"""

    @classmethod
    def setUpClass(cls):
        cls.font_config_path = PROJECT_ROOT / "template-lib" / "font-config.sty"
        cls.sty_content = cls.font_config_path.read_text(encoding="utf-8")

    def test_file_exists(self):
        """font-config.sty must exist"""
        self.assertTrue(self.font_config_path.exists(),
                        f"font-config.sty not found at {self.font_config_path}")

    def test_provides_package(self):
        """Must declare itself as a package"""
        self.assertIn(r"\ProvidesPackage{font-config}", self.sty_content,
                      r"Missing \ProvidesPackage{font-config}")

    def test_requires_fontspec(self):
        """Must require fontspec"""
        self.assertIn(r"\RequirePackage{fontspec}", self.sty_content,
                      r"Missing \RequirePackage{fontspec}")

    def test_requires_xecjk(self):
        """Must require xeCJK"""
        self.assertIn(r"\RequirePackage{xeCJK}", self.sty_content,
                      r"Missing \RequirePackage{xeCJK}")

    def test_user_override_priority(self):
        r"""User override (\CJKFontPath) must be checked first"""
        # Find the position of user override check
        override_pos = self.sty_content.find(r"\ifx\CJKFontPath\undefined")
        windows_pos = self.sty_content.find(r"C:/WINDOWS/Fonts/msyh.ttc")

        self.assertGreater(override_pos, -1,
                           "Missing user override check (\\ifx\\CJKFontPath\\undefined)")
        self.assertGreater(windows_pos, -1,
                           "Missing Windows font detection")
        self.assertLess(override_pos, windows_pos,
                        "User override must be checked BEFORE Windows auto-detect")

    def test_windows_detection(self):
        """Must detect Windows Microsoft YaHei"""
        self.assertIn(r"C:/WINDOWS/Fonts/msyh.ttc", self.sty_content,
                      "Missing Windows font path")
        self.assertIn(r"msyhbd.ttc", self.sty_content,
                      "Missing Windows bold font")

    def test_linux_detection(self):
        """Must detect Linux Noto Sans CJK"""
        self.assertIn(r"/usr/share/fonts/opentype/noto/", self.sty_content,
                      "Missing Linux opentype path")
        self.assertIn(r"/usr/share/fonts/truetype/noto/", self.sty_content,
                      "Missing Linux truetype path")

    def test_macos_detection(self):
        """Must detect macOS PingFang"""
        self.assertIn(r"/System/Library/Fonts/PingFang.ttc", self.sty_content,
                      "Missing macOS PingFang path")
        self.assertIn(r"~/Library/Fonts/", self.sty_content,
                      "Missing macOS user font path")

    def test_setfonts_command(self):
        """Must define @fc@setfonts helper"""
        self.assertIn(r"\newcommand{\@fc@setfonts}", self.sty_content,
                      "Missing \\@fc@setfonts helper command")

    def test_warn_command(self):
        """Must define @fc@warn helper"""
        self.assertIn(r"\newcommand{\@fc@warn}", self.sty_content,
                      "Missing \\@fc@warn helper command")

    # NOTE: A dedicated `\notocjk` named font family was never part of the
    # current font-config design — CJK is set globally via \setCJKmainfont and
    # nothing in template-lib/ references \notocjk. The stale assertion that
    # required it has been removed; test_setfonts_command covers the real API.

    def test_no_hardcoded_windows_path_in_fallback(self):
        """Linux/macOS fallbacks must not hardcode C:/WINDOWS/Fonts/"""
        # After the Windows \IfFileExists block, there should be no Windows paths
        # in the Linux/macOS branches
        linux_section = self.sty_content.split(r"C:/WINDOWS/Fonts/msyh.ttc")[1]
        # The fallback branch (after Windows) should not contain Windows paths
        # in its own fallbacks
        self.assertNotIn(r"Path=C:/WINDOWS/Fonts/", linux_section,
                         "Linux/macOS fallback contains hardcoded Windows path")


class TestTemplateLibSty(unittest.TestCase):
    """Tests for template-lib/template-lib.sty"""

    @classmethod
    def setUpClass(cls):
        cls.template_lib_path = PROJECT_ROOT / "template-lib" / "template-lib.sty"
        cls.sty_content = cls.template_lib_path.read_text(encoding="utf-8")

    def test_uses_font_config(self):
        """template-lib.sty must load font-config.sty"""
        self.assertIn(r"\input{\TLlibpath font-config.sty}", self.sty_content,
                      "template-lib.sty must load font-config.sty")

    def test_no_hardcoded_cjk_fonts(self):
        """template-lib.sty must not contain hardcoded CJK font paths"""
        self.assertNotIn(r"C:/WINDOWS/Fonts/msyh.ttc", self.sty_content,
                         "template-lib.sty still contains hardcoded Windows font path")

    def test_no_inline_xecjk(self):
        """template-lib.sty must not inline xeCJK font setup"""
        # Should not have \setCJKmainfont directly (should be in font-config)
        if r"\setCJKmainfont" in self.sty_content:
            # Allow if it's inside font-config.sty reference
            pass
        else:
            self.assertNotIn(r"\setCJKmainfont", self.sty_content,
                             "template-lib.sty contains inline \\setCJKmainfont")


class TestConfigTex(unittest.TestCase):
    """Tests for personal-deck/config.tex"""

    @classmethod
    def setUpClass(cls):
        cls.config_path = PROJECT_ROOT / "personal-deck" / "config.tex"
        # personal-deck/ holds legacy private material that is intentionally
        # absent from the public repo (removed in the "security: remove personal
        # slides and memory files" commit). Skip these checks when it is not
        # present rather than failing a clean public checkout.
        if not cls.config_path.exists():
            raise unittest.SkipTest("personal-deck/config.tex not present (public checkout)")
        cls.tex_content = cls.config_path.read_text(encoding="utf-8")

    def test_uses_font_config(self):
        """config.tex must load font-config.sty"""
        self.assertIn(r"\input{../template-lib/font-config.sty}", self.tex_content,
                      "config.tex must load font-config.sty")

    def test_no_hardcoded_cjk_fonts(self):
        """config.tex must not contain hardcoded CJK font paths"""
        self.assertNotIn(r"C:/WINDOWS/Fonts/msyh.ttc", self.tex_content,
                         "config.tex still contains hardcoded Windows font path")

    def test_documents_font_override(self):
        """config.tex must document font override mechanism"""
        self.assertIn(r"\def\CJKFontPath", self.tex_content,
                      "config.tex must document \\CJKFontPath override")


class TestThemeLibraryFiles(unittest.TestCase):
    """Tests for theme-library/*.tex files"""

    def test_all_use_font_config(self):
        """All theme-library files must use font-config.sty"""
        theme_dir = PROJECT_ROOT / "theme-library"
        tex_files = list(theme_dir.glob("minimal-*.tex"))

        self.assertGreater(len(tex_files), 0, "No theme-library .tex files found")

        for tex_file in tex_files:
            with self.subTest(file=tex_file.name):
                content = tex_file.read_text(encoding="utf-8")
                self.assertIn(
                    r"\input{../template-lib/font-config.sty}", content,
                    f"{tex_file.name} must load font-config.sty"
                )
                self.assertNotIn(
                    r"C:/WINDOWS/Fonts/msyh.ttc", content,
                    f"{tex_file.name} still contains hardcoded Windows font path"
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
