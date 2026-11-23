"""The measured false-accusation rate has one source, and the prose quotes it (#31).

The surfaces that can format their text (render, MCP, HTTP, the generated frontend
module) read :mod:`ductus.limits`. The prose that cannot (README, the skills, the package
docstring, the dev notes) is checked here: it must quote the current numbers and none of
the superseded ones, so recalibrating is one edit plus whatever this test names.
"""

from pathlib import Path

import pytest

import ductus
from ductus import limits

REPO = Path(__file__).resolve().parent.parent
SUPERSEDED = ("one in sixteen", "6.0% of 350", "20.6% of\n350")

PROSE = {
    "README.md": REPO / "README.md",
    "skill ductus": REPO / "ductus" / "data" / "skills" / "ductus" / "SKILL.md",
    "skill ductus-gauge": REPO
    / "ductus"
    / "data"
    / "skills"
    / "ductus-gauge"
    / "SKILL.md",
}


@pytest.mark.parametrize("name", PROSE)
def test_the_prose_quotes_the_current_rate(name):
    text = PROSE[name].read_text(encoding="utf-8")
    assert (
        limits.DOCUMENT_FALSE_ACCUSATION_RATE in text
        or f"in {limits.DOCUMENT_ONE_IN}" in text
    ), f"{name} does not quote the measured document rate from ductus.limits"
    assert not any(old in text for old in SUPERSEDED), f"{name} quotes a superseded rate"


def test_the_package_docstring_quotes_the_current_rate():
    assert limits.DOCUMENT_FALSE_ACCUSATION_RATE in ductus.__doc__
    assert limits.SOURCE in ductus.__doc__


def test_the_frontend_module_is_generated_from_the_constants():
    generated = REPO / "frontend" / "src" / "generated" / "limits.ts"
    assert generated.read_text(encoding="utf-8") == limits.as_typescript()
    for value in (limits.DOCUMENT_FALSE_ACCUSATION_RATE, limits.DOCUMENT_ONE_IN):
        assert f'"{value}"' in limits.as_typescript()
