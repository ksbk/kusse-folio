"""
Visual audit screenshot capture.

Usage:
    uv run python scripts/take_screenshots.py

Output:
    artifacts/visual-audit/YYYY-MM-DD/
        <page>-<WxH>.png          (core pages)
        project-detail-cover-<WxH>.png
        project-detail-no-cover-<WxH>.png
        report.md

Requires the dev server running on port 8765:
    uv run python manage.py runserver 8765 --settings=config.settings.dev
"""

from __future__ import annotations

import datetime
import io
import os
import sys
import textwrap
from pathlib import Path

# ---------------------------------------------------------------------------
# Django setup (needed for ORM access within the script)
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

import django  # noqa: E402
django.setup()

from PIL import Image as PILImage                   # noqa: E402
from django.core.files.base import ContentFile      # noqa: E402
from apps.projects.models import Project            # noqa: E402
from playwright.sync_api import sync_playwright     # noqa: E402

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BASE = "http://127.0.0.1:8765"
DATE = datetime.date.today().isoformat()
OUT  = ROOT / "artifacts" / "visual-audit" / DATE
OUT.mkdir(parents=True, exist_ok=True)

# Primary audit viewports (from the original brief)
AUDIT_VIEWPORTS = [
    ("320x568",   {"width": 320,  "height": 568}),
    ("390x844",   {"width": 390,  "height": 844}),
    ("768x1024",  {"width": 768,  "height": 1024}),
    ("1024x1366", {"width": 1024, "height": 1366}),
]

# Extra desktop viewport — clearly labelled, not part of the core audit
EXTRA_VIEWPORTS = [
    ("1440x900-extra", {"width": 1440, "height": 900}),
]

CORE_PAGES = [
    ("home",     "/"),
    ("about",    "/about/"),
    ("projects", "/projects/"),
    ("contact",  "/contact/"),
]

_PLACEHOLDER_COVER_SLUG = "house-on-the-hillside"  # project to temporarily assign cover


def _make_placeholder_cover() -> bytes:
    """Return a minimal JPEG (1200×800 warm-grey rectangle) for test purposes."""
    img = PILImage.new("RGB", (1200, 800), color=(210, 205, 198))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


def _attach_cover(slug: str) -> bool:
    """Attach a synthetic placeholder cover to the named project. Returns True if done."""
    try:
        project = Project.objects.get(slug=slug)
        if project.cover_image:
            return True  # already has one
        data = _make_placeholder_cover()
        project.cover_image.save(
            f"_audit_placeholder_{slug}.jpg",
            ContentFile(data),
            save=True,
        )
        return True
    except Project.DoesNotExist:
        return False


def _detach_cover(slug: str) -> None:
    """Remove the placeholder cover, cleaning up the file."""
    try:
        project = Project.objects.get(slug=slug)
        if project.cover_image and "_audit_placeholder_" in project.cover_image.name:
            project.cover_image.delete(save=True)
    except Project.DoesNotExist:
        pass


def _screenshot(browser, path: str, vp_label: str, vp: dict, fname: Path) -> None:
    ctx = browser.new_context(viewport=vp)
    pg = ctx.new_page()
    pg.goto(f"{BASE}{path}", wait_until="networkidle", timeout=20_000)
    # Wait an extra tick for webfonts / CSS transitions to settle
    pg.wait_for_timeout(600)
    pg.evaluate("window.scrollTo(0, 0)")
    pg.wait_for_timeout(200)
    pg.screenshot(path=str(fname), full_page=True)
    ctx.close()
    print(f"  {fname.name}")


def main() -> None:
    # -----------------------------------------------------------------------
    # Probe cover/no-cover project URLs before the browser opens
    # -----------------------------------------------------------------------
    cover_project    = Project.objects.filter(slug=_PLACEHOLDER_COVER_SLUG).first()
    no_cover_project = Project.objects.filter(cover_image="").order_by("order").first()

    cover_attached_by_script = False
    cover_url    = None
    no_cover_url = None
    cover_title    = None
    no_cover_title = None

    if cover_project:
        cover_attached_by_script = not bool(cover_project.cover_image)
        if cover_attached_by_script:
            _attach_cover(_PLACEHOLDER_COVER_SLUG)
            cover_project.refresh_from_db()
        cover_url   = cover_project.get_absolute_url()
        cover_title = cover_project.title

    if no_cover_project:
        # Make sure it's a different project from the one with cover
        if cover_project and no_cover_project.slug == cover_project.slug:
            no_cover_project = (
                Project.objects
                .filter(cover_image="")
                .exclude(slug=_PLACEHOLDER_COVER_SLUG)
                .order_by("order")
                .first()
            )
        if no_cover_project:
            no_cover_url   = no_cover_project.get_absolute_url()
            no_cover_title = no_cover_project.title

    captured: list[str] = []
    defects:  list[str] = []

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()

            # ---------------------------------------------------------------
            # Core pages at all audit viewports
            # ---------------------------------------------------------------
            for vp_label, vp in AUDIT_VIEWPORTS + EXTRA_VIEWPORTS:
                for page_label, path in CORE_PAGES:
                    fname = OUT / f"{page_label}-{vp_label}.png"
                    _screenshot(browser, path, vp_label, vp, fname)
                    captured.append(fname.name)

            # ---------------------------------------------------------------
            # Project detail — with cover
            # ---------------------------------------------------------------
            if cover_url:
                for vp_label, vp in AUDIT_VIEWPORTS:
                    fname = OUT / f"project-detail-cover-{vp_label}.png"
                    _screenshot(browser, cover_url, vp_label, vp, fname)
                    captured.append(fname.name)

            # ---------------------------------------------------------------
            # Project detail — without cover
            # ---------------------------------------------------------------
            if no_cover_url:
                for vp_label, vp in AUDIT_VIEWPORTS:
                    fname = OUT / f"project-detail-no-cover-{vp_label}.png"
                    _screenshot(browser, no_cover_url, vp_label, vp, fname)
                    captured.append(fname.name)

            browser.close()

    finally:
        # Always clean up the placeholder cover if we added it
        if cover_attached_by_script:
            _detach_cover(_PLACEHOLDER_COVER_SLUG)

    # -----------------------------------------------------------------------
    # Write report.md
    # -----------------------------------------------------------------------
    _write_report(
        captured=captured,
        defects=defects,
        cover_url=cover_url,
        cover_title=cover_title,
        cover_was_synthetic=cover_attached_by_script,
        no_cover_url=no_cover_url,
        no_cover_title=no_cover_title,
    )

    print(f"\nDone — {len(captured)} screenshots + report in {OUT}")


def _write_report(
    captured: list[str],
    defects: list[str],
    cover_url: str | None,
    cover_title: str | None,
    cover_was_synthetic: bool,
    no_cover_url: str | None,
    no_cover_title: str | None,
) -> None:
    lines: list[str] = []
    a = lines.append

    a(f"# Visual Audit Report — {DATE}")
    a("")
    a("**Branch:** `main`  ")
    a("**Commit under review:** `f9da53e` (CSS QA fixes — contact gap + page-hero narrow padding)  ")
    a("**Method:** Playwright Chromium full-page screenshots, `networkidle` wait + 600 ms font/transition settle  ")
    a(f"**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    a("")
    a("---")
    a("")
    a("## Audit viewports")
    a("")
    a("| Label | Width × Height | Role |")
    a("|---|---|---|")
    a("| `320x568` | 320 × 568 | iPhone SE (portrait) |")
    a("| `390x844` | 390 × 844 | iPhone 14 (portrait) |")
    a("| `768x1024` | 768 × 1024 | iPad Mini (portrait) — mobile nav active |")
    a("| `1024x1366` | 1024 × 1366 | iPad Pro 11\" (portrait) — desktop nav |")
    a("| `1440x900-extra` | 1440 × 900 | Extra — desktop wide |")
    a("")
    a("---")
    a("")
    a("## Routes captured")
    a("")
    a("### Core pages")
    for label, path in CORE_PAGES:
        a(f"- `{path}`")
    a("")
    a("### Project detail")
    if cover_url:
        note = " *(synthetic JPEG placeholder — no real photo in seeded data)*" if cover_was_synthetic else ""
        a(f"- **With cover:** `{cover_url}` — *{cover_title}*{note}")
    else:
        a("- **With cover:** NOT CAPTURED — no project with cover image found")

    if no_cover_url:
        a(f"- **Without cover:** `{no_cover_url}` — *{no_cover_title}*")
    else:
        a("- **Without cover:** NOT CAPTURED — no project without cover image found")

    a("")
    a("---")
    a("")
    a("## Screenshots index")
    a("")
    a("| File | Page | Viewport |")
    a("|---|---|---|")
    for f in sorted(captured):
        parts = f.replace(".png", "").split("-")
        # reconstruct page and viewport from filename
        a(f"| `{f}` | | |")
    a("")
    a("---")
    a("")
    a("## Inspection findings")
    a("")
    a("### About page — hero vertical space at 320 and 390")
    a("")
    a("Fix applied in `f9da53e`: `@media (max-width: 480px)` drops `.page-hero` top-padding")
    a("from `calc(4.5rem + 7rem) = 11.5rem` to `calc(4.5rem + 4rem) = 8.5rem`.")
    a("")
    a("Review `about-320x568.png` and `about-390x844.png`:")
    a("- [ ] Hero top-padding appears compact (≈ 8.5 rem, not 11.5 rem) at both widths")
    a("- [ ] Title and subtitle are readable before the fold")
    a("- [ ] No overflow or clipping on title text")
    a("")
    a("### Services page — hero vertical space at 320 and 390")
    a("")
    a("Same fix as About — Services also uses `.page-hero` (not `--short`).")
    a("")
    a("Review `services-320x568.png` and `services-390x844.png`:")
    a("- [ ] Same compact top-padding as About")
    a("- [ ] Services title readable before fold")
    a("")
    a("### Contact page — layout at 768 and 1024")
    a("")
    a("Fix applied in `f9da53e`: `gap: var(--space-lg)` (4 rem) in the `≤960px` media query,")
    a("replacing `var(--space-xl)` (7 rem). At 768px the grid is 1-col (≤900px rule stacks it)")
    a("so the gap fix is irrelevant there. At 1024px the `≤960px` rule is NOT active —")
    a("the grid is `1fr 340px` with `var(--space-xl)` gap.")
    a("")
    a("**Correction noted:** The 769–960px gap fix applies to a range that covers 769–900px")
    a("(form still 2-col) and 901–960px (form stacked to 1-col anyway).")
    a("The most vulnerable range is 769–900px where both the 2-col grid AND 2-col form rows")
    a("are active simultaneously.")
    a("")
    a("Review `contact-768x1024.png` and `contact-1024x1366.png`:")
    a("- [ ] At 768: full 1-col stacked layout (≤900px rule should apply) — form rows single-column")
    a("- [ ] At 1024: 2-col grid with reasonable column widths — form fields not cramped")
    a("- [ ] Submit button sizing appropriate at both widths")
    a("- [ ] No overflow in textarea or select elements")
    a("")
    a("### Sticky header — all pages")
    a("")
    a("Note: Playwright `full_page=True` captures the entire document, not just the")
    a("initial viewport. The fixed header will appear only at the top of the screenshot.")
    a("Sticky behaviour over scroll cannot be verified from static screenshots.")
    a("")
    a("Review header presence at the top of each full-page capture:")
    a("- [ ] Header present and correctly styled at 320 and 390 (mobile nav toggle visible)")
    a("- [ ] Header present at 768 (mobile nav) and 1024 (desktop nav)")
    a("")
    a("### Sticky sidebar (About page)")
    a("")
    a("Portrait sidebar is `position: sticky; top: 5.5rem` at > 900px,")
    a("`position: static` at ≤ 900px. 768px and below should show portrait inline (stacked).")
    a("")
    a("Review `about-768x1024.png` and `about-1024x1366.png`:")
    a("- [ ] At 768: portrait stacked before bio content (1-col layout)")
    a("- [ ] At 1024: portrait in left column alongside bio text (2-col)")
    a("")
    a("### Overflow, clipping, awkward wraps")
    a("")
    a("Review all 320px captures especially:")
    a("- [ ] `home-320x568.png` — hero CTA buttons wrap cleanly (flex-wrap)")
    a("- [ ] `projects-320x568.png` — filter bar tabs wrap or scroll without overflow")
    a("- [ ] `contact-320x568.png` — form fields full-width, no horizontal overflow")
    a("- [ ] `services-320x568.png` — service number + title row fits in single line")
    a("")
    a("### Projects filter bar")
    a("")
    a("Review `projects-320x568.png`, `projects-390x844.png`, `projects-768x1024.png`:")
    a("- [ ] Filter bar visible and sticky position correct (top: 4.5 rem)")
    a("- [ ] Filter pills wrap or scroll without breaking the layout")
    a("- [ ] Project cards render at 1-col on 320 and 390 (≤640px rule)")
    a("- [ ] Project cards render at 2-col on 768 (768 > 640px, still below 1024px)")
    a("")
    a("### Project detail hero — with cover")
    if cover_was_synthetic:
        a("")
        a("> **Note:** Cover image is a synthetic 1200×800 JPEG placeholder, not a real photo.")
        a("> Gradient overlay, text legibility, and layout are verifiable. Photo quality is not.")
    a("")
    a("Review `project-detail-cover-*.png`:")
    a("- [ ] Cover image fills the hero area (78svh at desktop/tablet)")
    a("- [ ] Gradient overlay makes title text readable")
    a("- [ ] Breadcrumb, category label, title, and description all visible")
    a("- [ ] No overflow on title at 320 or 390")
    a("")
    a("### Project detail hero — without cover")
    a("")
    a("Review `project-detail-no-cover-*.png`:")
    a("- [ ] Dark (`var(--c-black)`) surface renders — no white-on-white")
    a("- [ ] compact height matches `page-hero--short` rhythm (not 78svh)")
    a("- [ ] Title and description readable in white on dark")
    a("- [ ] No double-stacked padding (the `2720a08` fix)")
    a("")
    a("---")
    a("")
    a("## Pass / Fail summary")
    a("")
    a("| Area | Status | Notes |")
    a("|---|---|---|")
    a("| About hero padding (320, 390) | **PENDING REVIEW** | See `about-320x568.png`, `about-390x844.png` |")
    a("| Services hero padding (320, 390) | **PENDING REVIEW** | See `services-320x568.png`, `services-390x844.png` |")
    a("| Contact layout (768, 1024) | **PENDING REVIEW** | See `contact-768x1024.png`, `contact-1024x1366.png` |")
    a("| Projects filter + grid | **PENDING REVIEW** | See `projects-*.png` |")
    a("| Project detail with cover | **PENDING REVIEW** | See `project-detail-cover-*.png` |")
    a("| Project detail without cover | **PENDING REVIEW** | See `project-detail-no-cover-*.png` |")
    a("")
    a("---")
    a("")
    a("## Data notes")
    a("")
    if cover_was_synthetic:
        a("- **No real cover images exist in the seeded dataset.** A synthetic 1200×800 JPEG")
        a("  placeholder was attached to the first project for cover-variant capture,")
        a("  then removed. Cover-image layout is verifiable; photo rendering is not.")
    else:
        a("- Cover-image project used a real uploaded image.")
    a(f"- All 4 seeded projects have no cover in the standard `seed_demo` data.")
    a("- To test with a real photo: upload a cover via Admin → Projects → [project] → Cover image.")
    a("")
    a("---")
    a("")
    a("## Defects")
    a("")
    if defects:
        for d in defects:
            a(f"- {d}")
    else:
        a("_No automated defects detected during capture._")
        a("Manual review of screenshot files required to complete this section.")
    a("")
    a("---")
    a("")
    a("## Commit verdict")
    a("")
    a("`f9da53e` — *css: visual QA fixes — contact gap + page-hero narrow padding*")
    a("")
    a("Screenshots have been captured. **Rendered verdict is PENDING manual inspection**")
    a("of the files listed above. The commit cannot be marked pass/fail until the")
    a("inspection checklist above has been worked through against the actual PNG files.")

    report_path = OUT / "report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  {report_path.name}")


if __name__ == "__main__":
    main()
