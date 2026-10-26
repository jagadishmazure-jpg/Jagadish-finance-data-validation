# Distilled notes: patterns behind this repo

Written in the author's own words from a finance AI program brochure
that is held privately and not committed here. No sentences are copied
from that source, and no affiliation with any institution is claimed.
An 8-word overlap check against the extracted source text returns 0
hits (see `scripts/overlap_check.py`).

## 1. A score is not a decision

When a system reads many earnings calls or filings and turns tone into
a number, the useful question is not what the number is but whether it
is steady enough to act on. A sentiment figure that swings with wording
choices, or that no one can explain, should trigger a pause, not a
trade or a credit call. This repo generalises that caution: every
number must survive consistency checks before it is used at all.

## 2. Made-up figures need a checklist, not a hunch

A value that looks plausible can still be invented. The practical
defence is a short, mechanical list applied to every record: is the
value inside a sane band, does it agree with the other fields it
should agree with, is there a source note attached, do the parts add
up to the stated whole, and is the record fresh enough to matter?
This repo implements exactly that list, and a single miss blocks the
record.

## 3. Personal data rides along with financial data

Names, contact details, and account identifiers routinely appear in
the same documents as the figures. Scrubbing them is a precondition
for using the document, not a clean-up step afterwards: redact before
storage notes, before logs, before error messages, and before anything
leaves the validation layer. The checklist here covers phone numbers,
government ID numbers, card numbers, and email addresses — the last
two are easy to forget and are therefore tested explicitly.

## 4. Errors compound across chained steps

When several prompted steps run in sequence — pull a record, check it
against a policy, summarise it — a small mistake in step one does not
stay small; later steps build on it as if it were fact. The defence
is to validate at each handoff, not only at the end. This repo's
blocking validation and per-dataset report are the handoff check for
the first step in such a chain.

## 5. Explainability is an audit property

In regulated work, "the system said so" is not an explanation. Each
decision in this repo leaves a trace: the extraction reasoning steps,
the named check that failed, the redaction hit counts, the gate
decision and the named approver. A reviewer can reconstruct why a
value was released — or why it was blocked — without re-running
anything.

## What this repo does NOT take from the source

No curriculum structure, course titles, faculty names, program claims,
or institutional material is reproduced here. Only the five working
patterns above, restated in original wording, informed the design.
