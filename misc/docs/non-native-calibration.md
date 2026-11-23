# Bringing non-native false accusations to 3% (addaix/ductus#30)

After [`reducing-false-accusations.md`](reducing-false-accusations.md) the shipped defaults still call **10% of intermediate and advanced non-native human documents** `leans-machine` (bands B and C, sentence granularity), against 2% for native writers. This document fixes the procedure, the knobs and the criterion **before any number they decide is computed**, the same discipline as [`document-verdict-decision.md`](document-verdict-decision.md). The results are appended below the line, unedited, including if they fail.

## What may move

Only **document-level** thresholds, which [`what-calibration-means-here.md`](what-calibration-means-here.md) lists as legitimate to fit ("where the label thresholds sit ... should be made against measured rates rather than taste"):

- `SEGMENT_RATE_FULL`, the fraction of a document's segments with directional evidence at which the roll-up's rate view calls `strength` full. Grid: **0.35** (current), 0.50, 0.70, 1.00.
- A new `DOCUMENT_STRENGTH_FLOOR`, the strength below which the *document* claims no label. Today the document reuses the segment floor, `STRENGTH_FLOOR` = 0.20. Grid: **0.20** (current), 0.30, 0.40, 0.50, 0.60, 0.80.

Both act in `score.roll_up` only. **Segment verdicts do not change by construction**, so the correctly-flagged machine segments of both mixed fixtures (Gate 1's second condition) cannot move; the measurement checks it anyway. `lean` is untouched and still reaches ±1.0 off a single signal. Nothing here produces a per-document probability: the output is the same `(lean, strength, label)` with stricter thresholds.

Out of bounds for this pass: rule weights, rule patterns, tiers, segment thresholds. Those change segment output and need their own gates.

## Data

- **Calibration**: a seeded half (seed 30, per band) of the W&I **train** split, bands A, B, C: about 1,500 non-native human documents that no earlier decision in this package was measured on.
- **Held out**: the other half of train (about 1,500), and, reported separately for continuity with earlier numbers, the 350 **dev** documents (A, B, C and the native control N). LOCNESS has no train split, so native writers appear only in dev.
- **Recall**: two machine-written sets.
  1. The machine spans of the two vendored fixtures (LLMTrace and RoFT), each span of at least 300 characters taken as a standalone document.
  2. 100 synthetic essays (`misc/generate_machine_essays.py`): 25 learner-exam prompts of the genres W&I answers, written by two models (Claude Haiku and Sonnet), each in its own register and imitating an intermediate learner. Kept under `~/.local/share/ductus/corpora/`, like the human corpus.

## Selection rule

Among the 24 configurations, keep those whose **calibration** false-accusation rate is at most **2.5%** in each of bands A, B and C, at both granularities (paragraph, the default, and sentence). The margin below 3% is there because a held-out rate wanders from a calibration rate. Among those, pick the one that flags the most machine documents in the recall sets, both granularities summed. Ties go to the configuration nearest today's (lowest `DOCUMENT_STRENGTH_FLOOR`, then lowest `SEGMENT_RATE_FULL`).

If no configuration qualifies, nothing ships, and that is recorded as the result: it would mean document-level thresholds alone cannot separate these writers from machine text, which is the branch [`document-verdict-decision.md`](document-verdict-decision.md) holds in reserve.

## Done means

On the **held-out** train half, the pooled non-native rate (A, B and C together) is at most **3%** at both granularities, with each band reported, and document recall on both machine sets is reported next to it, before and after. The dev numbers are reported too; they are not the criterion, because earlier rule decisions were made on them.

---

## Results

The procedure above was committed and pushed first (commit `92b1544`); this is the output of `python misc/measure_document_threshold.py` on that procedure, pasted unedited. Corpus: 1,500 calibration and 1,500 held-out non-native train essays (seed 30), the 350 dev documents, 12 fixture machine spans of 300 characters or more, and 100 synthetic machine essays (50 by Claude Haiku, 50 by Claude Sonnet, generated 2026-11-23).

### Calibration grid (non-native train, calibration half)

| SEGMENT_RATE_FULL | DOCUMENT_STRENGTH_FLOOR | A para | B para | C para | A sent | B sent | C sent | machine docs flagged | qualifies |
|---|---|---|---|---|---|---|---|---|---|
| 0.35 | 0.2 | 4.9% | 8.8% | 8.6% | 3.7% | 10.6% | 10.6% | 35 |  |
| 0.35 | 0.3 | 2.0% | 5.0% | 5.1% | 2.6% | 4.2% | 4.0% | 19 |  |
| 0.35 | 0.4 | 0.8% | 3.0% | 3.4% | 0.6% | 1.4% | 2.0% | 7 |  |
| 0.35 | 0.5 | 0.5% | 2.0% | 2.3% | 0.5% | 1.2% | 1.7% | 2 | yes |
| 0.35 | 0.6 | 0.2% | 1.0% | 1.1% | 0.0% | 0.6% | 0.6% | 0 | yes |
| 0.35 | 0.8 | 0.0% | 0.6% | 0.3% | 0.0% | 0.0% | 0.0% | 0 | yes |
| 0.5 | 0.2 | 4.9% | 8.6% | 8.6% | 3.1% | 5.2% | 6.6% | 34 |  |
| 0.5 | 0.3 | 2.0% | 5.0% | 4.6% | 1.5% | 2.2% | 1.7% | 13 |  |
| 0.5 | 0.4 | 0.8% | 3.0% | 2.9% | 0.5% | 1.0% | 1.1% | 6 |  |
| 0.5 | 0.5 | 0.5% | 2.0% | 2.3% | 0.2% | 0.4% | 0.6% | 1 | yes |
| 0.5 | 0.6 | 0.2% | 1.0% | 1.1% | 0.0% | 0.0% | 0.0% | 0 | yes |
| 0.5 | 0.8 | 0.0% | 0.6% | 0.3% | 0.0% | 0.0% | 0.0% | 0 | yes |
| 0.7 | 0.2 | 4.9% | 8.4% | 8.3% | 2.0% | 2.4% | 2.3% | 23 |  |
| 0.7 | 0.3 | 2.0% | 4.8% | 4.0% | 0.6% | 1.2% | 0.9% | 10 |  |
| 0.7 | 0.4 | 0.8% | 2.8% | 2.6% | 0.2% | 0.0% | 0.0% | 6 |  |
| 0.7 | 0.5 | 0.3% | 1.8% | 2.3% | 0.2% | 0.0% | 0.0% | 0 | yes |
| 0.7 | 0.6 | 0.0% | 1.0% | 1.1% | 0.0% | 0.0% | 0.0% | 0 | yes |
| 0.7 | 0.8 | 0.0% | 0.4% | 0.3% | 0.0% | 0.0% | 0.0% | 0 | yes |
| 1.0 | 0.2 | 4.8% | 8.0% | 7.4% | 1.2% | 1.6% | 1.1% | 17 |  |
| 1.0 | 0.3 | 2.0% | 4.6% | 4.0% | 0.3% | 0.2% | 0.0% | 10 |  |
| 1.0 | 0.4 | 0.6% | 2.8% | 2.6% | 0.2% | 0.0% | 0.0% | 1 |  |
| 1.0 | 0.5 | 0.3% | 1.8% | 2.3% | 0.2% | 0.0% | 0.0% | 0 | yes |
| 1.0 | 0.6 | 0.0% | 0.8% | 1.1% | 0.0% | 0.0% | 0.0% | 0 | yes |
| 1.0 | 0.8 | 0.0% | 0.4% | 0.0% | 0.0% | 0.0% | 0.0% | 0 | yes |

**Chosen**: SEGMENT_RATE_FULL = 0.35, DOCUMENT_STRENGTH_FLOOR = 0.5

### Held out, dev and recall: today vs chosen

| set | granularity | today | chosen |
|---|---|---|---|
| held-out A | paragraph | 35/650 (5.4%) | 2/650 (0.3%) |
| held-out A | sentence | 13/650 (2.0%) | 2/650 (0.3%) |
| held-out B | paragraph | 33/500 (6.6%) | 7/500 (1.4%) |
| held-out B | sentence | 39/500 (7.8%) | 4/500 (0.8%) |
| held-out C | paragraph | 30/350 (8.6%) | 5/350 (1.4%) |
| held-out C | sentence | 41/350 (11.7%) | 6/350 (1.7%) |
| held-out A+B+C | paragraph | **98/1500 (6.5%)** | **14/1500 (0.9%)** |
| held-out A+B+C | sentence | **93/1500 (6.2%)** | **12/1500 (0.8%)** |
| dev A | paragraph | 4/130 (3.1%) | 0/130 (0.0%) |
| dev A | sentence | 3/130 (2.3%) | 1/130 (0.8%) |
| dev B | paragraph | 9/100 (9.0%) | 2/100 (2.0%) |
| dev B | sentence | 10/100 (10.0%) | 1/100 (1.0%) |
| dev C | paragraph | 5/70 (7.1%) | 1/70 (1.4%) |
| dev C | sentence | 7/70 (10.0%) | 1/70 (1.4%) |
| dev N | paragraph | 4/50 (8.0%) | 0/50 (0.0%) |
| dev N | sentence | 1/50 (2.0%) | 0/50 (0.0%) |
| machine llmtrace | paragraph | 1/2 (50.0%) | 0/2 (0.0%) |
| machine llmtrace | sentence | 1/2 (50.0%) | 0/2 (0.0%) |
| machine roft | paragraph | 1/10 (10.0%) | 0/10 (0.0%) |
| machine roft | sentence | 0/10 (0.0%) | 0/10 (0.0%) |
| machine synthetic | paragraph | 25/100 (25.0%) | 2/100 (2.0%) |
| machine synthetic | sentence | 7/100 (7.0%) | 0/100 (0.0%) |

Fixture machine segments flagged (sentence; unchanged by construction): {'llmtrace': 2, 'roft': 0}

## Reading it

**The criterion is met, and the selection rule picked `DOCUMENT_STRENGTH_FLOOR` = 0.50 with `SEGMENT_RATE_FULL` unchanged.** On the held-out half the pooled non-native rate falls from 6.5% to 0.9% at paragraph granularity (the default) and from 6.2% to 0.8% at sentence granularity; every band is at or under 1.7%. The dev set, which earlier decisions were made on, moves the same way: 3 of 350 at either granularity, against 22 and 21 before. The native control goes to zero.

**The price is recall, and it is most of it.** The document verdict called 25 of the 100 synthetic machine essays `leans-machine` at paragraph granularity, and now calls 2; at sentence granularity 7 became 0. On the fixture spans 2 of 12 became 0. Before the change the document label fired on a quarter of machine essays and on 6 to 10% of non-native human essays, a discrimination too weak to justify the harm it did. After it, the label fires on about 2% of machine essays and 1% of human ones. It is not better evidence now, only rarer.

**Nothing at segment level moved**, by construction and confirmed: the fixtures' correctly-flagged machine segments are 2 (LLMTrace) and 0 (RoFT) before and after, so Gate 1's second condition holds. The flagged sentences, with their quoted spans, carry the same evidence they did.

So the shipped trade is the one this package's asymmetry asks for: silence over a false accusation. But the numbers also say something the procedure did not ask: **no document threshold in this grid separates machine essays from fluent non-native human essays.** Every configuration that flags more than a handful of machine essays also flags more than 2.5% of some non-native band. That is the branch [`document-verdict-decision.md`](document-verdict-decision.md) holds in reserve, that a document-level verdict may not be supportable from evidence of this kind. Whether to stop emitting one is a separate decision for the package's owner; the measurement here is one input to it.

What follows for the surfaces: a document label is now rare in both directions, so "no-evidence" on a document is an even weaker result than it was. The renderers, the MCP and HTTP descriptions and the skills say so next to the rate.
