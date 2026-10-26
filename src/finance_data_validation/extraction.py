"""Structured extraction from synthetic financial text.

Deterministic, standard-library only, no live model required. The module
implements two prompting *patterns* as data, not as calls to a model:

* few-shot prompting: a small set of worked input/output pairs is placed
  in front of the target text so the expected output shape is unambiguous;
* chain-of-thought reasoning templates: a fixed, ordered list of reasoning
  steps (find the labels, read the figures, recompute the arithmetic, note
  what is missing) that an extractor must walk before emitting a value.

``extract_fields`` is the deterministic stand-in for the model step: it
applies the same label/figure rules the prompt describes, so the prompt,
the reasoning trace, and the extracted values can be checked against each
other in tests without any network access.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# Label -> canonical field name, in the order they are searched.
_LABELS = [
    (r"net\s+income", "net_income"),
    (r"total\s+revenue", "revenue"),
    (r"\brevenue\b", "revenue"),
    (r"total\s+expenses", "expenses"),
    (r"\bexpenses\b", "expenses"),
    (r"total\s+assets", "total_assets"),
    (r"total\s+liabilities", "total_liabilities"),
]

_MONEY = re.compile(r"\$?\s*([0-9][0-9,]*(?:\.[0-9]{2})?)")
_PERIOD = re.compile(r"\b(20\d{2}-[Qq][1-4])\b|\b(20\d{2}-\d{2}-\d{2})\b")
_SOURCE = re.compile(r"[Ss]ource\s*:\s*([^\n.;]+)")

# Worked examples: synthetic figures only. Each pair shows the input text
# and the exact field dict the extractor must produce for it.
FEW_SHOT_EXAMPLES = [
    {
        "text": "Revenue was $500,000 and expenses were $320,000, "
        "net income $180,000. Source: Q3 ledger note 2026-07.",
        "fields": {"revenue": 500000.0, "expenses": 320000.0,
                   "net_income": 180000.0},
    },
    {
        "text": "Total assets $2,400,000; total liabilities $900,000. "
        "Source: balance sheet draft 2026-06.",
        "fields": {"total_assets": 2400000.0, "total_liabilities": 900000.0},
    },
    {
        "text": "Revenue $120,000, expenses $150,000, net income -$30,000. "
        "Source: monthly close note 2026-08.",
        "fields": {"revenue": 120000.0, "expenses": 150000.0,
                   "net_income": -30000.0},
    },
]

COT_STEPS = [
    "1. List every labelled figure in the text before using any of them.",
    "2. Match each figure to exactly one field; never reuse a figure.",
    "3. Recompute any total from its parts and compare it with the stated total.",
    "4. Record the source citation, or record that none is present.",
    "5. Emit only fields found in the text; never invent a missing field.",
]


def chain_of_thought_template() -> list[str]:
    """Return the fixed reasoning-step template (a copy)."""
    return list(COT_STEPS)


def build_few_shot_prompt(text: str, examples=None) -> str:
    """Build a few-shot prompt: worked examples, then the target text."""
    examples = FEW_SHOT_EXAMPLES if examples is None else examples
    parts = [
        "Extract the financial fields below as field: value pairs. "
        "Use only figures present in the text.",
    ]
    for i, ex in enumerate(examples, 1):
        parts.append(f"Example {i} input: {ex['text']}")
        rendered = ", ".join(f"{k}={v:g}" for k, v in ex["fields"].items())
        parts.append(f"Example {i} output: {rendered}")
    parts.append("Reasoning steps:")
    parts.extend(COT_STEPS)
    parts.append(f"Target input: {text}")
    parts.append("Target output:")
    return "\n".join(parts)


@dataclass
class ExtractionResult:
    fields: dict
    period: str | None = None
    source_citation: str | None = None
    reasoning: list = field(default_factory=list)


def extract_fields(text: str) -> ExtractionResult:
    """Deterministically extract labelled financial figures from text.

    Only figures that follow a recognised label are extracted, and a
    figure already claimed by one field is never reused for another.
    Negative amounts written as ``-$30,000`` or ``- $30,000`` are kept.
    """
    fields: dict[str, float] = {}
    reasoning: list[str] = []
    used_spans: list[tuple[int, int]] = []

    for pattern, name in _LABELS:
        if name in fields:
            continue
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            tail = text[match.end(): match.end() + 40]
            # Prefer a dollar-prefixed amount: a bare year or note number
            # sitting between the label and the amount must not win.
            dollar = re.search(r"\$\s*(-?[0-9][0-9,]*(?:\.[0-9]{2})?)", tail)
            money = dollar if dollar else _MONEY.search(tail)
            if money is None:
                continue
            span = (match.start(), match.end())
            if any(s <= span[0] < e or s < span[1] <= e
                   for s, e in used_spans):
                continue
            raw = money.group(1).replace(",", "")
            value = float(raw)
            # A minus sign immediately before the amount makes it negative.
            # (money.start() is relative to `tail`, so slice `tail`, not
            # the full text -- an earlier version sliced the wrong string.)
            prefix = tail[max(0, money.start() - 3):money.start()]
            if "-" in prefix:
                value = -abs(value)
            fields[name] = value
            used_spans.append(span)
            reasoning.append(f"Matched label '{match.group(0)}' -> "
                             f"{name}={value:g}.")
            break

    period = None
    period_match = _PERIOD.search(text)
    if period_match:
        period = period_match.group(0)
        reasoning.append(f"Period found: {period}.")
    source = None
    source_match = _SOURCE.search(text)
    if source_match:
        source = source_match.group(1).strip()
        reasoning.append(f"Source citation found: {source}.")
    else:
        reasoning.append("No source citation present.")
    reasoning.append("Emitted only fields found in the text.")
    return ExtractionResult(fields=fields, period=period,
                            source_citation=source, reasoning=reasoning)
