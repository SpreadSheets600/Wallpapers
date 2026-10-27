#!/usr/bin/env python3
"""Generate README.md and one README.md per category.

Usage:
    python3 scripts/build_readme.py

Previews use the thumbnails published on the ``gh-pages`` branch, so these
files stay small on GitHub. The workflow runs this after deploying the site.
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


def image_files(category: Path) -> list[str]:
    return sorted(
        (f.name for f in category.iterdir() if f.suffix.lower() in SUFFIXES),
        key=lambda n: (0, int(Path(n).stem)) if Path(n).stem.isdigit() else (1, n),
    )


def categories() -> list[tuple[str, list[str], int]]:
    result = []
    for path in sorted(p for p in IMAGES.iterdir() if p.is_dir()):
        images = image_files(path)
        if not images:
            continue
        size = sum((path / n).stat().st_size for n in images)
        result.append((path.name, images, size))
    return result


def build_root(cats) -> str:
    total = sum(len(images) for _, images, _ in cats)
    size = sum(s for _, _, s in cats) / 1048576

    rows = [
        f'| <img src="{THUMBS}/{name}/{Path(images[0]).stem}.webp" width="180" alt="{name}"> '
        f"| **[{name}](Wallpapers/{name}/)** | {len(images)} | {s / 1048576:.1f} MB |"
        for name, images, s in cats
    ]

    return f"""# wallpapers

A wallpaper collection I actually use, sorted by subject and then by colour so
every folder flows from one palette into the next.

`{total}` images &middot; `{size:.0f} MB` &middot; `{len(cats)}` collections

**Gallery: [{SITE.replace('https://', '')}]({SITE})**

The gallery is generated, not hand-written: GitHub Actions builds the
thumbnails, the READMEs and the static site on every push and publishes them to
the `gh-pages` branch. Clicking a thumbnail on the site opens the full-size
image from this branch.

## collections

| cover | collection | images | size |
|---|---|---|---|
{chr(10).join(rows)}

## adding or removing wallpapers

```bash
git clone https://github.com/{USER}/{REPO}.git
cd {REPO}

# add or delete files under Wallpapers/<Collection>/
python3 scripts/organize.py      # HEIC -> JPEG, renumber loose files

git add -A && git commit -m "feat: add wallpapers" && git push
```

The push is all you need: the workflow regenerates the READMEs, the thumbnails
and the site, commits the READMEs back here and force-pushes a fresh `gh-pages`
branch.

To preview the site locally:

```bash
python3 scripts/build_site.py
python3 -m http.server -d _site 8000
```

## layout

```text
Wallpapers/<Collection>/<n>.<ext>   the images, numbered in colour order
scripts/build_site.py               thumbnails + site -> _site/ (gh-pages)
scripts/build_readme.py             this README and the per-collection ones
scripts/organize.py                 HEIC conversion, renumbering
.github/workflows/site.yml          build + deploy on push
```

## credits

I do not own any of these images; everything belongs to the respective artists
and is collected for personal desktop use. If you own an image and want it
removed, open an issue and it will be taken down.
"""


def build_category(name: str, images: list[str]) -> str:
    size = sum((IMAGES / name / image).stat().st_size for image in images) / 1048576
    rows = []
    for start in range(0, len(images), 4):
        cells = [
            f'<a href="{image}"><img src="{THUMBS}/{name}/{Path(image).stem}.webp" '
            f'width="220" alt="{name} {image}"></a>'
            for image in images[start:start + 4]
        ]
        cells += [""] * (4 - len(cells))
        rows.append("| " + " | ".join(cells) + " |")

    return f"""# {name}

[&larr; all collections](../README.md) &middot; [gallery]({SITE}{name}/)

`{len(images)}` images &middot; `{size:.1f} MB`

|  |  |  |  |
|---|---|---|---|
{chr(10).join(rows)}

Every wallpaper belongs to its original creator. See the
[main README](../README.md#credits) for credits and takedown requests.
"""


def main() -> None:
    cats = categories()
    (ROOT / "README.md").write_text(build_root(cats), encoding="utf-8")
    for name, images, _ in cats:
        (IMAGES / name / "README.md").write_text(build_category(name, images), encoding="utf-8")
    print(f"wrote README.md + {len(cats)} category READMEs")


if __name__ == "__main__":
    main()
