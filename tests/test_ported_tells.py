"""Rules ported from tbhb/vale-ai-tells (addaix/ductus#26).

Each fired on machine-written spans and on at most two of the 350 human essays of
``misc/measure_false_positives.py``, and adding them left every band's
false-accusation rate unchanged. These tests pin what each rule is *for* and the
literal senses upstream deliberately refuses, so a later edit to a pattern cannot
quietly widen it into ordinary human prose.
"""

from importlib.resources import files

import pytest

from ductus.tells import iter_tell_matches, load_rules

PORTED = ("resonate-overuse", "participial-padding", "growth-metaphor")
TIERS = {"resonate-overuse": "W", "participial-padding": "W", "growth-metaphor": "S"}


def _ids(text):
    return {m.rule_id for m in iter_tell_matches(text)}


def test_ported_rules_carry_their_tier_and_the_floor_weight():
    rules = {r.id: r for r in load_rules()}
    for rid in PORTED:
        assert rules[rid].tier == TIERS[rid]
        assert rules[rid].weight == 0.15


@pytest.mark.parametrize(
    "text,rule",
    [
        ("The message resonates deeply with younger readers.", "resonate-overuse"),
        ("The festival returned, fostering a sense of community.", "participial-padding"),
        (
            "The program has been cementing its position as the leader.",
            "participial-padding",
        ),
        ("The field is still in its infancy.", "growth-metaphor"),
        ("They closed a seed round in March.", "growth-metaphor"),
    ],
)
def test_ported_rule_fires_on_its_figure(text, rule):
    assert rule in _ids(text)


@pytest.mark.parametrize(
    "text",
    [
        "The resonance of the cavity was measured at 440 Hz.",  # the noun stays clean
        "We used a random seed of 42.",  # the seed outside the startup phrase
        "That is a viable option.",  # viable outside "minimum viable"
    ],
)
def test_ported_rules_refuse_the_literal_sense(text):
    assert not _ids(text) & set(PORTED), text


def test_ing_trailer_phrases_are_not_counted_twice():
    """`ing-trailer` already reads ", highlighting the importance ..."."""
    ids = [
        m.rule_id for m in iter_tell_matches("We met, highlighting the importance of it.")
    ]
    assert "participial-padding" not in ids


def test_the_upstream_licence_ships_with_the_catalogue():
    text = (files("ductus") / "data" / "LICENSE-vale-ai-tells").read_text()
    assert "MIT License" in text and "Tony Burns" in text


@pytest.mark.parametrize(
    "text",
    [
        "Cultivating a sense of belonging matters.",  # growth-metaphor reads it
        "We are ensuring a seamless handover.",  # ai-vocabulary reads it
        "It closed, marking a pivotal moment.",  # ai-vocabulary reads it
    ],
)
def test_one_phrase_is_one_signal(text):
    """A ported rule never re-counts a phrase another rule already reads."""
    matches = list(iter_tell_matches(text))
    spans = [(m.start, m.end) for m in matches]
    overlapping = [
        (a, b)
        for i, a in enumerate(spans)
        for b in spans[i + 1 :]
        if a[0] < b[1] and b[0] < a[1]
    ]
    assert not overlapping, [m.rule_id for m in matches]


@pytest.mark.parametrize(
    "blob", ["x" * 50_000, "x-" * 25_000, "word " * 10_000], ids=["run", "hyphens", "words"]
)
def test_the_whole_catalogue_stays_linear_on_pathological_input(blob):
    """A base64 blob or minified JS must not stall a scan (a surface takes any text).

    ``triad`` used to take about 48 s on the hyphenated blob (#28).
    """
    import time

    t0 = time.perf_counter()
    list(iter_tell_matches(blob))
    assert time.perf_counter() - t0 < 2.0
