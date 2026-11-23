"""Choose the document-level thresholds by the rule pre-registered in #30.

The procedure, the grid and the criterion are in ``misc/docs/non-native-calibration.md``
and were committed before this script was first run. In short: segment every document
once, then re-run only :func:`ductus.score.roll_up` under each ``(SEGMENT_RATE_FULL,
DOCUMENT_STRENGTH_FLOOR)`` pair; keep the pairs whose false-accusation rate on the
calibration half of W&I train is at most 2.5% in every non-native band at both
granularities; among them take the one that flags the most machine documents; then
report the held-out half, the dev set and the recall sets::

    python misc/measure_document_threshold.py            # prints markdown tables
    python misc/measure_document_threshold.py --jobs 6

Segment verdicts do not depend on either threshold, so the fixtures' correctly-flagged
machine *segments* are printed once, as the check that nothing moved.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from concurrent.futures import ProcessPoolExecutor
from itertools import product
from pathlib import Path

from ductus import gauge, score

sys.path.insert(0, str(Path(__file__).parent))  # the sibling measurement script
from measure_false_positives import fetch_corpus, load_band

RATE_GRID = (0.35, 0.50, 0.70, 1.00)
FLOOR_GRID = (0.20, 0.30, 0.40, 0.50, 0.60, 0.80)
GRANULARITIES = ("paragraph", "sentence")
CALIBRATION_MAX = 0.025
SEED = 30
MIN_SPAN_CHARS = 300

FIXTURES = Path(__file__).parent.parent / "tests" / "fixtures"
SYNTHETIC = (
    Path.home()
    / ".local"
    / "share"
    / "ductus"
    / "corpora"
    / "synthetic-machine"
    / "essays.jsonl"
)


def _segments(text: str) -> dict:
    """Both granularities' segments for one text (the expensive, threshold-free part)."""
    return {g: gauge(text, segmenter=g).segments for g in GRANULARITIES}


def _label(segments, n_chars: int, rate: float, floor: float) -> str:
    score.SEGMENT_RATE_FULL, score.DOCUMENT_STRENGTH_FLOOR = rate, floor
    return score.roll_up(segments, n_chars=n_chars)[2]


def _split(texts: list[str]) -> tuple[list[str], list[str]]:
    order = list(range(len(texts)))
    random.Random(SEED).shuffle(order)
    half = len(order) // 2
    return [texts[i] for i in order[:half]], [texts[i] for i in order[half:]]


def _fixture_machine_docs() -> dict[str, list[str]]:
    out = {}
    for name, file in (
        ("llmtrace", "mixed_authorship.json"),
        ("roft", "roft_boundary.json"),
    ):
        docs = json.loads((FIXTURES / file).read_text(encoding="utf-8"))["documents"]
        out[name] = [
            d["text"][a:b]
            for d in docs
            for a, b in d["ai_char_intervals"]
            if b - a >= MIN_SPAN_CHARS
        ]
    return out


def _fixture_segment_hits() -> dict[str, int]:
    """Correctly-flagged machine segments, sentence granularity, as Gate 1 counts them."""
    hits = {}
    for name, file in (
        ("llmtrace", "mixed_authorship.json"),
        ("roft", "roft_boundary.json"),
    ):
        docs = json.loads((FIXTURES / file).read_text(encoding="utf-8"))["documents"]
        found = 0
        for d in docs:
            for seg in gauge(d["text"], segmenter="sentence").segments:
                covered = sum(
                    max(0, min(seg.span.end, b) - max(seg.span.start, a))
                    for a, b in d["ai_char_intervals"]
                )
                found += (
                    seg.label == "leans-machine"
                    and covered / max(1, seg.span.length) >= 0.8
                )
        hits[name] = found
    return hits


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--jobs", type=int, default=6)
    args = parser.parse_args()

    root = fetch_corpus()
    calibration, held_out, dev = {}, {}, {}
    for band in "ABC":
        calibration[band], held_out[band] = _split(load_band(root, f"{band}.train"))
    for band in "ABCN":
        dev[band] = load_band(root, f"{band}.dev")
    machine = _fixture_machine_docs()
    if SYNTHETIC.is_file():
        rows = [json.loads(line) for line in SYNTHETIC.read_text().splitlines()]
        machine["synthetic"] = [r["text"] for r in rows]

    sets = {
        "calibration": calibration,
        "held-out": held_out,
        "dev": dev,
        "machine": machine,
    }
    flat = [
        (s, g, t) for s, groups in sets.items() for g, ts in groups.items() for t in ts
    ]
    with ProcessPoolExecutor(args.jobs) as pool:
        segmented = list(pool.map(_segments, [t for _, _, t in flat], chunksize=16))

    def rates(rate, floor):
        """``{(set, group, granularity): (flagged, total)}`` under one pair."""
        out: dict = {}
        for (s, g, text), segs in zip(flat, segmented, strict=True):
            for gran in GRANULARITIES:
                flagged, total = out.get((s, g, gran), (0, 0))
                hit = _label(segs[gran], len(text), rate, floor) == "leans-machine"
                out[(s, g, gran)] = (flagged + hit, total + 1)
        return out

    original = (score.SEGMENT_RATE_FULL, score.DOCUMENT_STRENGTH_FLOOR)
    grid = {pair: rates(*pair) for pair in product(RATE_GRID, FLOOR_GRID)}
    score.SEGMENT_RATE_FULL, score.DOCUMENT_STRENGTH_FLOOR = original

    def frac(cell):
        return cell[0] / cell[1] if cell[1] else 0.0

    def qualifies(r):
        return all(
            frac(r[("calibration", b, g)]) <= CALIBRATION_MAX
            for b in "ABC"
            for g in GRANULARITIES
        )

    def found(r):
        return sum(r[("machine", m, g)][0] for m in machine for g in GRANULARITIES)

    print("## Calibration grid (non-native train, calibration half)\n")
    print(
        "| SEGMENT_RATE_FULL | DOCUMENT_STRENGTH_FLOOR | A para | B para | C para "
        "| A sent | B sent | C sent | machine docs flagged | qualifies |"
    )
    print("|---|---|---|---|---|---|---|---|---|---|")
    for (rate, floor), r in grid.items():
        cells = [
            f"{frac(r[('calibration', b, g)]):.1%}" for g in GRANULARITIES for b in "ABC"
        ]
        print(
            f"| {rate} | {floor} | {' | '.join(cells)} | {found(r)} | "
            f"{'yes' if qualifies(r) else ''} |"
        )

    current = (RATE_GRID[0], FLOOR_GRID[0])
    eligible = [p for p, r in grid.items() if qualifies(r)]
    if not eligible:
        print("\n**No configuration qualifies.** Nothing ships (see the procedure).")
        chosen = None
    else:
        chosen = max(eligible, key=lambda p: (found(grid[p]), -p[1], -p[0]))
        print(
            f"\n**Chosen**: SEGMENT_RATE_FULL = {chosen[0]}, "
            f"DOCUMENT_STRENGTH_FLOOR = {chosen[1]}"
        )

    def report(name, pairs):
        print(f"\n## {name}\n")
        print("| set | granularity | " + " | ".join(label for label, _ in pairs) + " |")
        print("|---|---|" + "---|" * len(pairs))
        for s in ("held-out", "dev", "machine"):
            for g in sets[s]:
                for gran in GRANULARITIES:
                    cells = []
                    for _, pair in pairs:
                        k, n = grid[pair][(s, g, gran)]
                        cells.append(f"{k}/{n} ({k / n:.1%})")
                    print(f"| {s} {g} | {gran} | {' | '.join(cells)} |")
            if s == "held-out":
                for gran in GRANULARITIES:
                    cells = []
                    for _, pair in pairs:
                        k = sum(grid[pair][(s, b, gran)][0] for b in "ABC")
                        n = sum(grid[pair][(s, b, gran)][1] for b in "ABC")
                        cells.append(f"**{k}/{n} ({k / n:.1%})**")
                    print(f"| held-out A+B+C | {gran} | {' | '.join(cells)} |")

    pairs = [("today", current)] + ([("chosen", chosen)] if chosen else [])
    report("Held out, dev and recall: today vs chosen", pairs)
    print(
        "\nFixture machine segments flagged (sentence; unchanged by construction): "
        f"{_fixture_segment_hits()}"
    )


if __name__ == "__main__":
    main()
