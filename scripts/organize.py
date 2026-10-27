#!/usr/bin/env python3
"""Tidy the collection: convert HEIC, renumber loose images.

Usage:
    python3 scripts/organize.py

Every image in ``Wallpapers/<Category>/`` ends up numbered 1..n so the
directory listing, the READMEs and the site stay in sync. Existing numbers are
kept and new files get the next free number, in the order they are found.
HEIC/HEIF files are converted to JPEG because most desktop environments cannot
set them as a wallpaper.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "Wallpapers"
SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}
HEIC = {".heic", ".heif"}


def convert_heic(path: Path) -> Path:
    target = path.with_suffix(".jpg")
    subprocess.run(
        ["magick", f"{path}[0]", "-auto-orient", "-quality", "92", str(target)],
        check=True,
    )
    path.unlink()
    print(f"converted {path.name} -> {target.name}")
    return target


def main() -> int:
    if not IMAGES.is_dir():
        print(f"no Wallpapers/ directory in {ROOT}", file=sys.stderr)
        return 1

    for category in sorted(p for p in IMAGES.iterdir() if p.is_dir()):
        files = [f for f in sorted(category.iterdir()) if f.is_file()]
        for file in files:
            if file.suffix.lower() in HEIC:
                convert_heic(file)

        files = [
            f for f in sorted(category.iterdir())
            if f.is_file() and f.suffix.lower() in SUFFIXES
        ]
        numbered = [f for f in files if f.stem.isdigit()]
        loose = [f for f in files if not f.stem.isdigit()]
        if not loose:
            continue

        next_number = max((int(f.stem) for f in numbered), default=0) + 1
        for file in loose:
            target = category / f"{next_number}{file.suffix.lower()}"
            file.rename(target)
            print(f"{category.name}: {file.name} -> {target.name}")
            next_number += 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
