"""
Management command: import_project_images

Attach local image files to an existing Project record in a safe,
human-controlled way.  Always run with --dry-run first.

Usage examples
--------------
Dry run — cover only:
    python manage.py import_project_images --project residential-housing \\
        --cover /path/to/cover.jpg --dry-run

Set cover + gallery:
    python manage.py import_project_images --project residential-housing \\
        --cover /path/to/cover.jpg \\
        --gallery /path/to/a.jpg /path/to/b.jpg /path/to/c.jpg \\
        --dry-run

Live run (remove --dry-run when satisfied):
    python manage.py import_project_images --project residential-housing \\
        --cover /path/to/cover.jpg \\
        --gallery /path/to/a.jpg /path/to/b.jpg

Select project by numeric id instead of slug:
    python manage.py import_project_images --project-id 3 --gallery /path/to/a.jpg

Duplicate detection
-------------------
A file is considered a duplicate when a basename-matched filename is already
stored in the relevant ImageField path for the same project.  Django's own
collision-avoidance suffixes (_abc1234) are stripped before comparing, so a
file that was previously uploaded and renamed is still detected as a duplicate.
"""

import os
import re
from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from projects.models import Project, ProjectImage

# Regex that matches Django's collision-avoidance suffix, e.g.
# "cover_vFlUiiN" → "cover", "img_OV1wuG8" → "img"
_DJANGO_SUFFIX_RE = re.compile(r"_[A-Za-z0-9]{7}$")


def _stem_without_suffix(name: str) -> str:
    """Return the filename stem with any Django collision suffix stripped."""
    stem = Path(name).stem
    return _DJANGO_SUFFIX_RE.sub("", stem)


def _basename_matches(source_path: str, stored_path: str) -> bool:
    """Return True if source and stored paths share the same effective stem."""
    source_stem = _stem_without_suffix(os.path.basename(source_path))
    stored_stem = _stem_without_suffix(os.path.basename(stored_path))
    return source_stem == stored_stem


class Command(BaseCommand):
    help = (
        "Attach local image files to an existing Project record. "
        "Always run with --dry-run first to preview changes."
    )

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "--project",
            metavar="SLUG",
            help="Slug of the target project.",
        )
        group.add_argument(
            "--project-id",
            type=int,
            metavar="ID",
            help="Numeric pk of the target project.",
        )
        parser.add_argument(
            "--cover",
            metavar="FILE",
            help="Absolute path to the image to set as the cover.",
        )
        parser.add_argument(
            "--gallery",
            nargs="+",
            metavar="FILE",
            help="Absolute path(s) to image(s) to add to the gallery.",
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

    def _resolve_project(self, slug: str | None, pk: int | None) -> Project:
        try:
            if slug:
                return Project.objects.get(slug=slug)
            assert pk is not None  # guaranteed by mutually-exclusive argparse group
            return Project.objects.get(pk=pk)
        except Project.DoesNotExist as exc:
            identifier = f"slug='{slug}'" if slug else f"id={pk}"
            raise CommandError(f"No Project found with {identifier}.") from exc

    def _validate_file(self, path: str) -> Path:
        p = Path(path)
        if not p.is_absolute():
            raise CommandError(f"Path must be absolute: {path}")
        if not p.exists():
            raise CommandError(f"File does not exist: {path}")
        if not p.is_file():
            raise CommandError(f"Path is not a file: {path}")
        return p

    def _cover_is_duplicate(self, project: Project, source: str) -> bool:
        if not project.cover_image or not project.cover_image.name:
            return False
        return _basename_matches(source, project.cover_image.name)

    def _gallery_duplicates(self, project: Project, sources: list[str]) -> dict[str, bool]:
        """Return {source_path: is_duplicate} for each gallery candidate."""
        existing_stems = {
            _stem_without_suffix(os.path.basename(img.image.name))
            for img in project.images.all()
            if img.image.name
        }
        return {
            src: (_stem_without_suffix(os.path.basename(src)) in existing_stems)
            for src in sources
        }

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------

    def handle(self, *args, **options):
        dry_run: bool = options["dry_run"]
        cover_path: str | None = options["cover"]
        gallery_paths: list[str] = options["gallery"] or []

        if not cover_path and not gallery_paths:
            raise CommandError("Specify at least --cover or --gallery (or both).")

        project = self._resolve_project(options["project"], options["project_id"])

        # Validate all paths up front before touching anything
        cover_file: Path | None = None
        if cover_path:
            cover_file = self._validate_file(cover_path)

        gallery_files: list[Path] = [self._validate_file(p) for p in gallery_paths]

        # ------------------------------------------------------------------
        # Report target
        # ------------------------------------------------------------------
        mode = "[DRY RUN] " if dry_run else ""
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f"\n{mode}import_project_images → project: '{project.title}' (slug={project.slug}, id={project.pk})"
            )
        )

        # ------------------------------------------------------------------
        # Cover
        # ------------------------------------------------------------------
        if cover_file:
            duplicate = self._cover_is_duplicate(project, str(cover_file))
            if duplicate:
                self.stdout.write(
                    self.style.WARNING(
                        f"  SKIP cover  (duplicate detected): {cover_file.name}"
                    )
                )
            else:
                current = project.cover_image.name if project.cover_image else "(none)"
                self.stdout.write(
                    f"  {'WOULD SET' if dry_run else 'SET'} cover: {cover_file.name}"
                    f"  [was: {current}]"
                )
                if not dry_run:
                    with cover_file.open("rb") as fh:
                        project.cover_image.save(cover_file.name, File(fh), save=True)
                    self.stdout.write(self.style.SUCCESS(f"    ✓ cover saved → {project.cover_image.name}"))

        # ------------------------------------------------------------------
        # Gallery
        # ------------------------------------------------------------------
        if gallery_files:
            dup_map = self._gallery_duplicates(project, [str(f) for f in gallery_files])
            next_order = (
                project.images.order_by("-order").values_list("order", flat=True).first() or 0
            ) + 1

            for gf in gallery_files:
                is_dup = dup_map[str(gf)]
                if is_dup:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  SKIP gallery (duplicate detected): {gf.name}"
                        )
                    )
                else:
                    self.stdout.write(
                        f"  {'WOULD ADD' if dry_run else 'ADD'} gallery [{next_order}]: {gf.name}"
                    )
                    if not dry_run:
                        img = ProjectImage(project=project, order=next_order, image_type="gallery")
                        with gf.open("rb") as fh:
                            img.image.save(gf.name, File(fh), save=False)
                        img.save()
                        self.stdout.write(self.style.SUCCESS(f"    ✓ gallery saved → {img.image.name}"))
                    next_order += 1

        # ------------------------------------------------------------------
        # Summary
        # ------------------------------------------------------------------
        if dry_run:
            self.stdout.write(
                self.style.NOTICE(
                    "\nDry run complete — nothing was saved. "
                    "Remove --dry-run to apply."
                )
            )
        else:
            self.stdout.write(self.style.SUCCESS("\nDone."))
