from urllib.parse import urlsplit

from django import template

from apps.core.brand import compute_monogram
from apps.core.brand import nav_needs_monogram as _brand_nav_needs_monogram

register = template.Library()

# ---------------------------------------------------------------------------
# Navbar monogram — spec v3 (logic lives in apps.core.brand)
# ---------------------------------------------------------------------------


@register.filter
def nav_monogram(site_name: str | None) -> str:
    """Template filter: return the computed monogram for *site_name*."""
    return compute_monogram(site_name or "")


@register.filter
def nav_needs_monogram(site_name: str | None) -> bool:
    """Return True when site_name fails the safe-text test.

    Both conditions must pass for full text to render:
      - character count at or below NAV_TEXT_MAX_CHARS, AND
      - word count at or below NAV_TEXT_MAX_WORDS
    If either fails the monogram path is triggered.
    """
    return _brand_nav_needs_monogram(site_name or "")


@register.filter
def first_paragraph(text: str | None) -> str:
    """Return the first double-newline-separated paragraph of a text block.

    Used on the homepage to show only the opening paragraph of the About-page
    approach text without wrapping the whole multi-paragraph field in a blockquote.
    """
    if not text:
        return ""
    return text.split("\n\n")[0].strip()


@register.simple_tag
def absolute_url(request, value: str | None) -> str:
    """Return *value* as an absolute URL for the current request.

    Absolute URLs are returned unchanged. Relative URLs are resolved against the
    request host using Django's build_absolute_uri(path) behavior.
    """
    if not value:
        return ""
    parsed = urlsplit(value)
    if parsed.scheme and parsed.netloc:
        return value
    return request.build_absolute_uri(value)
