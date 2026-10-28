#!/usr/bin/env python3
"""Build the gallery into ``_site/``.

Usage:
    python3 scripts/build_site.py            # build
    python3 scripts/build_site.py --clean    # rebuild thumbnails from scratch

The output is what gets published to the ``gh-pages`` branch:

    _site/index.html            thumbnail grid with a lightbox
    _site/styles.css            shared stylesheet
    _site/thumbs/*.webp         480 px thumbnails

Full-size images are not copied. They are linked straight from the repository
through raw.githubusercontent.com, so the site stays small and the thumbnails
are the only thing a visitor downloads while browsing.

Thumbnails are made with Pillow (``pip install pillow``), or with
ImageMagick (``magick``/``convert``) when Pillow is not installed.
"""

from __future__ import annotations

import html
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "Wallpapers"
SITE = ROOT / "_site"
THUMBS = SITE / "thumbs"

USER = "SpreadSheets600"
REPO = "Wallpapers"
BRANCH = "master"
RAW = f"https://raw.githubusercontent.com/{USER}/{REPO}/{BRANCH}/Wallpapers"

THUMB_WIDTH = 480
SUFFIXES = (".jpg", ".jpeg", ".png", ".webp", ".gif")

try:  # Pillow is what CI uses: a wheel, no apt step to hang on.
    from PIL import Image, ImageOps
except ImportError:  # local fallback, ImageMagick
    Image = None

IM = shutil.which("magick") or shutil.which("convert")
IDENTIFY = shutil.which("identify")


def image_files() -> list[str]:
    return sorted(
        (f.name for f in IMAGES.iterdir() if f.suffix.lower() in SUFFIXES),
        key=lambda n: (0, int(Path(n).stem)) if Path(n).stem.isdigit() else (1, n),
    )


def dimensions(paths: list[Path]) -> dict[str, tuple[int, int]]:
    if not paths:
        return {}
    sizes = {}
    if Image is not None:
        for path in paths:
            with Image.open(path) as im:
                sizes[path.name] = im.size
        return sizes
    if not IDENTIFY:
        return {}
    out = subprocess.run(
        [IDENTIFY, "-format", "%w %h\n", *map(str, paths)],
        capture_output=True, text=True, check=True,
    ).stdout.split()
    for path, w, h in zip(paths, out[0::2], out[1::2]):
        sizes[path.name] = (int(w), int(h))
    return sizes


def webp_supported() -> bool:
    if Image is not None:
        from PIL import features
        return features.check("webp")
    if not IM:
        return False
    out = subprocess.run([IM, "-list", "format"], capture_output=True, text=True)
    for line in out.stdout.splitlines():
        if line.strip().upper().startswith("WEBP"):
            return "rw" in line or " rw" in line
    return False


THUMB_EXT = "webp" if webp_supported() else "jpg"


def make_thumb(src: Path, dst: Path, clean: bool) -> None:
    if not clean and dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
        return
    dst.parent.mkdir(parents=True, exist_ok=True)

    if Image is not None:
        with Image.open(src) as im:
            im = ImageOps.exif_transpose(im)
            im.thumbnail((THUMB_WIDTH, THUMB_WIDTH), Image.LANCZOS)
            if im.mode not in ("RGB", "RGBA"):
                im = im.convert("RGBA" if im.mode in ("P", "LA", "PA") else "RGB")
            if THUMB_EXT == "webp":
                im.save(dst, "WEBP", quality=78, method=4)
            else:
                im.convert("RGB").save(dst, "JPEG", quality=82, optimize=True)
        return

    quality = "78" if THUMB_EXT == "webp" else "82"
    subprocess.run(
        [IM, f"{src}[0]", "-auto-orient", "-thumbnail", f"{THUMB_WIDTH}x{THUMB_WIDTH}>",
         "-strip", "-quality", quality, str(dst)],
        check=True, capture_output=True,
    )


CSS = """\
:root {
  --bg: #0a0a0d;
  --surface: #131319;
  --line: #24242e;
  --text: #ececf2;
  --muted: #8f8f9e;
  --accent: #a6e3a1;
}

* { box-sizing: border-box; }

html { color-scheme: dark; scrollbar-color: #33333f var(--bg); }

body {
  margin: 0;
  padding: 40px 20px 80px;
  background: var(--bg);
  color: var(--text);
  font: 15px/1.6 "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
  -webkit-font-smoothing: antialiased;
}

.wrap { width: min(1240px, 100%); margin: 0 auto; }

header {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  justify-content: space-between;
  gap: 8px 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--line);
  margin-bottom: 28px;
}

h1 {
  margin: 0;
  font-size: clamp(1.4rem, 3.4vw, 2rem);
  font-weight: 600;
  letter-spacing: -0.02em;
}

h1 a { color: inherit; text-decoration: none; }

.sub { margin: 0; color: var(--muted); font-size: 0.82rem; }
.sub a { color: var(--accent); text-decoration: none; }
.sub a:hover { text-decoration: underline; }

.grid {
  columns: 4 250px;
  column-gap: 12px;
}

.grid a {
  display: block;
  margin: 0 0 12px;
  break-inside: avoid;
  content-visibility: auto;
  contain-intrinsic-size: 250px 160px;
  border: 1px solid var(--line);
  border-radius: 8px;
  overflow: hidden;
  background: var(--surface);
}

.grid img {
  width: 100%;
  height: auto;
  display: block;
  transition: opacity 0.2s ease;
}

.grid a:hover img, .grid a:focus-visible img { opacity: 0.82; }

footer {
  margin-top: 48px;
  padding-top: 18px;
  border-top: 1px solid var(--line);
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 8px;
  color: var(--muted);
  font-size: 0.78rem;
}

footer a { color: var(--muted); }

/* lightbox */
.lightbox {
  position: fixed;
  inset: 0;
  z-index: 10;
  display: none;
  place-items: center;
  padding: 3vmin;
  background: rgba(4, 4, 8, 0.94);
  backdrop-filter: blur(3px);
}

.lightbox[open] { display: grid; }

.lightbox img {
  max-width: 100%;
  max-height: 88vh;
  object-fit: contain;
  border-radius: 6px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
}

.lightbox .bar {
  position: fixed;
  inset: auto 0 0 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 18px;
  padding: 14px;
  font-size: 0.8rem;
  color: var(--muted);
}

.lightbox button {
  font: inherit;
  color: var(--text);
  background: #1b1b24;
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 6px 14px;
  cursor: pointer;
}

.lightbox button:hover { border-color: var(--accent); color: var(--accent); }

.lightbox .spinner {
  position: absolute;
  width: 28px;
  height: 28px;
  border: 2px solid var(--line);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

@media (prefers-reduced-motion: reduce) {
  * { transition: none !important; animation: none !important; }
}
"""

JS = """\
(() => {
  const box = document.getElementById('lightbox');
  if (!box) return;
  const img = box.querySelector('img');
  const spinner = box.querySelector('.spinner');
  const counter = box.querySelector('.counter');
  const open = box.querySelector('.open');
  const links = [...document.querySelectorAll('.grid a')];
  let index = 0;

  const show = (i) => {
    index = (i + links.length) % links.length;
    const link = links[index];
    spinner.hidden = false;
    img.style.visibility = 'hidden';
    img.src = link.dataset.full;
    img.alt = link.dataset.name;
    counter.textContent = `${index + 1} / ${links.length}`;
    open.href = link.dataset.full;
    box.setAttribute('open', '');
    document.body.style.overflow = 'hidden';
  };

  const close = () => {
    box.removeAttribute('open');
    img.removeAttribute('src');
    document.body.style.overflow = '';
  };

  img.addEventListener('load', () => {
    spinner.hidden = true;
    img.style.visibility = 'visible';
  });

  links.forEach((link, i) => link.addEventListener('click', (e) => {
    if (e.metaKey || e.ctrlKey || e.shiftKey) return;
    e.preventDefault();
    show(i);
  }));

  box.querySelector('.prev').addEventListener('click', () => show(index - 1));
  box.querySelector('.next').addEventListener('click', () => show(index + 1));
  box.querySelector('.close').addEventListener('click', close);
  box.addEventListener('click', (e) => { if (e.target === box) close(); });
  addEventListener('keydown', (e) => {
    if (!box.hasAttribute('open')) return;
    if (e.key === 'Escape') close();
    if (e.key === 'ArrowLeft') show(index - 1);
    if (e.key === 'ArrowRight') show(index + 1);
  });
})();
"""

LIGHTBOX = """\
<div class="lightbox" id="lightbox">
  <div class="spinner"></div>
  <img alt="">
  <div class="bar">
    <button class="prev" aria-label="previous">←</button>
    <span class="counter"></span>
    <a class="open" target="_blank" rel="noopener">original ↗</a>
    <button class="next" aria-label="next">→</button>
    <button class="close" aria-label="close">close</button>
  </div>
</div>"""


def page(title: str, body: str, script: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="color-scheme" content="dark">
<link rel="preconnect" href="https://cdn.jsdelivr.net">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fontsource/jetbrains-mono@5.0.0/index.min.css">
<link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="wrap">
{body}
<footer>
  <span>All wallpapers belong to their original creators.</span>
  <span><a href="https://github.com/{USER}/{REPO}">github.com/{USER}/{REPO}</a></span>
</footer>
</div>
{script}
</body>
</html>
"""


def build_index(images: list[str], sizes: dict[str, tuple[int, int]]) -> str:
    size = sum((IMAGES / n).stat().st_size for n in images) / 1048576
    shots = []
    for image in images:
        thumb = f"{Path(image).stem}.{THUMB_EXT}"
        w, h = sizes.get(image, (1920, 1080))
        full = f"{RAW}/{image}"
        shots.append(
            f'''  <a href="{html.escape(full)}" data-full="{html.escape(full)}" data-name="{html.escape(image)}">
    <img src="thumbs/{thumb}" width="{w}" height="{h}" alt="{html.escape(image)}" loading="lazy" decoding="async">
  </a>'''
        )
    body = f'''<header>
  <h1>wallpapers</h1>
  <p class="sub">{len(images)} images &middot; {size:.0f} MB &middot; <a href="https://github.com/{USER}/{REPO}">github</a></p>
</header>

<main class="grid">
{os.linesep.join(shots)}
</main>
{LIGHTBOX}
'''
    return page("Wallpapers", body, f"<script>{JS}</script>")


def check_site() -> list[str]:
    """Fail the build if a page points at a file that was not generated."""
    missing = []
    for html_page in SITE.rglob("index.html"):
        for ref in re.findall(r'(?:src|href)="([^"]+)"', html_page.read_text(encoding="utf-8")):
            if ref.startswith(("http://", "https://", "#", "mailto:")):
                continue
            if not (html_page.parent / ref).resolve().exists():
                missing.append(f"{html_page.relative_to(SITE)}: {ref}")
    return missing


def main() -> int:
    if Image is None and not IM:
        print("need Pillow (pip install pillow) or ImageMagick", file=sys.stderr)
        return 1

    clean = "--clean" in sys.argv
    if SITE.exists():
        if clean:
            shutil.rmtree(SITE)
        else:
            for entry in SITE.iterdir():
                if entry.name == "thumbs":
                    continue
                shutil.rmtree(entry) if entry.is_dir() else entry.unlink()
    SITE.mkdir(exist_ok=True)

    images = image_files()
    for image in images:
        make_thumb(IMAGES / image, THUMBS / f"{Path(image).stem}.{THUMB_EXT}", clean)

    sizes = dimensions([IMAGES / image for image in images])

    (SITE / "styles.css").write_text(CSS, encoding="utf-8")
    (SITE / "index.html").write_text(build_index(images, sizes), encoding="utf-8")
    (SITE / ".nojekyll").write_text("", encoding="utf-8")

    missing = check_site()
    if missing:
        print("broken links:", file=sys.stderr)
        for line in missing[:20]:
            print("  " + line, file=sys.stderr)
        return 1

    print(f"built {len(images)} images, {len(images)} thumbnails ({THUMB_EXT}) -> {SITE}")
    print("preview: python3 -m http.server -d _site 8000")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
