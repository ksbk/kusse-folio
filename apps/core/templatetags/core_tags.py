import re

from django import template

register = template.Library()

# ---------------------------------------------------------------------------
# Navbar monogram — spec v3
# ---------------------------------------------------------------------------

# Design-system thresholds: both conditions must pass for full text to render.
# Site names at or below these limits look obviously navbar-safe; anything
# outside them goes to the monogram path.  Named constants so a type-scale
# revision can locate and adjust them in one place.
NAV_TEXT_MAX_CHARS = 18   # e.g. "Atelier Nord" (12), "Studio Form" (11)
NAV_TEXT_MAX_WORDS = 2    # single or two-word names only

# Universal syntactic connectors — never carry identity value.
# Conservative by design; culturally specific particles are NOT included.
# Note: "+" is also listed here as defensive redundancy — the tokeniser splits
# on "+" before filtering, so this entry only catches edge-case residue.
_STOP_WORDS: frozenset[str] = frozenset({"and", "&", "of", "the", "for", "a", "an", "+"})


def _compute_monogram(site_name: str) -> str:
    """
    Derive an identity monogram from *site_name* using the v3 algorithm.

    Returns 1–3 uppercase letters.  Profession descriptors (e.g. "Architects",
    "Partners") are intentionally kept — their initials are part of the brand
    mark.  Only syntactic stop words ("and", "the", "of", …) are removed.
    Never truncates — the result is always a clean, intentional string.
    """
    if not site_name:
        return ""

    # Step 1 — normalise
    name = " ".join(site_name.split())

    # Step 2 — tokenise on spaces and + (hyphens are NOT token boundaries)
    tokens = re.split(r"[ +]+", name)

    # Step 3 — hyphens: compound tokens yield only the first component's initial
    # (handled implicitly: we take token[0] regardless of internal hyphens)

    # Step 4 — filter stop words only; profession descriptors are kept
    filtered = [
        t for t in tokens
        if t.lower() not in _STOP_WORDS
    ]

    # Step 6 — extract initials (first char of each surviving token, uppercased)
    initials = [t[0].upper() for t in filtered if t]

    # Step 7 — letter count cap
    if not initials:
        # Last-resort: take first character of the original name
        return name[0].upper()
    if len(initials) <= 3:
        return "".join(initials)
    # 4+ tokens: take the first three — simpler, more predictable
    return "".join(initials[:3])


@register.filter
def nav_monogram(site_name: str | None) -> str:
    """Template filter: return the computed monogram for *site_name*."""
    return _compute_monogram(site_name or "")


@register.filter
def nav_needs_monogram(site_name: str | None) -> bool:
    """Return True when site_name fails the safe-text test.

    Both conditions must pass for full text to render:
      - character count at or below NAV_TEXT_MAX_CHARS, AND
      - word count at or below NAV_TEXT_MAX_WORDS
    If either fails the monogram path is triggered.
    """
    name = site_name or ""
    return len(name) > NAV_TEXT_MAX_CHARS or len(name.split()) > NAV_TEXT_MAX_WORDS


@register.filter
def first_paragraph(text: str | None) -> str:
    """Return the first double-newline-separated paragraph of a text block.

    Used on the homepage to show only the opening paragraph of the About-page
    approach text without wrapping the whole multi-paragraph field in a blockquote.
    """
    if not text:
        return ""
    return text.split("\n\n")[0].strip()
