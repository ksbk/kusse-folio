"""
Management command: bootstrap_project

Create a new Project record with optional cover and gallery images in a safe,
human-controlled way.  Always run with --dry-run first.

One project per invocation — intentional.

Usage examples
--------------
Dry run — title + category only:
    python manage.py bootstrap_project \\
        --title "Residential Housing — Reykjavík" \\
        --category residential \\
        --dry-run

Dry run — full:
    python manage.py bootstrap_project \\
        --title "Residential Housing — Reykjavík" \\
        --category residential \\
        --short-description "Multi-family residential housing project." \\
        --cover /Users/ksb/Downloads/jeanote/byggingar_jeannot_0061_unnin.jpg \\
        --gallery /Users/ksb/Downloads/jeanote/byggingar_jeannot_0096_unnin.jpg \\
                  /Users/ksb/Downloads/jeanote/byggingar_jeannot_0034_unnin.jpg \\
                  /Users/ksb/Downloads/jeanote/byggingar_jeannot_0025_unnin.jpg \\
        --featured --order 1 \\
        --dry-run

Live run (remove --dry-run when satisfied):
    python manage.py bootstrap_project \\
        --title "Residential Housing — Reykjavík" \\
        --category residential \\
        --cover /Users/ksb/Downloads/jeanote/byggingar_jeannot_0061_unnin.jpg \\
        --gallery /Users/ksb/Downloads/jeanote/byggingar_jeannot_0096_unnin.jpg \\
                  /Users/ksb/Downloads/jeanote/byggingar_jeannot_0034_unnin.jpg \\
        --featured --order 1

Safety rules
------------
- If a Project with the generated slug already exists, the command aborts.
  Use import_project_images to add images to an existing project.
- All file paths are validated before any database write.
- --dry-run prints the full plan and exits without saving anything.
"""

import os
import re
from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

from projects.models import Project, ProjectImage

_PLACEHOLDER_DESCRIPTION = "[Placeholder — update in admin]"

# Valid category keys derived from the model's CATEGORY_CHOICES
_VALID_CATEGORIES = {key for key, _ in Project.CATEGORY_CHOICES}

# Strips Django's collision-avoidance suffix, e.g. "img_vFlUiiN" → "img"
_DJANGO_SUFFIX_RE = re.compile(r"_[A-Za-z0-9]{7}$")


def _stem_without_suffix(name: str) -> str:
    stem = Path(name).stem
    return _DJANGO_SUFFIX_RE.sub("", stem)


def _basename_matches(source_path: str, stored_path: str) -> bool:
    source_stem = _stem_without_suffix(os.path.basename(source_path))
    stored_stem = _stem_without_suffix(os.path.basename(stored_path))
    return source_stem == stored_stem


class Command(BaseCommand):
    help = (
        "Create a new Project record with optional cover and gallery images. "
        "One project per invocation. Always run with --dry-run first."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--title",
            required=True,
            metavar="TITLE",
            help="Project title. The slug is generated automatically via slugify().",
        )
        parser.add_argument(
            "--category",
            required=True,
            metavar="CATEGORY",
            choices=sorted(_VALID_CATEGORIES),
            help=(
                "Project category. "
                f"Valid values: {', '.join(sorted(_VALID_CATEGORIES))}."
            ),
        )
        parser.add_argument(
            "--short-description",
            default=_PLACEHOLDER_DESCRIPTION,
            metavar="TEXT",
            help=(
                f"Short description (max 300 chars). "
                f"Defaults to: '{_PLACEHOLDER_DESCRIPTION}'"
            ),
        )
        parser.add_argument(
            "--cover",
            metavar="FILE",
            help="Absolute path to the cover image.",
        )
        parser.add_argument(
            "--gallery",
            nargs="+",
            metavar="FILE",
            help="Absolute path(s) to gallery image(s).",
        )
        parser.add_argument(
            "--featured",
            action="store_true",
            default=False,
            help="Mark the project as featured (shown on home page).",
        )
        parser.add_argument(
            "--order",
            type=int,
            default=0,
            metavar="N",
            help="Display order (integer, default 0).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="Print what would happen without saving anything.",
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _validate_file(self, path: str) -> Path:
        p = Path(path)
        if not p.is_absolute():
            raise CommandError(f"Path must be absolute: {path}")
        if not p.exists():
            raise CommandError(f"File does not exist: {path}")
        if not p.is_file():
            raise CommandError(f"Path is not a file: {path}")
        return p

    def _gallery_duplicates(
        self, existing_stems: set[str], sources: list[str]
    ) -> dict[str, bool]:
        return {
            src: (_stem_without_suffix(os.path.basename(src)) in existing_stems)
            for src in sources
        }

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------

    def handle(self, *args, **options):
        dry_run: bool = options["dry_run"]
        title: str = options["title"]
        category: str = options["category"]
        short_description: str = options["short_description"]
        cover_path: str | None = options["cover"]
        gallery_paths: list[str] = options["gallery"] or []
        featured: bool = options["featured"]
        order: int = options["order"]

        slug = slugify(title)

        # ------------------------------------------------------------------
        # Guard: slug collision
        # ------------------------------------------------------------------
        if Project.objects.filter(slug=slug).exists():
            raise CommandError(
                f"A Project with slug '{slug}' already exists. "
                "Use import_project_images to add images to an existing project, "
                "or choose a different title."
            )

        # ------------------------------------------------------------------
        # Validate all file paths up front — before any DB write
        # ------------------------------------------------------------------
        cover_file: Path | None = None
        if cover_path:
            cover_file = self._validate_file(cover_path)

        gallery_files: list[Path] = [self._validate_file(p) for p in gallery_paths]

        # ------------------------------------------------------------------
        # Duplicate detection for gallery
        # New project has no images yet, so no true duplicates are possible.
        # Check within the supplied gallery list itself for repeated files.
        # ------------------------------------------------------------------
        seen_stems: set[str] = set()
        intra_duplicates: set[str] = set()
        for gf in gallery_files:
            stem = _stem_without_suffix(gf.name)
            if stem in seen_stems:
                intra_duplicates.add(str(gf))
            seen_stems.add(stem)

        # ------------------------------------------------------------------
        # Report plan
        # ------------------------------------------------------------------
        mode = "[DRY RUN] " if dry_run else ""
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f"\n{mode}bootstrap_project"
            )
        )
        self.stdout.write(f"  Title    : {title}")
        self.stdout.write(f"  Slug     : {slug}")
        self.stdout.write(f"  Category : {category}")
        self.stdout.write(f"  Featured : {featured}")
        self.stdout.write(f"  Order    : {order}")
        self.stdout.write(f"  Short desc: {short_description}")

        if cover_file:
            self.stdout.write(
                f"  {'WOULD SET' if dry_run else 'SET'} cover: {cover_file.name}"
            )
        else:
            self.stdout.write("  Cover    : (none)")

        if gallery_files:
            counter = 1
            for gf in gallery_files:
                is_dup = str(gf) in intra_duplicates
                if is_dup:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  SKIP gallery (duplicate in supplied list): {gf.name}"
                        )
                    )
                else:
                    self.stdout.write(
                        f"  {'WOULD ADD' if dry_run else 'ADD'} gallery [{counter}]: {gf.name}"
                    )
                    counter += 1
        else:
            self.stdout.write("  Gallery  : (none)")

        # ------------------------------------------------------------------
        # Exit here if dry run
        # ------------------------------------------------------------------
        if dry_run:
            self.stdout.write(
                self.style.NOTICE(
                    "\nDry run complete — nothing was saved. "
                    "Remove --dry-run to apply."
                )
            )
            return

        # ------------------------------------------------------------------
        # Create Project
        # ------------------------------------------------------------------
        project = Project(
            title=title,
            slug=slug,
            category=category,
            short_description=short_description,
            featured=featured,
            order=order,
            status="completed",
        )
        project.save()
        self.stdout.write(self.style.SUCCESS(f"\n  ✓ Project created (id={project.pk}, slug={project.slug})"))

        # ------------------------------------------------------------------
        # Cover
        # ------------------------------------------------------------------
        if cover_file:
            with cover_file.open("rb") as fh:
                project.cover_image.save(cover_file.name, File(fh), save=True)
            self.stdout.write(self.style.SUCCESS(f"  ✓ Cover saved → {project.cover_image.name}"))

        # ------------------------------------------------------------------
        # Gallery
        # ------------------------------------------------------------------
        gallery_order = 1
        for gf in gallery_files:
            if str(gf) in intra_duplicates:
                continue
            img = ProjectImage(project=project, order=gallery_order, image_type="gallery")
            with gf.open("rb") as fh:
                img.image.save(gf.name, File(fh), save=False)
            img.save()
            self.stdout.write(self.style.SUCCESS(f"  ✓ Gallery [{gallery_order}] saved → {img.image.name}"))
            gallery_order += 1

        self.stdout.write(self.style.SUCCESS("\nDone."))
