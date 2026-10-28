import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IMAGES = ROOT / "Wallpapers"

SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}
HEIC = {".heic", ".heif"}


def convert_heic(path: Path):
    target = path.with_suffix(".jpg")

    subprocess.run(
        ["magick", f"{path}[0]", "-auto-orient", "-quality", "92", str(target)],
        check=True,
    )
    path.unlink()
    print(f"Converted {path.name} -> {target.name}")

    return target


def main():
    if not IMAGES.is_dir():
        print(f"No Wallpapers Directory In {ROOT}", file=sys.stderr)
        return 1

    for file in sorted(IMAGES.iterdir()):
        if file.is_file() and file.suffix.lower() in HEIC:
            convert_heic(file)

    files = [
        f
        for f in sorted(IMAGES.iterdir())
        if f.is_file() and f.suffix.lower() in SUFFIXES
    ]

    numbered = [f for f in files if f.stem.isdigit()]
    loose = [f for f in files if not f.stem.isdigit()]

    if not loose:
        return 0

    next_number = max((int(f.stem) for f in numbered), default=0) + 1
    for file in loose:
        target = IMAGES / f"{next_number}{file.suffix.lower()}"
        file.rename(target)

        print(f"{file.name} -> {target.name}")
        next_number += 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
