#!/usr/bin/env python3
"""Generate README.md for the collection.

Usage:
    python3 scripts/build_readme.py

Previews use the thumbnails published on the ``gh-pages`` branch, so the file
stays small on GitHub. The workflow runs this after deploying the site.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "Wallpapers"
SUFFIXES = (".jpg", ".jpeg", ".png", ".webp", ".gif")
USER = "SpreadSheets600"
REPO = "Wallpapers"
SITE = f"https://{USER.lower()}.github.io/{REPO}/"
THUMBS = f"https://raw.githubusercontent.com/{USER}/{REPO}/gh-pages/thumbs"


def image_files() -> list[str]:
    return sorted(
        (f.name for f in IMAGES.iterdir() if f.suffix.lower() in SUFFIXES),
        key=lambda n: (0, int(Path(n).stem)) if Path(n).stem.isdigit() else (1, n),
    )


def build_root(images: list[str]) -> str:
    size = sum((IMAGES / n).stat().st_size for n in images) / 1048576

    rows = []
    for start in range(0, len(images), 4):
        cells = [
            f'<a href="Wallpapers/{image}"><img src="{THUMBS}/{Path(image).stem}.webp" '
            f'width="220" alt="{image}"></a>'
            for image in images[start:start + 4]
        ]
        cells += [""] * (4 - len(cells))
        rows.append("| " + " | ".join(cells) + " |")

    return f"""# wallpapers

A wallpaper collection I actually use, numbered in a stable order so the
gallery, the README and the folder always agree.

`{len(images)}` images &middot; `{size:.0f} MB`

**Gallery: [{SITE.replace('https://', '')}]({SITE})**

The gallery is generated, not hand-written: GitHub Actions builds the
thumbnails, this README and the static site on every push and publishes them to
the `gh-pages` branch. Clicking a thumbnail on the site opens the full-size
image from this branch.

## wallpapers

|  |  |  |  |
|---|---|---|---|
{chr(10).join(rows)}

## adding or removing wallpapers

```bash
git clone https://github.com/{USER}/{REPO}.git
cd {REPO}

# add or delete files under Wallpapers/
python3 scripts/organize.py      # HEIC -> JPEG, renumber loose files

git add -A && git commit -m "feat: add wallpapers" && git push
```

The push is all you need: the workflow regenerates the README, the thumbnails
and the site, commits the README back here and force-pushes a fresh `gh-pages`
branch.

To preview the site locally (Pillow or ImageMagick needed):

```bash
python3 -m pip install --user pillow
python3 scripts/build_site.py
python3 -m http.server -d _site 8000
```

## layout

```text
Wallpapers/<n>.<ext>                the images, numbered in a stable order
scripts/build_site.py               thumbnails + site -> _site/ (gh-pages)
scripts/build_readme.py             this README
scripts/organize.py                 HEIC conversion, renumbering
.github/workflows/site.yml          build + deploy on push
```

## credits

I do not own any of these images; everything belongs to the respective artists
and is collected for personal desktop use. If you own an image and want it
removed, open an issue and it will be taken down.
"""


def main() -> None:
    images = image_files()
    (ROOT / "README.md").write_text(build_root(images), encoding="utf-8")
    print(f"wrote README.md ({len(images)} images)")


if __name__ == "__main__":
    main()
