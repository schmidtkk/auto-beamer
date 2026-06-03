"""Tests for executable AutoBeamer static validation gates."""

from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools" / "validate_deck.py"
FIXTURES = ROOT / "tests" / "fixtures" / "validate"


def run_validator(filename: str, mode: str = "academic-presentation") -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(VALIDATOR),
            "static",
            str(FIXTURES / filename),
            "--mode",
            mode,
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


class ValidateDeckStaticTest(unittest.TestCase):
    def test_uncover_overlay_fails_validation(self) -> None:
        result = run_validator("illegal_uncover.tex")
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(r"\uncover", result.stdout)
        self.assertIn("overlay", result.stdout.lower())

    def test_references_must_be_before_thank_you(self) -> None:
        result = run_validator("bad_references_order.tex")
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("References", result.stdout)
        self.assertIn("Thank You", result.stdout)

    def test_appendix_must_precede_backup_slides(self) -> None:
        result = run_validator("missing_appendix_backup.tex")
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(r"\appendix", result.stdout)
        self.assertIn("backup", result.stdout.lower())

    def test_valid_academic_presentation_static_gates_pass(self) -> None:
        result = run_validator("valid_academic_presentation.tex")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("PASS", result.stdout)


if __name__ == "__main__":
    unittest.main()
