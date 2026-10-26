#!/usr/bin/env python3
"""Scan repo Markdown docs for blocklisted names (hash-based).

Usage: python3 scripts/brand_check.py [repo-root]
Exits non-zero and prints the offending file on any hit.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from finance_data_validation import brand  # noqa: E402


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent.parent
    hits = []
    for path in sorted(root.rglob("*.md")):
        if ".git" in path.parts:
            continue
        if brand.check_text(path.read_text(errors="replace")):
            hits.append(str(path))
    if hits:
        print("BRAND CHECK FAILED:")
        for hit in hits:
            print(f"  blocklisted name in {hit}")
        return 1
    print("brand check passed: no blocklisted names in Markdown docs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
