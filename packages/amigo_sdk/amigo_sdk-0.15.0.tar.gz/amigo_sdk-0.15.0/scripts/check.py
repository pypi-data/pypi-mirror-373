#!/usr/bin/env python3
"""
Development check script - runs formatting, linting, and tests.

Usage:
    python scripts/check.py           # Run all checks
    python scripts/check.py --fix     # Run all checks and auto-fix issues
    python scripts/check.py --fast    # Skip tests (format + lint only)
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return True if successful."""
    print(f"🔍 {description}...")

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd=Path(__file__).parent.parent
        )

        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            if result.stdout:
                print(f"   {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} - FAILED")
            if result.stdout:
                print(f"   stdout: {result.stdout.strip()}")
            if result.stderr:
                print(f"   stderr: {result.stderr.strip()}")
            return False

    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Run development checks")
    parser.add_argument(
        "--fix", action="store_true", help="Auto-fix linting and formatting issues"
    )
    parser.add_argument(
        "--fast", action="store_true", help="Skip tests (format + lint only)"
    )
    args = parser.parse_args()

    print("🚀 Running development checks...\n")

    all_passed = True

    # 1. Format check or fix
    if args.fix:
        success = run_command(["ruff", "format", "."], "Code formatting (auto-fix)")
    else:
        success = run_command(
            ["ruff", "format", "--check", "."], "Code formatting check"
        )
    all_passed &= success

    print()

    # 2. Lint check or fix
    if args.fix:
        success = run_command(["ruff", "check", ".", "--fix"], "Linting (auto-fix)")
    else:
        success = run_command(["ruff", "check", "."], "Linting check")
    all_passed &= success

    print()

    # 3. Tests (unless --fast)
    if not args.fast:
        success = run_command(
            ["pytest", "--cov=src", "--cov-report=term", "-v"],
            "Test suite with coverage",
        )
        all_passed &= success
        print()

    # Summary
    print("=" * 50)
    if all_passed:
        print("🎉 All checks PASSED! Ready to commit.")
        if args.fast:
            print("💡 Run without --fast to include tests.")
        sys.exit(0)
    else:
        print("💥 Some checks FAILED!")
        if not args.fix:
            print("💡 Try running with --fix to auto-fix formatting/linting issues.")
        sys.exit(1)


if __name__ == "__main__":
    main()
