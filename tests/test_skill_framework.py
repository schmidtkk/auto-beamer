"""Regression tests for AutoBeamer skill framework guidance."""

from pathlib import Path
import json
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

    def test_validate_static_mode_gates_are_wired(self) -> None:
        validate_text = read("skills/autobeamer-validate/SKILL.md")
        create_text = read("skills/autobeamer-create/SKILL.md")
        gates_text = read("skills/autobeamer-create/references/validation/mode-gates.md")

        self.assertIn("tools/validate_deck.py static", validate_text)
        self.assertIn("references/validation/mode-gates.md", create_text)
        self.assertIn("second-to-last", validate_text)
        self.assertIn(r"\appendix", validate_text)
        self.assertIn("mode-specific", validate_text)
        for mode in ("passive-study", "active-socratic", "academic-presentation"):
            with self.subTest(mode=mode):
                self.assertIn(mode, gates_text)

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

    def test_create_skill_exposes_three_first_class_modes(self) -> None:
        text = read("skills/autobeamer-create/SKILL.md")
        for mode in ("passive-study", "active-socratic", "academic-presentation"):
            with self.subTest(mode=mode):
                self.assertIn(mode, text)
        self.assertIn("references/modes/passive-study.md", text)
        self.assertIn("references/modes/active-socratic.md", text)
        self.assertIn("references/modes/academic-presentation.md", text)

    def test_create_skill_is_compact_progressive_disclosure_router(self) -> None:
        text = read("skills/autobeamer-create/SKILL.md")
        line_count = len(text.splitlines())
        self.assertLessEqual(line_count, 220)
        for path in (
            "references/workflows/full-create-guide.md",
            "references/images/source-document-first.md",
            "references/validation/mode-gates.md",
            "references/modes/passive-study.md",
            "references/modes/active-socratic.md",
            "references/modes/academic-presentation.md",
        ):
            with self.subTest(path=path):
                self.assertIn(path, text)
                self.assertTrue((ROOT / "skills" / "autobeamer-create" / path).exists())

    def test_review_skill_exposes_three_mode_rubrics(self) -> None:
        text = read("skills/autobeamer-review/SKILL.md")
        for mode in ("passive-study", "active-socratic", "academic-presentation"):
            with self.subTest(mode=mode):
                self.assertIn(mode, text)
        self.assertIn("references/rubrics/passive-study-review.md", text)
        self.assertIn("references/rubrics/active-socratic-review.md", text)
        self.assertIn("references/rubrics/academic-presentation-review.md", text)

    def test_mode_reference_files_encode_distinct_learning_philosophies(self) -> None:
        expected_terms = {
            "skills/autobeamer-create/references/modes/passive-study.md": (
                "background",
                "shield",
                "self-contained",
            ),
            "skills/autobeamer-create/references/modes/active-socratic.md": (
                "question",
                "attempt",
                "thought experiment",
            ),
            "skills/autobeamer-create/references/modes/academic-presentation.md": (
                "audience",
                "time",
                "references",
            ),
            "skills/autobeamer-review/references/rubrics/passive-study-review.md": (
                "background",
                "frustration",
                "self-contained",
            ),
            "skills/autobeamer-review/references/rubrics/active-socratic-review.md": (
                "question",
                "attempt",
                "mentor",
            ),
            "skills/autobeamer-review/references/rubrics/academic-presentation-review.md": (
                "audience",
                "timing",
                "backup",
            ),
        }
        for path, terms in expected_terms.items():
            with self.subTest(path=path):
                text = read(path).lower()
                for term in terms:
                    self.assertIn(term, text)

    def test_source_document_first_image_policy_is_wired(self) -> None:
        create_text = read("skills/autobeamer-create/SKILL.md")
        review_text = read("skills/autobeamer-review/SKILL.md")
        policy_text = read("skills/autobeamer-create/references/images/source-document-first.md")

        self.assertIn("references/images/source-document-first.md", create_text)
        self.assertIn("paper_parser.py parse", create_text)
        self.assertIn("paper_parser.py extract-images", create_text)
        self.assertIn("source-document-first", policy_text)
        self.assertIn("provided PDF", policy_text)
        self.assertIn("external image", policy_text)
        self.assertIn("attribution", policy_text)
        self.assertIn("local", policy_text)
        self.assertIn("provenance", review_text)
        self.assertIn("source-document-first", review_text)

    def test_external_images_are_fallback_not_default(self) -> None:
        text = read("skills/autobeamer-create/references/images/source-document-first.md")
        self.assertRegex(text, r"(?is)provided PDF.*before.*web")
        self.assertRegex(text, r"(?is)external image.*fallback")
        self.assertRegex(text, r"(?is)never.*hotlink|no.*hotlink")

    def test_plugin_metadata_advertises_modes_and_image_policy(self) -> None:
        manifest_paths = (
            ".codex-plugin/plugin.json",
            ".claude-plugin/plugin.json",
            ".claude-plugin/marketplace.json",
        )
        for path in manifest_paths:
            with self.subTest(path=path):
                data = json.loads(read(path))
                blob = json.dumps(data, ensure_ascii=False)
                for term in (
                    "passive-study",
                    "active-socratic",
                    "academic-presentation",
                    "source-document-first",
                ):
                    self.assertIn(term, blob)

    def test_every_skill_has_openai_metadata(self) -> None:
        skill_dirs = sorted(
            path
            for path in (ROOT / "skills").iterdir()
            if path.is_dir() and (path / "SKILL.md").exists()
        )
        self.assertGreaterEqual(len(skill_dirs), 6)
        for skill_dir in skill_dirs:
            with self.subTest(skill=skill_dir.name):
                metadata = skill_dir / "agents" / "openai.yaml"
                self.assertTrue(metadata.exists())
                text = metadata.read_text(encoding="utf-8")
                self.assertIn("interface:", text)
                self.assertIn("default_prompt:", text)
                self.assertIn(f"${skill_dir.name}", text)


if __name__ == "__main__":
    unittest.main()
