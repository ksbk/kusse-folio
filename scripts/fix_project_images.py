"""
Fix homepage featured-project image state.

Context
-------
seed_demo.py was updated with new project slugs (house-on-the-hillside,
community-library-pavilion, etc.) but the demo media folder still contains
images for the old slug set (coastline-civic-centre, harbour-court-apartments,
harbour-glass-offices).  As a result five featured projects lack preview
images.  This script:

  1. Assigns cover images to all five new-seed featured projects, sourcing
     from the existing local demo media — no external downloads.
  2. Unfeatured the three old-seed orphan projects and pushes their order
     to 11–13 so they no longer compete for the homepage top-6 slots.
  3. Adds ridgeline-housing gallery images to house-on-the-hillside so the
     project detail page is also properly illustrated.

Image source mapping (all from media/ tree)
-------------------------------------------
  house-on-the-hillside       ← demo_seed/.../ridgeline-housing/01–05.jpg
                                  (housing gallery, same category)
  community-library-pavilion  ← demo_seed/.../coastline-civic-centre/01.jpg
                                  (civic gallery, same category)
  commercial-office-conversion ← projects/covers/commercial-office-conversion.jpg
                                  (file already present, orphaned from old seed)
  civic-waterfront-square     ← demo_seed/.../coastline-civic-centre/02.jpg
                                  (civic gallery, same category)
  housing-block-north-quarter ← demo_seed/.../harbour-court-apartments/01.jpg
                                  (housing gallery, same category)

Usage:  uv run python scripts/fix_project_images.py
"""

import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

import django
django.setup()

from apps.projects.models import Project, ProjectImage

MEDIA = Path("media")
DEMO = MEDIA / "demo_seed" / "strand-architecture"


def _copy_cover(src: Path, slug: str) -> str:
    """Copy src into projects/covers/<slug>.jpg, return relative path."""
    dest_rel = f"projects/covers/{slug}.jpg"
    dest = MEDIA / dest_rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        shutil.copy2(src, dest)
    return dest_rel


def assign_cover(slug: str, src_rel: str, note: str = "") -> None:
    """Assign a cover image to a project by slug."""
    try:
        p = Project.objects.get(slug=slug)
    except Project.DoesNotExist:
        print(f"  SKIP  {slug} — project not found in DB")
        return

    if p.cover_image:
        print(f"  SKIP  {slug} — already has cover: {p.cover_image.name}")
        return

    src = MEDIA / src_rel
    if not src.exists():
        print(f"  ERROR {slug} — source file not found: {src}")
        return

    dest_rel = _copy_cover(src, slug)
    p.cover_image = dest_rel
    p.save(update_fields=["cover_image"])
    print(f"  OK    {slug}: cover = {dest_rel}  [{note}]")


def assign_gallery(slug: str, sources: list[str], start_order: int = 1) -> None:
    """Attach gallery ProjectImage records to a project (skip if already present)."""
    try:
        p = Project.objects.get(slug=slug)
    except Project.DoesNotExist:
        return

    existing = ProjectImage.objects.filter(project=p, image_type="gallery").count()
    if existing:
        print(f"  SKIP  {slug} gallery — already has {existing} gallery image(s)")
        return

    for i, src_rel in enumerate(sources):
        src = MEDIA / src_rel
        if not src.exists():
            print(f"  WARN  {slug} gallery {i+1} — source not found: {src_rel}")
            continue
        ext = src.suffix.lower()
        dest_rel = f"projects/gallery/{slug}/{i+1:02d}{ext}"
        dest = MEDIA / dest_rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists():
            shutil.copy2(src, dest)
        ProjectImage.objects.create(
            project=p,
            image=dest_rel,
            alt_text=p.title,
            order=start_order + i,
            image_type="gallery",
        )
        print(f"  OK    {slug} gallery/{i+1:02d}")


print("=" * 60)
print("STEP 1 — Assign cover images to new-seed featured projects")
print("=" * 60)

assign_cover(
    "house-on-the-hillside",
    "demo_seed/strand-architecture/gallery/ridgeline-housing/01.jpg",
    note="ridgeline-housing/01.jpg — housing gallery, same category",
)
assign_cover(
    "community-library-pavilion",
    "demo_seed/strand-architecture/gallery/coastline-civic-centre/01.jpg",
    note="coastline-civic-centre/01.jpg — civic gallery, same category",
)

# commercial-office-conversion: the file already exists in projects/covers/
# (orphaned from an earlier seed run) — point the DB field at it directly
_coml_slug = "commercial-office-conversion"
_coml_path = "projects/covers/commercial-office-conversion.jpg"
try:
    _p = Project.objects.get(slug=_coml_slug)
    if not _p.cover_image and (MEDIA / _coml_path).exists():
        _p.cover_image = _coml_path
        _p.save(update_fields=["cover_image"])
        print(f"  OK    {_coml_slug}: cover = {_coml_path}  [existing orphan file, same slug]")
    elif _p.cover_image:
        print(f"  SKIP  {_coml_slug} — already has cover")
    else:
        print(f"  WARN  {_coml_slug} — orphan file not found, falling back to demo_seed")
        assign_cover(
            _coml_slug,
            "demo_seed/strand-architecture/covers/harbour-glass-offices.jpg",
            note="harbour-glass-offices.jpg — workplace cover, same category",
        )
except Project.DoesNotExist:
    print(f"  SKIP  {_coml_slug} — not found in DB")

assign_cover(
    "civic-waterfront-square",
    "demo_seed/strand-architecture/gallery/coastline-civic-centre/02.jpg",
    note="coastline-civic-centre/02.jpg — civic gallery, same category",
)
assign_cover(
    "housing-block-north-quarter",
    "demo_seed/strand-architecture/gallery/harbour-court-apartments/01.jpg",
    note="harbour-court-apartments/01.jpg — housing gallery, same category",
)

print()
print("=" * 60)
print("STEP 2 — Add gallery images to house-on-the-hillside")
print("=" * 60)

assign_gallery(
    "house-on-the-hillside",
    [
        "demo_seed/strand-architecture/gallery/ridgeline-housing/02.jpg",
        "demo_seed/strand-architecture/gallery/ridgeline-housing/03.jpg",
        "demo_seed/strand-architecture/gallery/ridgeline-housing/04.jpg",
        "demo_seed/strand-architecture/gallery/ridgeline-housing/05.jpg",
    ],
)

print()
print("=" * 60)
print("STEP 3 — Unfeatured old-seed orphan projects, fix order")
print("=" * 60)

OLD_SEED_ORPHANS = [
    ("coastline-civic-centre",    11),
    ("harbour-court-apartments",  12),
    ("harbour-glass-offices",     13),
]
for slug, new_order in OLD_SEED_ORPHANS:
    try:
        p = Project.objects.get(slug=slug)
        p.featured = False
        p.order = new_order
        p.save(update_fields=["featured", "order"])
        print(f"  OK    {slug}: featured=False, order={new_order}")
    except Project.DoesNotExist:
        print(f"  SKIP  {slug} — not found in DB")

print()
print("=" * 60)
print("STEP 4 — Final state check")
print("=" * 60)
for p in Project.objects.filter(featured=True).order_by("order"):
    cover = p.cover_image.name if p.cover_image else None
    ngal = ProjectImage.objects.filter(project=p, image_type="gallery").count()
    has_preview = bool(cover or ngal)
    flag = "✓" if has_preview else "✗ MISSING"
    print(f"  {p.order}  {p.slug:<45s} {flag}  cover={'yes' if cover else 'no'}  gallery={ngal}")

print()
print("Done.")
