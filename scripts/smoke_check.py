"""Quick smoke check: all routes 200, key HTML content present."""
import os
import sys
from pathlib import Path

# Ensure project root is on sys.path when run from scripts/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

import django  # noqa: E402

django.setup()

from django.test import Client  # noqa: E402

c = Client(SERVER_NAME="localhost")
failures = []

ROUTES = [
    ("/", "home"),
    ("/about/", "about"),
    ("/services/", "services"),
    ("/contact/", "contact"),
    ("/contact/thank-you/", "contact_success"),
    ("/projects/", "projects list"),
    ("/sitemap.xml", "sitemap"),
    ("/robots.txt", "robots"),
]

for path, name in ROUTES:
    r = c.get(path, HTTP_HOST="localhost")
    ok = r.status_code == 200
    sym = "OK  " if ok else "FAIL"
    print(f"{sym} {r.status_code} {name}")
    if not ok:
        failures.append(f"{name} returned {r.status_code}")

# Content checks on home page
home = c.get("/", HTTP_HOST="localhost")
CONTENT_CHECKS = [
    (b"skip-link", "skip-to-content link"),
    (b"favicon.svg", "favicon link"),
    (b"og:site_name", "og:site_name meta"),
    (b"twitter:card", "twitter:card meta"),
    (b"og:title", "og:title meta"),
]
for needle, label in CONTENT_CHECKS:
    found = needle in home.content
    sym = "OK  " if found else "MISS"
    print(f"{sym} home contains: {label}")
    if not found:
        failures.append(f"home missing: {label}")

# contact_success noindex
success = c.get("/contact/thank-you/", HTTP_HOST="localhost")
noindex = b"noindex" in success.content
sym = "OK  " if noindex else "MISS"
print(f"{sym} contact_success: noindex meta")
if not noindex:
    failures.append("contact_success missing noindex")

# services page title
services = c.get("/services/", HTTP_HOST="localhost")
title_ok = b"Architectural Services" in services.content
sym = "OK  " if title_ok else "MISS"
print(f"{sym} services: 'Architectural Services' in title")
if not title_ok:
    failures.append("services page title not updated")

# about og:title
about = c.get("/about/", HTTP_HOST="localhost")
og_about = "About \u2014 " in about.content.decode()
sym = "OK  " if og_about else "MISS"
print(f"{sym} about: og:title override present")
if not og_about:
    failures.append("about og:title missing")

# contact og:title
contact = c.get("/contact/", HTTP_HOST="localhost")
og_contact = "Contact \u2014 " in contact.content.decode()
sym = "OK  " if og_contact else "MISS"
print(f"{sym} contact: og:title override present")
if not og_contact:
    failures.append("contact og:title missing")

# projects list canonical should not contain ?category=
# Request with a filter query param; strip-to-path canonical should equal /projects/
projects = c.get("/projects/?category=residential", HTTP_HOST="localhost")
canonical_clean = b'rel="canonical" href="http://localhost/projects/"' in projects.content
sym = "OK  " if canonical_clean else "MISS"
print(f"{sym} projects list: canonical strips query string")
if not canonical_clean:
    failures.append("projects list canonical includes query string")

print()
if failures:
    print(f"FAILED: {len(failures)} checks")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
else:
    print("All checks passed!")
