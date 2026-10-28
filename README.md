# wallpapers

A wallpaper collection I actually use, sorted by subject and then by colour so
every folder flows from one palette into the next.

`164` images &middot; `357 MB` &middot; `14` collections

**Gallery: [spreadsheets600.github.io/Wallpapers/](https://spreadsheets600.github.io/Wallpapers/)**

The gallery is generated, not hand-written: GitHub Actions builds the
thumbnails, the READMEs and the static site on every push and publishes them to
the `gh-pages` branch. Clicking a thumbnail on the site opens the full-size
image from this branch.

## collections

| cover | collection | images | size |
|---|---|---|---|
| <img src="https://raw.githubusercontent.com/SpreadSheets600/Wallpapers/gh-pages/thumbs/Abstract/1.webp" width="180" alt="Abstract"> | **[Abstract](Wallpapers/Abstract/)** | 8 | 16.1 MB |
| <img src="https://raw.githubusercontent.com/SpreadSheets600/Wallpapers/gh-pages/thumbs/Anime/1.webp" width="180" alt="Anime"> | **[Anime](Wallpapers/Anime/)** | 9 | 37.6 MB |
| <img src="https://raw.githubusercontent.com/SpreadSheets600/Wallpapers/gh-pages/thumbs/City/1.webp" width="180" alt="City"> | **[City](Wallpapers/City/)** | 8 | 4.6 MB |
| <img src="https://raw.githubusercontent.com/SpreadSheets600/Wallpapers/gh-pages/thumbs/Cyberpunk/1.webp" width="180" alt="Cyberpunk"> | **[Cyberpunk](Wallpapers/Cyberpunk/)** | 4 | 7.1 MB |
| <img src="https://raw.githubusercontent.com/SpreadSheets600/Wallpapers/gh-pages/thumbs/Fantasy/1.webp" width="180" alt="Fantasy"> | **[Fantasy](Wallpapers/Fantasy/)** | 6 | 8.9 MB |
| <img src="https://raw.githubusercontent.com/SpreadSheets600/Wallpapers/gh-pages/thumbs/Flowers/1.webp" width="180" alt="Flowers"> | **[Flowers](Wallpapers/Flowers/)** | 43 | 78.4 MB |
| <img src="https://raw.githubusercontent.com/SpreadSheets600/Wallpapers/gh-pages/thumbs/Manga/1.webp" width="180" alt="Manga"> | **[Manga](Wallpapers/Manga/)** | 7 | 11.1 MB |
| <img src="https://raw.githubusercontent.com/SpreadSheets600/Wallpapers/gh-pages/thumbs/Minimal/1.webp" width="180" alt="Minimal"> | **[Minimal](Wallpapers/Minimal/)** | 16 | 6.6 MB |
| <img src="https://raw.githubusercontent.com/SpreadSheets600/Wallpapers/gh-pages/thumbs/Mountain/1.webp" width="180" alt="Mountain"> | **[Mountain](Wallpapers/Mountain/)** | 10 | 28.0 MB |
| <img src="https://raw.githubusercontent.com/SpreadSheets600/Wallpapers/gh-pages/thumbs/Nature/1.webp" width="180" alt="Nature"> | **[Nature](Wallpapers/Nature/)** | 15 | 21.5 MB |
| <img src="https://raw.githubusercontent.com/SpreadSheets600/Wallpapers/gh-pages/thumbs/Photography/1.webp" width="180" alt="Photography"> | **[Photography](Wallpapers/Photography/)** | 5 | 3.2 MB |
| <img src="https://raw.githubusercontent.com/SpreadSheets600/Wallpapers/gh-pages/thumbs/Sea/1.webp" width="180" alt="Sea"> | **[Sea](Wallpapers/Sea/)** | 6 | 15.1 MB |
| <img src="https://raw.githubusercontent.com/SpreadSheets600/Wallpapers/gh-pages/thumbs/Space/1.webp" width="180" alt="Space"> | **[Space](Wallpapers/Space/)** | 5 | 25.3 MB |
| <img src="https://raw.githubusercontent.com/SpreadSheets600/Wallpapers/gh-pages/thumbs/WuWa/2.webp" width="180" alt="WuWa"> | **[WuWa](Wallpapers/WuWa/)** | 22 | 93.7 MB |

## adding or removing wallpapers

```bash
git clone https://github.com/SpreadSheets600/Wallpapers.git
cd Wallpapers

# add or delete files under Wallpapers/<Collection>/
python3 scripts/organize.py      # HEIC -> JPEG, renumber loose files

git add -A && git commit -m "feat: add wallpapers" && git push
```

The push is all you need: the workflow regenerates the READMEs, the thumbnails
and the site, commits the READMEs back here and force-pushes a fresh `gh-pages`
branch.

To preview the site locally (Pillow or ImageMagick needed):

```bash
python3 -m pip install --user pillow
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
