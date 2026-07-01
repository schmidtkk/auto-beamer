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
            "skills/autobeamer-build/SKILL.md",
            "skills/autobeamer-create/SKILL.md",
            "skills/autobeamer-layout/SKILL.md",
            "skills/autobeamer-review/SKILL.md",
            "skills/autobeamer-validate/SKILL.md",
        ):
            text = read(skill_path)
            for pattern in legacy_patterns:
                with self.subTest(skill=skill_path, pattern=pattern):
                    self.assertIsNone(re.search(pattern, text))

    def test_primary_skills_use_current_mode_labels(self) -> None:
        deprecated_patterns = (
            r"Presentation mode",
            r"Mentor mode",
            r"Presentation default",
            r"Mentor override",
        )
        for skill_path in sorted((ROOT / "skills").glob("autobeamer-*/SKILL.md")):
            text = skill_path.read_text(encoding="utf-8")
            for pattern in deprecated_patterns:
                with self.subTest(skill=skill_path.name, pattern=pattern):
                    self.assertIsNone(re.search(pattern, text, flags=re.IGNORECASE))

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


SKILL_PATHS = sorted(str(p.relative_to(ROOT)) for p in (ROOT / "skills").glob("autobeamer-*/SKILL.md"))


def frontmatter(skill_rel_path: str) -> str:
    text = read(skill_rel_path)
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    assert match, f"no YAML frontmatter in {skill_rel_path}"
    return match.group(1)


class SkillPluginHardeningTest(unittest.TestCase):
    """Regression coverage for the 2026-06 hardening pass."""

    def test_all_skills_share_consistent_frontmatter(self) -> None:
        self.assertGreaterEqual(len(SKILL_PATHS), 10)
        required = ("name", "description", "when_to_use", "argument-hint", "allowed-tools")
        for path in SKILL_PATHS:
            fm = frontmatter(path)
            for field in required:
                with self.subTest(skill=path, field=field):
                    self.assertRegex(fm, rf"(?m)^{re.escape(field)}:")

    def test_no_bare_beamer_skill_names(self) -> None:
        # Every cross-reference must use the autobeamer-* prefix, never legacy
        # "beamer-review" / "beamer-layout" / etc.
        pattern = re.compile(r"(?<![A-Za-z])beamer-(review|layout|build|create|tikz|validate)")
        targets = SKILL_PATHS + ["memories/MEMORY_INDEX.md"]
        for path in targets:
            with self.subTest(path=path):
                self.assertIsNone(pattern.search(read(path)))

    def test_gv4_threshold_matches_optimizer(self) -> None:
        # layout_optimizer.py treats SIDE as balanced only at AR <= 1.4.
        for path in ("skills/autobeamer-review/SKILL.md", "skills/autobeamer-layout/SKILL.md"):
            text = read(path)
            with self.subTest(skill=path):
                self.assertIn("AR>1.4", text)
                self.assertNotIn("AR>1.5", text)

    def test_validate_counts_overfull_vbox(self) -> None:
        text = read("skills/autobeamer-validate/SKILL.md")
        self.assertIn(r"Overfull \vbox", text)
        self.assertRegex(text, r"(?i)vbox \(slide overflow\)")

    def test_create_cross_links_validate(self) -> None:
        self.assertIn("autobeamer-validate", read("skills/autobeamer-create/SKILL.md"))

    def test_png_directory_is_standardized(self) -> None:
        for path in (
            "skills/autobeamer-build/SKILL.md",
            "skills/autobeamer-layout/SKILL.md",
            "skills/autobeamer-validate/SKILL.md",
        ):
            text = read(path)
            with self.subTest(skill=path):
                self.assertIn("_slides_png", text)
                # No bare `pdftoppm ... slides_png` output target (missing underscore).
                self.assertIsNone(re.search(r"pdftoppm[^\n]*[^_]slides_png\b", text))

    def test_skill_memory_present_and_clean(self) -> None:
        self.assertTrue((ROOT / "memories" / "MEMORY_INDEX.md").exists())
        self.assertTrue((ROOT / "memories" / "repo" / "user-preferences.md").exists())
        index = read("memories/MEMORY_INDEX.md")
        # No dangling reference to a memory file that does not ship.
        self.assertNotIn("feedback-underbrace-fix.md", index)
        self.assertIn("autobeamer-tikz", index)

    def test_manifests_have_no_empty_email(self) -> None:
        for path in (".claude-plugin/plugin.json", ".claude-plugin/marketplace.json", ".codex-plugin/plugin.json"):
            with self.subTest(path=path):
                self.assertNotIn('"email": ""', read(path))


class LanguageGateTest(unittest.TestCase):
    """The executable language-quality gate (lang_lint.py) and its wiring."""

    def test_lang_lint_tool_exists(self) -> None:
        self.assertTrue((ROOT / "tools" / "lang_lint.py").exists())

    def test_canonical_gate_and_rubric_references_exist(self) -> None:
        for path in (
            "skills/autobeamer-review/references/language-quality-gate.md",
            "skills/autobeamer-review/references/quality-rubric.md",
        ):
            with self.subTest(path=path):
                self.assertTrue((ROOT / path).exists())

    def test_gate_is_wired_into_validate_create_review(self) -> None:
        for path in (
            "skills/autobeamer-validate/SKILL.md",
            "skills/autobeamer-create/SKILL.md",
            "skills/autobeamer-review/SKILL.md",
        ):
            with self.subTest(path=path):
                self.assertIn("lang_lint.py", read(path))
        self.assertIn("language-quality-gate.md", read("skills/autobeamer-review/SKILL.md"))

    def test_finisher_agent_runs_language_gate(self) -> None:
        self.assertIn("lang_lint.py", read("agents/autobeamer-finisher.md"))

    def test_canonical_gate_owns_the_four_axes(self) -> None:
        gate = read("skills/autobeamer-review/references/language-quality-gate.md")
        for axis in ("流畅性", "准确度", "优雅性", "科学性"):
            with self.subTest(axis=axis):
                self.assertIn(axis, gate)


class ThreeWaveCreatePipelineTest(unittest.TestCase):
    """Coverage for the leader + 3-wave create pipeline and image index."""

    WAVE_AGENTS = ("autobeamer-planner", "autobeamer-drafter", "autobeamer-finisher")

    def test_wave_agents_exist_with_frontmatter(self) -> None:
        for name in self.WAVE_AGENTS:
            path = f"agents/{name}.md"
            with self.subTest(agent=path):
                self.assertTrue((ROOT / path).exists(), f"missing {path}")
                fm = frontmatter(path)
                self.assertRegex(fm, rf"(?m)^name:\s*{re.escape(name)}\b")
                self.assertRegex(fm, r"(?m)^tools:")

    def test_agents_declared_in_manifests(self) -> None:
        for path in (".claude-plugin/plugin.json",
                     ".claude-plugin/marketplace.json",
                     ".codex-plugin/plugin.json"):
            with self.subTest(path=path):
                self.assertIn('"agents"', read(path),
                              f"{path} must declare an agents path")

    def test_create_skill_wires_index_alignment_and_waves(self) -> None:
        text = read("skills/autobeamer-create/SKILL.md")
        self.assertIn("references/images/image-index.md", text)
        self.assertIn("references/validation/alignment-check.md", text)
        for name in self.WAVE_AGENTS:
            with self.subTest(agent=name):
                self.assertIn(name, text)

    def test_new_reference_docs_exist(self) -> None:
        for path in (
            "skills/autobeamer-create/references/images/image-index.md",
            "skills/autobeamer-create/references/validation/alignment-check.md",
        ):
            with self.subTest(path=path):
                self.assertTrue((ROOT / path).exists())

    def test_phase_3_and_4_are_merged(self) -> None:
        guide = read("skills/autobeamer-create/references/workflows/full-create-guide.md")
        self.assertRegexpMatches = self.assertRegex  # py-compat alias
        self.assertRegex(guide, r"(?i)draft\s*\+\s*figures|one\s+wave")
        self.assertIn("image-index.md", guide)

    def test_image_index_tool_present(self) -> None:
        self.assertTrue((ROOT / "tools" / "image_index.py").exists())


class EnvironmentDoctorTest(unittest.TestCase):
    """Coverage for the dependency doctor and its wiring into planning."""

    def test_doctor_tool_and_reference_exist(self) -> None:
        self.assertTrue((ROOT / "tools" / "doctor.py").exists())
        self.assertTrue((ROOT / "skills/autobeamer-create/references/validation/env-doctor.md").exists())

    def test_create_skill_runs_doctor_first(self) -> None:
        text = read("skills/autobeamer-create/SKILL.md")
        self.assertIn("tools/doctor.py", text)
        self.assertIn("env-doctor.md", text)

    def test_planner_agent_runs_doctor(self) -> None:
        text = read("agents/autobeamer-planner.md")
        self.assertIn("doctor.py", text)

    def test_gitignore_excludes_env_state(self) -> None:
        self.assertRegex(read(".gitignore"), r"(?m)^\.autobeamer/")

    def test_build_skill_documents_doctor_action(self) -> None:
        self.assertIn("doctor", read("skills/autobeamer-build/SKILL.md"))

    def test_dedicated_doctor_skill_exists_and_runs_tool(self) -> None:
        path = "skills/autobeamer-doctor/SKILL.md"
        self.assertTrue((ROOT / path).exists())
        text = read(path)
        self.assertIn("tools/doctor.py", text)
        self.assertRegex(frontmatter(path), r"(?m)^name:\s*autobeamer-doctor\b")


if __name__ == "__main__":
    unittest.main()
