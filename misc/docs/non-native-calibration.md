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

(Appended by `python misc/measure_document_threshold.py` after the procedure above was committed.)
