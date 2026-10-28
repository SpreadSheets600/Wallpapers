from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "Wallpapers"
SUFFIXES = (".jpg", ".jpeg", ".png", ".webp", ".gif")

USER = "SpreadSheets600"
REPO = "Wallpapers"

SITE = f"https://{USER.lower()}.github.io/{REPO}/"
THUMBS = f"https://raw.githubusercontent.com/{USER}/{REPO}/gh-pages/thumbs"


def image_files():
    return sorted(
        (f.name for f in IMAGES.iterdir() if f.suffix.lower() in SUFFIXES),
        key=lambda n: (0, int(Path(n).stem)) if Path(n).stem.isdigit() else (1, n),
    )


def build_root(images: list[str]):
    size = sum((IMAGES / n).stat().st_size for n in images) / 1048576

    rows = []

    for start in range(0, len(images), 4):
        cells = [
            f'<a href="Wallpapers/{image}"><img src="{THUMBS}/{Path(image).stem}.webp" '
            f'width="220" alt="{image}"></a>'
            for image in images[start : start + 4]
        ]

        cells += [""] * (4 - len(cells))
        rows.append("| " + " | ".join(cells) + " |")

    return f"""# wallpapers

A wallpaper collection I actually use, curated over time, numbered in a stable order so the
gallery, the README and the folder always agree.

### `{len(images)}` Images &middot; `{size:.0f} MB`

**Gallery: [{SITE.replace("https://", "")}]({SITE})**

> [!NOTE] 
> The gallery is generated - GitHub Actions builds the
thumbnails, this README and the static site on every push and publishes them to
the `gh-pages` branch. Clicking a thumbnail on the site opens the full-size
image from this branch.

## Wallpapers

|  |  |  |  |
|---|---|---|---|
{chr(10).join(rows)}

## Adding Or Removing Wallpapers

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

## Credits

> [!NOTE] 
> I do not own any of these images. Everything belongs to the respective artists
and is collected for personal desktop use. If you own an image and want it
removed, open an issue and it will be taken down.
"""


def main():
    images = image_files()
    (ROOT / "README.md").write_text(build_root(images), encoding="utf-8")

    print(f"Completed README.md For ({len(images)} Images)")


if __name__ == "__main__":
    main()
