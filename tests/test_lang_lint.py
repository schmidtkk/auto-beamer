"""Tests for the executable AutoBeamer language-quality gate (lang_lint.py)."""

from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
LINTER = ROOT / "tools" / "lang_lint.py"
FIXTURES = ROOT / "tests" / "fixtures" / "lang"


def run_lint(filename: str, mode: str = "passive-study", *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(LINTER), "lint", str(FIXTURES / filename), "--mode", mode, *extra],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


class LangLintTest(unittest.TestCase):
    def test_clean_chinese_deck_passes(self) -> None:
        result = run_lint("good.tex")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("PASS", result.stdout)

    def test_math_and_macros_never_flagged(self) -> None:
        # good.tex is full of $...$, \[...\], \TLtakeaway{}, term names — none may trip.
        result = run_lint("good.tex")
        for term in ("leakage", "ai-filler", "proof-hedge"):
            self.assertNotIn(term, result.stdout, result.stdout)

    def test_english_prose_leakage_is_critical(self) -> None:
        result = run_lint("bad.tex")
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("foreign-prose-leakage", result.stdout)
        self.assertIn("CRITICAL", result.stdout)

    def test_ai_filler_is_flagged(self) -> None:
        result = run_lint("bad.tex")
        self.assertIn("ai-filler", result.stdout)
        # specific filler from the fixture
        self.assertIn("值得注意的是", result.stdout)

    def test_proof_hedge_is_critical_in_passive_study(self) -> None:
        result = run_lint("bad.tex", "passive-study")
        self.assertIn("proof-hedge", result.stdout)
        # 显然 / 易证 should be CRITICAL in passive-study
        self.assertRegex(result.stdout, r"CRITICAL.*proof-hedge")

    def test_proof_hedge_is_advisory_in_presentation(self) -> None:
        # Same hedges, academic-presentation: not CRITICAL (sketches allowed).
        result = run_lint("bad.tex", "academic-presentation")
        self.assertNotRegex(result.stdout, r"CRITICAL.*proof-hedge")

    def test_english_deck_skips_leakage_gate(self) -> None:
        result = run_lint("english.tex", "academic-presentation")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("non-CJK deck", result.stdout)
        # No leakage *finding* line (the skip-note mentions the category by name).
        self.assertNotIn("· foreign-prose-leakage", result.stdout)

    def test_json_output_is_machine_readable(self) -> None:
        import json
        result = run_lint("bad.tex", "passive-study", "--json")
        payload = json.loads(result.stdout)
        self.assertIn("summary", payload)
        self.assertGreaterEqual(payload["summary"]["critical"], 1)


if __name__ == "__main__":
    unittest.main()
