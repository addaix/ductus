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

PORTED = ("resonate-overuse", "participial-padding", "growth-metaphor", "bare-reach")


def _ids(text):
    return {m.rule_id for m in iter_tell_matches(text)}


def test_ported_rules_are_advice_tier_and_floor_weight():
    rules = {r.id: r for r in load_rules()}
    for rid in PORTED:
        assert rules[rid].tier == "W"
        assert rules[rid].weight == 0.15


@pytest.mark.parametrize(
    "text,rule",
    [
        ("The message resonates deeply with younger readers.", "resonate-overuse"),
        ("The festival returned, fostering a sense of community.", "participial-padding"),
        ("The program has been cementing its position as the leader.", "participial-padding"),
        ("The field is still in its infancy.", "growth-metaphor"),
        ("They closed a seed round in March.", "growth-metaphor"),
        ("Only referenced records reach the store.", "bare-reach"),
        ("An orphan never reaches an extractor.", "bare-reach"),
    ],
)
def test_ported_rule_fires_on_its_figure(text, rule):
    assert rule in _ids(text)


@pytest.mark.parametrize(
    "text",
    [
        "The child reaches the top shelf.",  # a person reaching: an upstream exception
        "The counter reaches zero and the loop stops.",  # measurement, not metaphor
        "The ship reached the harbour at dawn.",  # a vehicle
        "The resonance of the cavity was measured at 440 Hz.",  # the noun stays clean
        "We used a random seed of 42.",  # the seed outside the startup phrase
        "That is a viable option.",  # viable outside "minimum viable"
    ],
)
def test_ported_rules_refuse_the_literal_sense(text):
    assert not _ids(text) & set(PORTED), text


def test_ing_trailer_phrases_are_not_counted_twice():
    """`ing-trailer` already reads ", highlighting the importance ..."."""
    ids = [m.rule_id for m in iter_tell_matches("We met, highlighting the importance of it.")]
    assert "participial-padding" not in ids


def test_the_upstream_licence_ships_with_the_catalogue():
    text = (files("ductus") / "data" / "LICENSE-vale-ai-tells").read_text()
    assert "MIT License" in text and "Tony Burns" in text
