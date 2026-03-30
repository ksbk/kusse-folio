"""Tests for custom template filters in core/templatetags/core_tags.py."""

import pytest

from apps.core.templatetags.core_tags import (
    NAV_TEXT_MAX_CHARS,
    _compute_monogram,
    first_paragraph,
    nav_needs_monogram,
)


# ---------------------------------------------------------------------------
# first_paragraph filter (existing tests)
# ---------------------------------------------------------------------------

def test_first_paragraph_single_block():
    text = "This is the first paragraph."
    assert first_paragraph(text) == "This is the first paragraph."


def test_first_paragraph_two_blocks():
    text = "First paragraph.\n\nSecond paragraph."
    assert first_paragraph(text) == "First paragraph."


def test_first_paragraph_strips_whitespace():
    text = "  First paragraph.  \n\nSecond paragraph."
    assert first_paragraph(text) == "First paragraph."


def test_first_paragraph_empty_string():
    assert first_paragraph("") == ""


def test_first_paragraph_none():
    assert first_paragraph(None) == ""


def test_first_paragraph_only_whitespace():
    assert first_paragraph("   ") == ""


# ---------------------------------------------------------------------------
# nav_needs_monogram filter
# ---------------------------------------------------------------------------

def test_nav_needs_monogram_short_name():
    # 12 chars, 2 words — both within thresholds → full text
    assert nav_needs_monogram("Atelier Nord") is False


def test_nav_needs_monogram_single_word():
    assert nav_needs_monogram("Strand") is False  # 6 chars, 1 word


def test_nav_needs_monogram_char_threshold_exceeded():
    # 19 chars, 2 words — char count alone fails the test
    assert nav_needs_monogram("Strand Architecture") is True


def test_nav_needs_monogram_word_count_exceeded():
    # 3 words triggers monogram even if char count would otherwise pass
    assert nav_needs_monogram("Studio of Form") is True  # 14 chars, 3 words


def test_nav_needs_monogram_at_threshold():
    name = "A" * NAV_TEXT_MAX_CHARS
    assert nav_needs_monogram(name) is False


def test_nav_needs_monogram_above_threshold():
    name = "A" * (NAV_TEXT_MAX_CHARS + 1)
    assert nav_needs_monogram(name) is True


def test_nav_needs_monogram_empty():
    assert nav_needs_monogram("") is False


def test_nav_needs_monogram_none():
    assert nav_needs_monogram(None) is False


# ---------------------------------------------------------------------------
# _compute_monogram — standard cases
# ---------------------------------------------------------------------------

def test_monogram_two_founder_names():
    # "Beaumont Whitfield" → stop-list filtered: none; descriptor filtered: none → BW
    assert _compute_monogram("Beaumont Whitfield Architects") == "BW"


def test_monogram_three_founders():
    assert _compute_monogram("Beaumont Whitfield Kellerman Architects") == "BWK"


def test_monogram_four_plus_tokens_first_second_last():
    # Beaumont Whitfield Kellerman Adeyemi Architects → BWKA after descriptor strip
    # 4 tokens → first(B) + second(W) + last(A)
    assert _compute_monogram("Beaumont Whitfield Kellerman Adeyemi Architects") == "BWA"


def test_monogram_one_meaningful_token():
    # Hopkins Architects → strip "Architects" → ["Hopkins"] → "H"
    assert _compute_monogram("Hopkins Architects") == "H"


def test_monogram_strips_stop_words():
    # "Foster and Partners" → strip "and", "Partners" → ["Foster"] → "F"
    assert _compute_monogram("Foster and Partners") == "F"


def test_monogram_strips_ampersand():
    # "Skidmore, Owings & Merrill" — '&' is stop word; no split on comma so
    # "Skidmore," is one token (comma stays). Initials: S, O, M → SOM
    # Note: comma is not a token boundary in the spec; this tests real behaviour.
    result = _compute_monogram("Skidmore Owings & Merrill")
    assert result == "SOM"


def test_monogram_strips_plus():
    # "Foster + Partners" — '+' is both a token boundary and stop word
    # tokens after split: ["Foster", "Partners"] → strip "Partners" → ["Foster"] → "F"
    assert _compute_monogram("Foster + Partners") == "F"


def test_monogram_hyphen_single_initial_only():
    # Hyphen is NOT a token boundary; "Zaha-Hadid" is one token → initial "Z"
    assert _compute_monogram("Zaha-Hadid Architects") == "Z"


def test_monogram_preserves_particle():
    # "De Graaf Architects" — "De" is NOT in stop list (conservative policy)
    assert _compute_monogram("De Graaf Architects") == "DG"


def test_monogram_short_acronym_not_triggered():
    # "OMA" is ≤ 24 chars; monogram path would yield "O" but the template
    # never calls compute_monogram — this test verifies the function itself
    # returns "O" even if called directly (full text path prevents it in template).
    assert _compute_monogram("OMA") == "O"


def test_monogram_empty_string():
    assert _compute_monogram("") == ""


def test_monogram_none_equivalent():
    assert _compute_monogram("") == ""


def test_monogram_all_filtered():
    # If every token is filtered the first char of the original name is used
    result = _compute_monogram("Architecture Studio")
    assert result == "A"  # all tokens filtered → first char of original


def test_monogram_normalises_whitespace():
    assert _compute_monogram("  Strand   Architecture  ") == "S"


def test_monogram_uppercase():
    result = _compute_monogram("strand architecture")
    assert result == result.upper()
