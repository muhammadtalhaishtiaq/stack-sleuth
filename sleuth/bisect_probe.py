#!/usr/bin/env python3
"""Exit-code probe for `git bisect run`-style evaluation.

Usage: bisect_probe.py <repo_path>

Exit 0   -> the bulk-discount behavior is correct at this commit (good)
Exit 1   -> the behavior is broken at this commit (bad)
Exit 125 -> cannot be evaluated here, e.g. the feature does not exist yet (skip)
"""
import subprocess
import sys

PROBE = """
import sys
sys.path.insert(0, {repo!r})
try:
    from pricing import bulk_discount_rate, total
except ImportError:
    sys.exit(125)
got = total([(10.0, 10)])
sys.exit(0 if abs(got - 90.0) < 1e-9 else 1)
"""


def main():
    repo = sys.argv[1]
    p = subprocess.run(
        [sys.executable, "-B", "-c", PROBE.format(repo=repo)],
        capture_output=True, text=True, timeout=60,
    )
    sys.exit(p.returncode)


if __name__ == "__main__":
    main()
