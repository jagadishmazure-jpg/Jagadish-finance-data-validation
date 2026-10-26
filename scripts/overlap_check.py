#!/usr/bin/env python3
"""8-word overlap check: repo docs vs. a source text file.

Usage: python3 scripts/overlap_check.py <source-text-file> [repo-root]
Builds normalised 8-word shingles from the source, then reports any
shingle that also appears in the repo's Markdown docs. Target: 0 hits.
The source file itself is never committed to the repo.
"""

import re
import sys
from pathlib import Path

WORD = re.compile(r"[a-z0-9]+")


def shingles(text: str, n: int = 8):
    words = WORD.findall(text.lower())
    return {" ".join(words[i:i + n]) for i in range(len(words) - n + 1)}


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: overlap_check.py <source-text-file> [repo-root]")
        return 2
    source = Path(sys.argv[1]).read_text(errors="replace")
    root = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).parent.parent
    source_shingles = shingles(source)
    hits = []
    for path in sorted(root.rglob("*.md")):
        if ".git" in path.parts:
            continue
        overlap = sorted(shingles(path.read_text(errors="replace"))
                         & source_shingles)
        if overlap:
            hits.append((str(path), overlap))
    if hits:
        print("OVERLAP CHECK FAILED:")
        for path, overlap in hits:
            for item in overlap[:10]:
                print(f"  {path}: {item!r}")
        return 1
    print("overlap check passed: 0 eight-word matches against source text")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
