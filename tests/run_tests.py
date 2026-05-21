#!/usr/bin/env python3
"""
run_tests.py — Test runner for Beamer Deck Auto
===============================================

Runs all test suites. Supports filtering by test name.

Usage:
  python tests/run_tests.py              # Run all tests
  python tests/run_tests.py smoke        # Run only smoke tests
  python tests/run_tests.py unit         # Run only unit tests
  python tests/run_tests.py integration  # Run only integration tests
  python tests/run_tests.py font         # Run only font-config tests
  python tests/run_tests.py build        # Run only build script tests
"""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
TESTS_DIR = PROJECT_ROOT / "tests"


def load_tests(loader, pattern="test_*.py"):
    """Discover and load all test modules"""
    suite = unittest.TestSuite()
    for test_file in sorted(TESTS_DIR.glob(pattern)):
        if test_file.name == "run_tests.py":
            continue
        # Load directly from file path
        try:
            tests = loader.loadTestsFromName(test_file.stem)
            suite.addTests(tests)
        except Exception as e:
            print(f"WARNING: Could not load {test_file.stem}: {e}")
    return suite


def main():
    filter_arg = sys.argv[1] if len(sys.argv) > 1 else None

    loader = unittest.TestLoader()

    if filter_arg == "smoke":
        print("=== Running Smoke Tests ===")
        suite = loader.loadTestsFromName("test_smoke")
    elif filter_arg == "unit":
        print("=== Running Unit Tests ===")
        suite = loader.loadTestsFromName("test_font_config")
        suite.addTests(loader.loadTestsFromName("test_build_scripts"))
    elif filter_arg == "integration":
        print("=== Running Integration Tests ===")
        suite = loader.loadTestsFromName("test_layout_optimizer")
        suite.addTests(loader.loadTestsFromName("test_check_layout"))
    elif filter_arg == "font":
        print("=== Running Font Config Tests ===")
        suite = loader.loadTestsFromName("test_font_config")
    elif filter_arg == "build":
        print("=== Running Build Script Tests ===")
        suite = loader.loadTestsFromName("test_build_scripts")
    else:
        print("=== Running All Tests ===")
        suite = load_tests(loader)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Exit with non-zero if tests failed
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
