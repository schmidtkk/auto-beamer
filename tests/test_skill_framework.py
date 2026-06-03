"""Regression tests for AutoBeamer skill framework guidance."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


class SkillFrameworkGuidanceTest(unittest.TestCase):
    def test_validate_checks_all_overlay_commands(self) -> None:
        text = read("skills/autobeamer-validate/SKILL.md")
        for command in (r"\pause", r"\onslide", r"\only", r"\uncover"):
            with self.subTest(command=command):
                self.assertIn(command, text)

    def test_validate_uses_correct_sixteen_by_nine_ratio(self) -> None:
        text = read("skills/autobeamer-validate/SKILL.md")
        self.assertNotIn("364.19", text)
        self.assertNotIn("272.65", text)
        self.assertNotIn("1.336", text)
        self.assertRegex(text, r"16:9|16/9|1\.77")
        self.assertNotRegex(text, r"1\.30[–-]1\.37")

    def test_no_mentor_five_block_exception(self) -> None:
        for skill_path in (
            "skills/autobeamer-create/SKILL.md",
            "skills/autobeamer-layout/SKILL.md",
        ):
            with self.subTest(skill=skill_path):
                text = read(skill_path)
                self.assertNotRegex(text, r"(?i)5\s+blocks")
                self.assertNotRegex(text, r"(?i)blocks\s*\|\s*5")
                self.assertNotRegex(text, r"(?i)block count <= 5")

    def test_primary_skills_do_not_prescribe_legacy_box_macros(self) -> None:
        legacy_patterns = (
            r"\\begin\{goldcall\}",
            r"\\end\{goldcall\}",
            r"\\begin\{bluecard\}",
            r"\\begin\{eqbox\}",
            r"\\budgetwideimg",
            r"`goldcall`",
            r"`bluecard`",
            r"`eqbox`",
        )
        for skill_path in (
            "skills/autobeamer-layout/SKILL.md",
            "skills/autobeamer-review/SKILL.md",
            "skills/autobeamer-validate/SKILL.md",
        ):
            text = read(skill_path)
            for pattern in legacy_patterns:
                with self.subTest(skill=skill_path, pattern=pattern):
                    self.assertIsNone(re.search(pattern, text))


if __name__ == "__main__":
    unittest.main()
