#!/usr/bin/env python3
"""Build the static gallery in ``index.html`` + ``styles.css``.

Usage:
    python3 scripts/build_site.py

The output is plain HTML/CSS with no build step, so GitHub Pages can serve the
repository as-is. One page per category plus a landing page with a cover image
for each category.
"""

from __future__ import annotations

import html
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "Wallpapers"
SUFFIXES = (".jpg", ".jpeg", ".png", ".webp", ".gif")

CSS = """\
:root {
  --bg: #0b0b0f;
  --surface: #14141b;
  --line: #262630;
  --text: #e8e8ef;
  --muted: #9a9aa8;
  --accent: #a6e3a1;
}

* { box-sizing: border-box; }

html { color-scheme: dark; }

body {
  margin: 0;
  padding: 48px 24px 96px;
  background: var(--bg);
  color: var(--text);
  font-family: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 15px;
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
}

.wrap {
  width: min(1180px, 100%);
  margin: 0 auto;
}

header {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--line);
  margin-bottom: 32px;
}

h1 {
  font-size: clamp(1.6rem, 4vw, 2.4rem);
  font-weight: 600;
  letter-spacing: -0.02em;
  margin: 0;
}

h1 a { color: inherit; text-decoration: none; }

.sub {
  color: var(--muted);
  font-size: 0.85rem;
  margin: 0;
}

.sub a { color: var(--accent); text-decoration: none; }

.categories {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
}

.category {
  position: relative;
  display: block;
  overflow: hidden;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: var(--surface);
  text-decoration: none;
  color: inherit;
  aspect-ratio: 16 / 10;
}

.category img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  opacity: 0.72;
  transition: opacity 0.25s ease, transform 0.4s ease;
}

.category:hover img,
.category:focus-visible img { opacity: 1; transform: scale(1.04); }

.category .label {
  position: absolute;
  inset: auto 0 0 0;
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 8px;
  padding: 32px 14px 12px;
  background: linear-gradient(transparent, rgba(5, 5, 9, 0.92));
  font-size: 0.95rem;
}

.category .count { color: var(--muted); font-size: 0.8rem; }

.grid {
  columns: 4 260px;
  column-gap: 16px;
}

.grid figure {
  margin: 0 0 16px;
  break-inside: avoid;
  border: 1px solid var(--line);
  border-radius: 10px;
  overflow: hidden;
  background: var(--surface);
}

.grid img {
  width: 100%;
  display: block;
  transition: opacity 0.2s ease;
}

.grid a:hover img { opacity: 0.8; }

footer {
  margin-top: 56px;
  padding-top: 20px;
  border-top: 1px solid var(--line);
  color: var(--muted);
  font-size: 0.8rem;
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 8px;
}

footer a { color: var(--muted); }

@media (prefers-reduced-motion: reduce) {
  * { transition: none !important; }
}
"""


def categories() -> list[tuple[str, list[str], int]]:
    result = []
    for path in sorted(p for p in IMAGES.iterdir() if p.is_dir()):
        images = sorted(
            (f.name for f in path.iterdir() if f.suffix.lower() in SUFFIXES),
            key=lambda name: (0, int(Path(name).stem)) if Path(name).stem.isdigit() else (1, name),
        )
        if not images:
            continue
        size = sum((path / name).stat().st_size for name in images)
        result.append((path.name, images, size))
    return result


def page(title: str, body: str, depth: int) -> str:
    prefix = "../" * depth
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="preconnect" href="https://cdn.jsdelivr.net">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fontsource/jetbrains-mono@5.0.0/index.min.css">
<link rel="stylesheet" href="{prefix}styles.css">
</head>
<body>
<div class="wrap">
{body}
<footer>
  <span>All wallpapers belong to their original creators.</span>
  <span><a href="https://github.com/SpreadSheets600/Wallpapers">github.com/SpreadSheets600/Wallpapers</a></span>
</footer>
</div>
</body>
</html>
"""


def build_index(cats) -> str:
    total = sum(len(images) for _, images, _ in cats)
    size = sum(size for _, _, size in cats)
    cards = []
    for name, images, _ in cats:
        cards.append(
            f'''  <a class="category" href="Wallpapers/{name}/">
    <img src="Wallpapers/{name}/{images[0]}" alt="{html.escape(name)}" loading="lazy">
    <span class="label">{html.escape(name)}<span class="count">{len(images)}</span></span>
  </a>'''
        )
    body = f'''<header>
  <h1>wallpapers</h1>
  <p class="sub">{total} images &middot; {size / 1048576:.0f} MB &middot; {len(cats)} categories</p>
</header>

<main class="categories">
{os.linesep.join(cards)}
</main>
'''
    return page("Wallpapers", body, 0)


def build_category(name: str, images: list[str]) -> str:
    figures = []
    for image in images:
        figures.append(
            f'''  <figure><a href="{image}" target="_blank" rel="noopener">'''
            f'''<img src="{image}" alt="{html.escape(name)} {html.escape(image)}" loading="lazy"></a></figure>'''
        )
    body = f'''<header>
  <h1><a href="../../index.html">{html.escape(name)}</a></h1>
  <p class="sub">{len(images)} images &middot; <a href="../../index.html">all categories</a></p>
</header>

<main class="grid">
{os.linesep.join(figures)}
</main>
'''
    return page(f"{name} wallpapers", body, 2)


def main() -> None:
    cats = categories()
    (ROOT / "styles.css").write_text(CSS, encoding="utf-8")
    (ROOT / "index.html").write_text(build_index(cats), encoding="utf-8")
    for name, images, _ in cats:
        (IMAGES / name / "index.html").write_text(build_category(name, images), encoding="utf-8")
    print(f"built index.html + {len(cats)} category pages")


if __name__ == "__main__":
    main()
