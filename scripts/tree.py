#!/usr/bin/env python3
"""
tree.py — pretty-print a directory tree.

Usage:
  python scripts/tree.py [ROOT] [OPTIONS]

Examples:
  python scripts/tree.py
  python scripts/tree.py . --depth 2
  python scripts/tree.py . --all --size
  python scripts/tree.py . --ignore dist build --no-color
  python scripts/tree.py . --only "*.py" "*.html"
"""

from __future__ import annotations

import argparse
import fnmatch
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# ANSI colours — disabled automatically when not writing to a TTY
# ---------------------------------------------------------------------------

USE_COLOR = sys.stdout.isatty()


class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    DIR = "\033[1;34m"  # bold blue
    LINK = "\033[1;36m"  # bold cyan
    EXEC = "\033[1;32m"  # bold green
    HIDDEN = "\033[2;37m"  # dim grey
    SIZE = "\033[0;33m"  # yellow
    COUNT = "\033[0;36m"  # cyan

    # Extension → colour mapping
    EXT_COLORS: dict[str, str] = {
        ".py": "\033[0;32m",  # green
        ".html": "\033[0;33m",  # yellow
        ".css": "\033[0;35m",  # magenta
        ".js": "\033[0;33m",  # yellow
        ".ts": "\033[0;34m",  # blue
        ".json": "\033[0;36m",  # cyan
        ".md": "\033[0;37m",  # light grey
        ".txt": "\033[0;37m",
        ".env": "\033[0;31m",  # red  (sensitive)
        ".yaml": "\033[0;36m",
        ".yml": "\033[0;36m",
        ".toml": "\033[0;36m",
        ".cfg": "\033[0;36m",
        ".ini": "\033[0;36m",
        ".sh": "\033[1;32m",
        ".sql": "\033[0;35m",
        ".png": "\033[0;35m",
        ".jpg": "\033[0;35m",
        ".jpeg": "\033[0;35m",
        ".gif": "\033[0;35m",
        ".svg": "\033[0;35m",
        ".pdf": "\033[0;31m",
    }


def colorize(text: str, code: str) -> str:
    if not USE_COLOR:
        return text
    return f"{code}{text}{C.RESET}"


def file_color(name: str) -> str:
    ext = Path(name).suffix.lower()
    return C.EXT_COLORS.get(ext, "")


# ---------------------------------------------------------------------------
# Gitignore-aware ignore logic
# ---------------------------------------------------------------------------

DEFAULT_IGNORE_DIRS = {
    ".venv",
    ".mypy_cache",
    ".git",
    "__pycache__",
    "staticfiles",
    "node_modules",
    ".tox",
}
DEFAULT_IGNORE_FILES = {"db.sqlite3", ".env"}
DEFAULT_IGNORE_SUFFIXES = {".pyc", ".pyo", ".pyd", ".egg-info"}


def load_gitignore(root: Path) -> list[str]:
    """Return gitignore patterns found at root."""
    gi = root / ".gitignore"
    if not gi.is_file():
        return []
    patterns = []
    for line in gi.read_text(errors="replace").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            patterns.append(line.rstrip("/"))
    return patterns


def matches_any(name: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(name, p) for p in patterns)


# ---------------------------------------------------------------------------
# Human-readable file size
# ---------------------------------------------------------------------------


def human_size(n: int) -> str:
    for unit in ("B", "K", "M", "G"):
        if n < 1024:
            return f"{n:>4}{unit}"
        n //= 1024
    return f"{n:>4}T"


# ---------------------------------------------------------------------------
# Core tree walk
# ---------------------------------------------------------------------------


def tree(
    path: Path,
    *,
    prefix: str = "",
    depth: int,
    max_depth: int,
    show_hidden: bool,
    show_size: bool,
    dirs_only: bool,
    only_patterns: list[str],
    extra_ignore: list[str],
    gitignore_patterns: list[str],
    stats: dict,
) -> None:
    if max_depth != -1 and depth > max_depth:
        return

    try:
        raw = list(os.scandir(path))
    except PermissionError:
        print(prefix + colorize("  [permission denied]", C.DIM))
        return

    def should_skip(e: os.DirEntry) -> bool:
        name = e.name
        if not show_hidden and name.startswith("."):
            return True
        if e.is_dir(follow_symlinks=False):
            if name in DEFAULT_IGNORE_DIRS:
                return True
        else:
            if name in DEFAULT_IGNORE_FILES:
                return True
            if any(name.endswith(s) for s in DEFAULT_IGNORE_SUFFIXES):
                return True
        if matches_any(name, extra_ignore):
            return True
        if matches_any(name, gitignore_patterns):
            return True
        return bool(
            only_patterns
            and not e.is_dir(follow_symlinks=False)
            and not matches_any(name, only_patterns)
        )

    entries = [e for e in raw if not should_skip(e)]
    entries.sort(key=lambda e: (not e.is_dir(follow_symlinks=False), e.name.lower()))

    for i, entry in enumerate(entries):
        is_last = i == len(entries) - 1
        connector = "└── " if is_last else "├── "
        extension = "    " if is_last else "│   "

        is_dir = entry.is_dir(follow_symlinks=False)
        is_link = entry.is_symlink()

        if is_dir:
            stats["dirs"] += 1
            label = colorize(entry.name + "/", C.DIR)
            if is_link:
                target = os.readlink(entry.path)
                label += colorize(f" → {target}", C.LINK)
            print(f"{prefix}{connector}{label}")
            if not dirs_only:
                tree(
                    Path(entry.path),
                    prefix=prefix + extension,
                    depth=depth + 1,
                    max_depth=max_depth,
                    show_hidden=show_hidden,
                    show_size=show_size,
                    dirs_only=dirs_only,
                    only_patterns=only_patterns,
                    extra_ignore=extra_ignore,
                    gitignore_patterns=gitignore_patterns,
                    stats=stats,
                )
        else:
            stats["files"] += 1
            name = entry.name

            if is_link:
                label = colorize(name, C.LINK) + colorize(f" → {os.readlink(entry.path)}", C.DIM)
            elif show_hidden and name.startswith("."):
                label = colorize(name, C.HIDDEN)
            elif os.access(entry.path, os.X_OK):
                label = colorize(name, C.EXEC)
            else:
                col = file_color(name)
                label = colorize(name, col) if col else name

            size_str = ""
            if show_size:
                try:
                    sz = entry.stat(follow_symlinks=False).st_size
                    stats["bytes"] += sz
                    size_str = " " + colorize(f"[{human_size(sz)}]", C.SIZE)
                except OSError:
                    pass

            print(f"{prefix}{connector}{label}{size_str}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="tree.py",
        description="Print a pretty directory tree.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "root",
        nargs="?",
        default=".",
        metavar="ROOT",
        help="Root directory (default: current directory)",
    )
    p.add_argument(
        "-d",
        "--depth",
        type=int,
        default=-1,
        metavar="N",
        help="Maximum display depth (-1 = unlimited)",
    )
    p.add_argument(
        "-a",
        "--all",
        dest="show_hidden",
        action="store_true",
        help="Show hidden files and directories (dotfiles)",
    )
    p.add_argument(
        "-s",
        "--size",
        dest="show_size",
        action="store_true",
        help="Show file sizes",
    )
    p.add_argument(
        "-D",
        "--dirs-only",
        dest="dirs_only",
        action="store_true",
        help="List directories only",
    )
    p.add_argument(
        "--ignore",
        nargs="+",
        default=[],
        metavar="PATTERN",
        help="Additional glob patterns to ignore (e.g. dist build '*.log')",
    )
    p.add_argument(
        "--only",
        nargs="+",
        default=[],
        metavar="PATTERN",
        help="Show only files matching these glob patterns (e.g. '*.py' '*.html')",
    )
    p.add_argument(
        "--no-gitignore",
        dest="use_gitignore",
        action="store_false",
        help="Disable .gitignore-aware filtering",
    )
    p.add_argument(
        "--no-color",
        dest="color",
        action="store_false",
        help="Disable coloured output",
    )
    p.add_argument(
        "--summary",
        action="store_true",
        default=True,
        help="Print directory/file count summary (default: on)",
    )
    p.add_argument(
        "--no-summary",
        dest="summary",
        action="store_false",
        help="Suppress the summary line",
    )
    return p


def main() -> None:
    global USE_COLOR

    args = build_parser().parse_args()

    if not args.color:
        USE_COLOR = False

    root = Path(args.root).resolve()
    if not root.exists():
        print(f"tree.py: '{root}' does not exist", file=sys.stderr)
        sys.exit(1)

    gitignore_patterns = load_gitignore(root) if args.use_gitignore else []

    stats: dict = {"dirs": 0, "files": 0, "bytes": 0}

    # Print root
    print(colorize(str(root), C.DIR if root.is_dir() else ""))

    tree(
        root,
        depth=1,
        max_depth=args.depth,
        show_hidden=args.show_hidden,
        show_size=args.show_size,
        dirs_only=args.dirs_only,
        only_patterns=args.only,
        extra_ignore=args.ignore,
        gitignore_patterns=gitignore_patterns,
        stats=stats,
    )

    if args.summary:
        parts = [
            colorize(str(stats["dirs"]), C.COUNT)
            + " director"
            + ("y" if stats["dirs"] == 1 else "ies"),
            colorize(str(stats["files"]), C.COUNT) + " file" + ("" if stats["files"] == 1 else "s"),
        ]
        if args.show_size and stats["bytes"]:
            total = stats["bytes"]
            parts.append(colorize(human_size(total), C.SIZE) + " total")
        print("\n" + colorize("─" * 40, C.DIM))
        print("  " + ",  ".join(parts))


if __name__ == "__main__":
    main()
