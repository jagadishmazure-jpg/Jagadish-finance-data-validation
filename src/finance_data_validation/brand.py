"""Brand/name guard: blocklisted names must not appear in repo docs.

The blocklist is stored as SHA-256 hashes only, never as plain names, so
the guard itself cannot leak the names it guards against. ``check_text``
normalises text and hashes every 1- to 4-word run, so a blocklisted
multi-word name is caught wherever it appears, while ordinary words pass.
"""

from __future__ import annotations

import hashlib
import re

# SHA-256 hashes of names that must not appear in this repo's docs.
# Kept as hashes deliberately: see scripts/brand_check.py.
BLOCKLIST_HASHES = {
    "c952a08fdb0ff916b78a489ff321a4eb73d258612ededdd834c5a7c55fbc6c70",
    "5e43fa8fc186bf403a2de960d645a0cfc4bd2cf3fe59121bac118b48b9e00b89",
    "17e9b17189f2f67e00b4c8dce8a6bedb38051ee221602fd52c88650ef9f68687",
    "f7782dfdd1ab18af5f652ca9f73991237ef367dd6c3d1021a68658117915d118",
    "adafc599c1ebe8e7a2bf8489528d79cb2704022b3b5766f219afeae8d2d10bc0",
    "3b8eccd79c406969d8fa1a98deea4b0a3d13df5959d6ea421b99222a64055246",
    "d5c8e96de8c104e4597cd8a2848171d44c291a2bd96858339694b707dd13c867",
}

_WORD = re.compile(r"[a-z0-9]+")


def _ngram_hashes(text: str):
    words = _WORD.findall(text.lower())
    for size in (1, 2, 3, 4):
        for i in range(len(words) - size + 1):
            phrase = " ".join(words[i:i + size])
            yield hashlib.sha256(phrase.encode()).hexdigest()


def check_text(text: str) -> bool:
    """Return True when ``text`` contains a blocklisted name."""
    return any(h in BLOCKLIST_HASHES for h in _ngram_hashes(text))
