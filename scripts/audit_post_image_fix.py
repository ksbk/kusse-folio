"""
Screenshot audit for homepage image + coda fixes.

Captures both SiteSettings configs (3/4/6 and 1/2/4) at three viewports
and counts actually-visible project cards (CSS-aware).

Usage:  uv run python scripts/audit_post_image_fix.py
Server: must be running on localhost:8000
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

import django
django.setup()

from asgiref.sync import sync_to_async
from playwright.async_api import async_playwright
from apps.core.models import SiteSettings

OUT = "artifacts/visual-audit/post-image-fix"
BASE_URL = "http://localhost:8000"
VIEWPORTS = [
    (390,  844,  "mobile"),
    (768,  1024, "tablet"),
    (1440, 900,  "desktop"),
]


@sync_to_async
def apply_config(mob, tab, desk):
    site = SiteSettings.load()
    site.homepage_projects_mobile_count = mob
    site.homepage_projects_tablet_count = tab
    site.homepage_projects_desktop_count = desk
    site.save()


async def shoot_config(browser, label, mob, tab, desk):
    await apply_config(mob, tab, desk)
    print(f"\n-- Config {mob}/{tab}/{desk} --")
    for w, h, vp_name in VIEWPORTS:
        page = await browser.new_page(viewport={"width": w, "height": h})
        await page.goto(f"{BASE_URL}/", wait_until="networkidle")

        path = f"{OUT}/{label}_{vp_name}_{w}x{h}.png"
        await page.screenshot(path=path, full_page=True)

        visible   = await page.evaluate("""() =>
            [...document.querySelectorAll('.project-card')]
            .filter(el => window.getComputedStyle(el).display !== 'none').length
        """)
        with_img  = await page.evaluate("""() =>
            [...document.querySelectorAll('.project-card')]
            .filter(el => window.getComputedStyle(el).display !== 'none')
            .filter(el => el.querySelector('img') !== null).length
        """)
        blanks    = visible - with_img
        flag = "  ✓" if blanks == 0 else f"  ✗ {blanks} blank card(s)"
        print(f"  {vp_name:7s} {w}x{h}  →  {visible} visible  {with_img} with-image{flag}")
        await page.close()


async def main():
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        await shoot_config(browser, "3-4-6", 3, 4, 6)
        await shoot_config(browser, "1-2-4", 1, 2, 4)
        await browser.close()

    await apply_config(3, 4, 6)   # restore default
    print(f"\nScreenshots: {OUT}/")


asyncio.run(main())
