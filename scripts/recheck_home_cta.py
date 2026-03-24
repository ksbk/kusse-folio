"""
Retake home-320x568 and home-390x844 screenshots after the hero CTA overflow fix.
Also DOM-probes scrollWidth at 320 to confirm the ghost overflow is gone.

Run: uv run python scripts/recheck_home_cta.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import django
django.setup()

from playwright.sync_api import sync_playwright

AUDIT = Path(__file__).resolve().parent.parent / "artifacts" / "visual-audit" / "2026-03-24"
BASE = "http://127.0.0.1:8765"

VIEWPORTS = [
    {"label": "320x568", "w": 320, "h": 568},
    {"label": "390x844", "w": 390, "h": 844},
]


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for vp in VIEWPORTS:
            context = browser.new_context(viewport={"width": vp["w"], "height": vp["h"]})
            page = context.new_page()
            page.goto(f"{BASE}/", wait_until="networkidle")
            page.wait_for_timeout(600)

            fname = f"home-{vp['label']}.png"
            page.screenshot(path=str(AUDIT / fname), full_page=True)
            print(f"  captured {fname}")

            # Verify scrollWidth
            scroll_w = page.evaluate("() => document.documentElement.scrollWidth")
            img_w = vp["w"]
            status = "OK (no overflow)" if scroll_w <= img_w else f"OVERFLOW: scrollWidth={scroll_w}"
            print(f"  scrollWidth={scroll_w}  viewport={img_w}  → {status}")

            context.close()

        browser.close()

    print("\nDone.")


if __name__ == "__main__":
    main()
