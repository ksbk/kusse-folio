"""
Pixel-level analysis of visual audit screenshots.
Produces structured findings to fill the report.

Run: uv run python scripts/analyse_screenshots.py
"""

from __future__ import annotations

import datetime
from pathlib import Path

from PIL import Image

AUDIT = Path(__file__).resolve().parent.parent / "artifacts" / "visual-audit" / "2026-03-24"

# Design token colours (from tokens.css)
C_BLACK  = (26,  25,  23)   # --c-black  #1A1917
C_STONE  = (242, 238, 233)  # --c-stone  #F2EEE9
C_WHITE  = (250, 250, 248)  # --c-white  #FAFAF8
C_WARM   = (221, 217, 211)  # --c-warm-grey #DDD9D3

TOLERANCE = 18  # pixel colour comparison tolerance


def load(name: str) -> Image.Image:
    return Image.open(AUDIT / name).convert("RGB")


def near(px: tuple, ref: tuple, tol: int = TOLERANCE) -> bool:
    return all(abs(a - b) <= tol for a, b in zip(px, ref))


def sample_row(img: Image.Image, y: int, x_fraction: float = 0.5) -> tuple:
    x = int(img.width * x_fraction)
    return img.getpixel((x, y))


def first_bright_row(img: Image.Image, x_fraction: float = 0.5,
                     start_y: int = 100) -> int | None:
    """Find the first row (from start_y) where pixel is near white."""
    x = int(img.width * x_fraction)
    for y in range(start_y, img.height):
        if near(img.getpixel((x, y)), C_WHITE, tol=12):
            return y
    return None


def dominant_top_color(img: Image.Image, rows: int = 8) -> str:
    """Sample the top N rows across several x positions; return 'dark'/'stone'/'white'."""
    samples = []
    for y in range(10, 10 + rows):
        for frac in (0.25, 0.5, 0.75):
            samples.append(img.getpixel((int(img.width * frac), y)))
    dark  = sum(1 for p in samples if near(p, C_BLACK, 30) or near(p, (40, 38, 35), 30))
    stone = sum(1 for p in samples if near(p, C_STONE, 20))
    white = sum(1 for p in samples if near(p, C_WHITE, 20))
    if dark  >= len(samples) // 2: return "dark"
    if stone >= len(samples) // 2: return "stone"
    if white >= len(samples) // 2: return "white"
    return f"mixed (dark={dark} stone={stone} white={white} total={len(samples)})"


def hero_height_px(img: Image.Image) -> int | None:
    """
    For stone-bg heroes (about, services): scan downward from y=80
    (safely past the fixed nav) to find where stone gives way to white/dark.
    Uses a strict white threshold (tol=8) to avoid confusing stone with white.
    Returns the y-coordinate of that transition (≈ hero bottom).
    """
    x = int(img.width * 0.5)
    found_stone = False
    for y in range(80, img.height):
        px = img.getpixel((x, y))
        is_stone = near(px, C_STONE, 28)
        # Strict tolerance for white — C_STONE is close to C_WHITE
        is_white = (
            abs(px[0] - C_WHITE[0]) <= 8
            and abs(px[1] - C_WHITE[1]) <= 8
            and abs(px[2] - C_WHITE[2]) <= 8
        )
        is_dark  = near(px, C_BLACK, 35)
        if is_stone:
            found_stone = True
        if found_stone and (is_white or is_dark):
            return y
    return None


def check_horizontal_overflow(img: Image.Image, margin: int = 3) -> bool:
    """
    Check if any non-white/near-white pixels exist in the rightmost `margin` columns.
    A consistent non-background strip on the right edge suggests overflow.
    """
    w, h = img.size
    unusual = 0
    for y in range(0, h, 4):
        for x in range(w - margin, w):
            px = img.getpixel((x, y))
            if not (near(px, C_WHITE, 25) or near(px, C_STONE, 25)
                    or near(px, C_BLACK, 25) or near(px, C_WARM, 25)):
                unusual += 1
    return unusual > 20  # noise threshold


def contact_is_single_col(img: Image.Image) -> bool:
    """
    Heuristic: in single-column layout (≤900px), the form occupies the full
    width with no sidebar. We sample a horizontal band mid-page and check
    whether the right 30% of the viewport is background-colour only (sidebar
    absent) vs contains form-field colours.
    Form fields have border #DDD9D3 and bg #FAFAF8; they'll appear similar
    to the white background. The sidebar, when present, has a distinct sticky
    top area with text. This is hard to detect purely by colour.

    Simpler proxy: if image height > 2.5× the viewport height it was rendered
    at, the page is likely long and single-column (sidebar not reducing page
    height). We'll use the ratio of image height to image width as a proxy for
    layout density — a stacked 1-col page will be taller relative to its width.
    Not definitive but indicative.
    """
    ratio = img.height / img.width
    # 768×1024 viewport: 1-col stacked page will be very tall (ratio >> 1)
    return ratio > 2.0


def main() -> None:
    findings: list[str] = []
    f = findings.append

    f("=" * 70)
    f("VISUAL AUDIT — PIXEL ANALYSIS")
    f(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    f("=" * 70)

    # -----------------------------------------------------------------------
    # 1. Project detail — cover vs no-cover hero darkness + raw pixel dump
    # -----------------------------------------------------------------------
    f("\n--- PROJECT DETAIL HERO DARKNESS ---")
    for label, fname_cov, fname_nocov in [
        ("320x568",   "project-detail-cover-320x568.png",   "project-detail-no-cover-320x568.png"),
        ("390x844",   "project-detail-cover-390x844.png",   "project-detail-no-cover-390x844.png"),
        ("768x1024",  "project-detail-cover-768x1024.png",  "project-detail-no-cover-768x1024.png"),
        ("1024x1366", "project-detail-cover-1024x1366.png", "project-detail-no-cover-1024x1366.png"),
    ]:
        cov_img = load(fname_cov)
        noc_img = load(fname_nocov)
        cov_top = dominant_top_color(cov_img)
        noc_top = dominant_top_color(noc_img)
        # Raw pixel at y=10, centre-x
        cov_raw = cov_img.getpixel((cov_img.width // 2, 10))
        noc_raw = noc_img.getpixel((noc_img.width // 2, 10))
        # Sample hero midpoint (e.g. y=40% of typical hero height ~300px → y=120)
        cov_mid = cov_img.getpixel((cov_img.width // 2, 120))
        noc_mid = noc_img.getpixel((noc_img.width // 2, 120))
        f(f"[{label}]  cover top: {cov_top}  raw@y10={cov_raw}  raw@y120={cov_mid}")
        f(f"         noc top: {noc_top}  raw@y10={noc_raw}  raw@y120={noc_mid}")

    # -----------------------------------------------------------------------
    # 2. About page — hero bottom (stone → next section transition)
    # -----------------------------------------------------------------------
    f("\n--- ABOUT HERO HEIGHT (px from top of document) ---")
    for label, fname in [
        ("320x568",   "about-320x568.png"),
        ("390x844",   "about-390x844.png"),
        ("768x1024",  "about-768x1024.png"),
        ("1024x1366", "about-1024x1366.png"),
    ]:
        img = load(fname)
        hy  = hero_height_px(img)
        pct = f"{hy/img.height*100:.1f}% of page height" if hy else "N/A"
        f(f"[{label}]  hero ends at y={hy}px  ({pct})  image_h={img.height}px")

    # -----------------------------------------------------------------------
    # 3. Services page — same measurement
    # -----------------------------------------------------------------------
    f("\n--- SERVICES HERO HEIGHT (px from top of document) ---")
    for label, fname in [
        ("320x568",   "services-320x568.png"),
        ("390x844",   "services-390x844.png"),
        ("768x1024",  "services-768x1024.png"),
        ("1024x1366", "services-1024x1366.png"),
    ]:
        img = load(fname)
        hy  = hero_height_px(img)
        pct = f"{hy/img.height*100:.1f}% of page height" if hy else "N/A"
        f(f"[{label}]  hero ends at y={hy}px  ({pct})  image_h={img.height}px")

    # -----------------------------------------------------------------------
    # 4. Contact — single vs two-column heuristic
    # -----------------------------------------------------------------------
    f("\n--- CONTACT LAYOUT (height/width ratio heuristic) ---")
    for label, fname in [
        ("320x568",   "contact-320x568.png"),
        ("390x844",   "contact-390x844.png"),
        ("768x1024",  "contact-768x1024.png"),
        ("1024x1366", "contact-1024x1366.png"),
    ]:
        img = load(fname)
        ratio = img.height / img.width
        verdict = "likely 1-col" if ratio > 1.8 else "likely 2-col or medium height"
        f(f"[{label}]  {img.width}×{img.height}  ratio={ratio:.2f}  → {verdict}")

    # -----------------------------------------------------------------------
    # 5. Horizontal overflow check
    # -----------------------------------------------------------------------
    f("\n--- HORIZONTAL OVERFLOW CHECK ---")
    files_to_check = [
        ("home-320x568.png",     "Home 320"),
        ("about-320x568.png",    "About 320"),
        ("services-320x568.png", "Services 320"),
        ("projects-320x568.png", "Projects 320"),
        ("contact-320x568.png",  "Contact 320"),
        ("about-390x844.png",    "About 390"),
        ("contact-768x1024.png", "Contact 768"),
        ("contact-1024x1366.png","Contact 1024"),
        ("project-detail-cover-320x568.png",   "PD Cover 320"),
        ("project-detail-no-cover-320x568.png","PD NoCover 320"),
    ]
    for fname, label in files_to_check:
        img = load(fname)
        overflow = check_horizontal_overflow(img)
        f(f"  {label:<22} overflow={overflow}")

    # -----------------------------------------------------------------------
    # 6. About portrait layout check (1-col vs 2-col heuristic at 768 vs 1024)
    # -----------------------------------------------------------------------
    f("\n--- ABOUT PORTRAIT LAYOUT (image height/width ratio) ---")
    for label, fname in [
        ("320x568",   "about-320x568.png"),
        ("390x844",   "about-390x844.png"),
        ("768x1024",  "about-768x1024.png"),
        ("1024x1366", "about-1024x1366.png"),
        ("1440x900-extra", "about-1440x900-extra.png"),
    ]:
        img = load(fname)
        ratio = img.height / img.width
        # About 2-col: portrait left, bio right — page won't be as tall
        # About 1-col: portrait above, bio below — page will be taller
        verdict = "portrait stacked above bio (1-col expected)" if ratio > 2.5 else "portrait beside bio (2-col)"
        f(f"[{label}]  {img.width}×{img.height}  ratio={ratio:.2f}  → {verdict}")

    # -----------------------------------------------------------------------
    # 7. Projects page — approximate card grid check
    # -----------------------------------------------------------------------
    f("\n--- PROJECTS GRID (document height relative to vp width) ---")
    for label, fname in [
        ("320x568",   "projects-320x568.png"),
        ("390x844",   "projects-390x844.png"),
        ("768x1024",  "projects-768x1024.png"),
        ("1024x1366", "projects-1024x1366.png"),
    ]:
        img = load(fname)
        f(f"[{label}]  {img.width}×{img.height}")

    f("\n" + "=" * 70)
    print("\n".join(findings))


if __name__ == "__main__":
    main()
