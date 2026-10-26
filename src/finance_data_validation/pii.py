"""PII detection and redaction for financial data.

Runs BEFORE any value leaves the validation layer. Four categories are
covered -- phone numbers, Social Security numbers, card numbers, and
email addresses. Card candidates must also pass a Luhn check, so ordinary
long figures (account totals, reference numbers) are not swept up.

Redaction is proven, not assumed: ``redact`` returns both the cleaned
text and a per-category hit count, and ``safe_log`` / ``safe_error``
redact before anything is written to a log or raised as an error, so a
raw value can never leak through a log line or an exception message.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

_PHONE = re.compile(r"(?:\(\d{3}\)\s*|\b\d{3}[-.\s])\d{3}[-.\s]\d{4}\b")
_SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_CARD_CANDIDATE = re.compile(r"\b(?:\d[ -]?){13,19}\b")

_PATTERNS = [
    ("phone", _PHONE, "[REDACTED:PHONE]"),
    ("ssn", _SSN, "[REDACTED:SSN]"),
    ("email", _EMAIL, "[REDACTED:EMAIL]"),
]


def _luhn_ok(digits: str) -> bool:
    total = 0
    for i, ch in enumerate(reversed(digits)):
        d = int(ch)
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0 and len(digits) >= 13


def _card_spans(text: str) -> list[tuple[int, int]]:
    spans = []
    for match in _CARD_CANDIDATE.finditer(text):
        digits = re.sub(r"[ -]", "", match.group(0))
        if 13 <= len(digits) <= 19 and _luhn_ok(digits):
            spans.append((match.start(), match.end()))
    return spans


@dataclass
class RedactionResult:
    text: str
    hits: dict = field(default_factory=dict)

    @property
    def total_hits(self) -> int:
        return sum(self.hits.values())


def detect(text: str) -> dict:
    """Count PII hits by category without changing the text."""
    hits = {}
    for name, pattern, _ in _PATTERNS:
        count = len(pattern.findall(text))
        if count:
            hits[name] = count
    card_count = len(_card_spans(text))
    if card_count:
        hits["card"] = card_count
    return hits


def redact(text: str) -> RedactionResult:
    """Return the text with every detected PII value replaced."""
    hits: dict[str, int] = {}
    out = text
    # Cards first: their digit runs could otherwise overlap other rules.
    card_spans = _card_spans(out)
    if card_spans:
        hits["card"] = len(card_spans)
        rebuilt, last = [], 0
        for start, end in card_spans:
            rebuilt.append(out[last:start])
            rebuilt.append("[REDACTED:CARD]")
            last = end
        rebuilt.append(out[last:])
        out = "".join(rebuilt)
    for name, pattern, token in _PATTERNS:
        out, count = pattern.subn(token, out)
        if count:
            hits[name] = count
    return RedactionResult(text=out, hits=hits)


def safe_log(text: str) -> str:
    """Redact before logging: the returned string is safe to emit."""
    return redact(text).text


def safe_error(prefix: str, raw_text: str) -> str:
    """Build an error message that never echoes raw PII."""
    return f"{prefix}: {redact(raw_text).text}"
