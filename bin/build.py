#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build.py — turns book.yaml + pages.yaml + art/*.png into a finished PDF.

Usage:
    python3 build.py                       # default language
    python3 build.py --lang ru             # a specific language
    python3 build.py --all                 # every language in book.yaml
    python3 build.py --dir path/to/book    # a different book folder

Reads:
    book.yaml        layout + one typography block per language
    pages.yaml       page structure (image, shot, angle, scene) — no text
    text/<lang>.yaml the story text and title for that language
    art/*.png        the illustrations

To make a new book: copy this whole folder, replace pages.yaml, text/ and
art/, then run this script.

IMAGE PLACEMENT
---------------
Three modes, set per page (or globally) via `image_mode`:

  fit_width (default) — the illustration spans the full width of its half of
                    the spread. Nothing is cropped on any side. Because the
                    art is taller in proportion than the panel, the leftover
                    space falls only at the top and bottom, filled with the
                    page tint. No side bands, no amputated hands or paws.

  fill            — covers the panel edge to edge and crops the overflow.
                    `crop_anchor` picks which edge survives (0.0 left,
                    0.5 centre, 1.0 right). Only for pages you have checked.

  fit             — whole image scaled to fit inside the panel, leaving space
                    on all four sides. Puts a visible border around the art.
"""

import sys
import os

def _need(module, package):
    try:
        return __import__(module)
    except ModuleNotFoundError:
        raise SystemExit(
            f"\nMissing dependency: {package}\n\n"
            f"Install everything this repo needs:\n\n"
            f"    python3 -m venv .venv\n"
            f"    source .venv/bin/activate\n"
            f"    pip install -r requirements.txt\n\n"
            f"Then run the command again. On macOS, `pip install` without a\n"
            f"virtual environment is often blocked by the system Python;\n"
            f"the venv above avoids that.\n")


_need("yaml", "PyYAML")
_need("reportlab", "reportlab")
_need("PIL", "pillow")

import yaml
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.utils import ImageReader
from PIL import Image

GS = "/usr/share/fonts/type1/gsfonts"
GF = "/usr/share/fonts/truetype/google-fonts"

FONT_LIBRARY = {
    "CenturySchoolbook": ("type1", f"{GS}/c059013l.afm", f"{GS}/c059013l.pfb"),
    "Bookman":           ("type1", f"{GS}/b018012l.afm", f"{GS}/b018012l.pfb"),
    "Palatino":          ("type1", f"{GS}/p052003l.afm", f"{GS}/p052003l.pfb"),
    "Lora":              ("ttf", f"{GF}/Lora-Variable.ttf"),
    "Caladea":           ("ttf", "/usr/share/fonts/truetype/crosextra/Caladea-Regular.ttf"),
}


def register_font(alias):
    kind, *paths = FONT_LIBRARY[alias]
    if kind == "type1":
        afm, pfb = paths
        face = pdfmetrics.EmbeddedType1Face(afm, pfb)
        pdfmetrics.registerTypeFace(face)
        pdfmetrics.registerFont(pdfmetrics.Font(alias, face.name, "WinAnsiEncoding"))
    else:
        (ttf,) = paths
        pdfmetrics.registerFont(TTFont(alias, ttf))


def wrap_measured(text, font, size, maxw):
    """Word-wrap on real glyph widths, so a font or language swap can't
    overrun the column."""
    lines, cur = [], ""
    for w in text.split():
        trial = (cur + " " + w).strip()
        if pdfmetrics.stringWidth(trial, font, size) <= maxw:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def hex_to_rgb255(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def sample_rgb(path, sample_edge):
    im = Image.open(path).convert("RGB")
    iw, ih = im.size
    strip = im.crop((int(iw * sample_edge), 0, iw, ih)).resize((24, 24))
    px = list(strip.getdata())
    n = len(px)
    return (sum(p[0] for p in px) / n,
            sum(p[1] for p in px) / n,
            sum(p[2] for p in px) / n)


def lift_to_paper(rgb, lift, paper_rgb):
    pr, pg, pb = paper_rgb
    r, g, b = rgb
    mix = lambda c, pc: (c + (pc - c) * lift) / 255.0
    return Color(mix(r, pr), mix(g, pg), mix(b, pb))


def relative_luminance(color):
    return 0.2126 * color.red + 0.7152 * color.green + 0.0722 * color.blue


def enforce_floor(color, paper_rgb, floor):
    """Keep the text panel light enough to read dark ink on. A very dark
    illustration would otherwise drag its panel down with it."""
    r, g, b = color.red * 255, color.green * 255, color.blue * 255
    pr, pg, pb = paper_rgb
    out = Color(r / 255, g / 255, b / 255)
    guard = 0
    while relative_luminance(out) < floor and guard < 60:
        r, g, b = r + (pr - r) * 0.06, g + (pg - g) * 0.06, b + (pb - b) * 0.06
        out = Color(r / 255, g / 255, b / 255)
        guard += 1
    return out


def resolve_tint(cfg, page_paths, cover_path, paper_rgb, paper_color):
    """Returns ({path -> Color}, cover_color).

    mode 'per_page' (default): every spread takes its cast from its own
    illustration, so the text side continues that page's colour. The cover
    is sampled from the cover art, not left white.

    mode 'uniform': one colour averaged across the book, used everywhere.
    """
    all_paths = page_paths + [cover_path]
    if not cfg.get("enabled"):
        return {p: paper_color for p in all_paths}, paper_color

    lift = cfg.get("lift", 0.86)
    edge = cfg.get("sample_edge", 0.72)
    mode = cfg.get("mode", "per_page")
    floor = cfg.get("luminance_floor", 0.80)

    if cfg.get("fixed"):
        c = HexColor(cfg["fixed"])
        return {p: c for p in all_paths}, c

    def tint_for(path):
        c = lift_to_paper(sample_rgb(path, edge), lift, paper_rgb)
        return enforce_floor(c, paper_rgb, floor)

    if mode == "uniform":
        samples = [sample_rgb(p, edge) for p in all_paths]
        n = len(samples)
        avg = tuple(sum(s[i] for s in samples) / n for i in range(3))
        c = enforce_floor(lift_to_paper(avg, lift, paper_rgb), paper_rgb, floor)
        return {p: c for p in all_paths}, c

    tints = {p: tint_for(p) for p in all_paths}
    return tints, tints[cover_path]


def place_image(c, path, x0, half_w, page_h, mode="fit_width", anchor=0.5):
    im = Image.open(path)
    iw, ih = im.size

    if mode == "fit_width":
        # Span the panel's full width; nothing is cropped horizontally.
        # Any leftover height shows as bands at the top and bottom only.
        scale = half_w / iw
        nw, nh = half_w, ih * scale
        if nh > page_h:          # taller than the panel: clip evenly, no side loss
            c.saveState()
            p = c.beginPath()
            p.rect(x0, 0, half_w, page_h)
            c.clipPath(p, stroke=0)
            c.drawImage(ImageReader(im), x0, -(nh - page_h) / 2, nw, nh, mask=None)
            c.restoreState()
        else:
            c.drawImage(ImageReader(im), x0, (page_h - nh) / 2, nw, nh, mask=None)
    elif mode == "fill":
        scale = max(half_w / iw, page_h / ih)
        nw, nh = iw * scale, ih * scale
        c.saveState()
        p = c.beginPath()
        p.rect(x0, 0, half_w, page_h)
        c.clipPath(p, stroke=0)
        c.drawImage(ImageReader(im), x0 - (nw - half_w) * anchor,
                    -(nh - page_h) / 2, nw, nh, mask=None)
        c.restoreState()
    else:                                       # fit — border on all sides
        scale = min(half_w / iw, page_h / ih)
        nw, nh = iw * scale, ih * scale
        c.drawImage(ImageReader(im), x0 + (half_w - nw) / 2,
                    (page_h - nh) / 2, nw, nh, mask=None)


def build(book_dir, lang=None):
    book_dir = os.path.abspath(book_dir)
    with open(os.path.join(book_dir, "book.yaml"), encoding="utf-8") as f:
        book = yaml.safe_load(f)
    with open(os.path.join(book_dir, "pages.yaml"), encoding="utf-8") as f:
        pages = yaml.safe_load(f)["pages"]

    lang = lang or book.get("default_language", "en")
    langs = book["languages"]
    if lang not in langs:
        raise SystemExit(f"language '{lang}' not in book.yaml "
                         f"(have: {', '.join(langs)})")
    cfg = langs[lang]

    tpath = os.path.join(book_dir, "text", f"{lang}.yaml")
    with open(tpath, encoding="utf-8") as f:
        tdoc = yaml.safe_load(f)
    title = tdoc["title"]
    texts = tdoc["pages"]

    missing = [pg["n"] for pg in pages if pg["n"] not in texts]
    if missing:
        raise SystemExit(f"text/{lang}.yaml has no text for page(s): "
                         f"{', '.join(map(str, missing))}")

    art = os.path.join(book_dir, "art")
    font_alias = cfg["font"]
    register_font(font_alias)

    W, H = book["page"]["size"]
    HALF = W / 2
    m_text = book["page"]["margin_text"]
    m_right = book["page"]["margin_right"]
    PAPER = HexColor(book["page"]["paper"])
    PAPER_RGB = hex_to_rgb255(book["page"]["paper"])
    INK = HexColor(book["page"]["ink"])
    FAINT = HexColor(book["page"]["faint"])

    title_size = cfg["title_size"]
    body_size = cfg["body_size"]
    leading = cfg["leading"]
    author = book.get("author", "")
    default_mode = book.get("image_mode", "fit_width")

    cover = book["cover"]
    cover_path = os.path.join(art, cover["image"])
    page_paths = [os.path.join(art, pg["image"]) for pg in pages]

    tints, cover_tint = resolve_tint(book.get("tint", {}),
                                     page_paths, cover_path, PAPER_RGB, PAPER)

    out_path = os.path.join(book_dir, cfg["output"])
    c = canvas.Canvas(out_path, pagesize=(W, H))

    # --- cover: same background colour as every interior spread ---
    c.setFillColor(cover_tint)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    place_image(c, cover_path, 0, HALF, H,
                mode=cover.get("image_mode", default_mode),
                anchor=cover.get("crop_anchor", 0.5))
    c.setFillColor(INK)
    c.setFont(font_alias, title_size)
    c.drawString(HALF + m_text, H / 2 - 8, title)
    c.showPage()

    # --- interior spreads ---
    for pg in pages:
        img_path = os.path.join(art, pg["image"])
        c.setFillColor(tints[img_path])
        c.rect(0, 0, W, H, stroke=0, fill=1)
        place_image(c, img_path, 0, HALF, H,
                    mode=pg.get("image_mode", default_mode),
                    anchor=pg.get("crop_anchor", 0.5))

        if author:
            c.setFillColor(FAINT)
            c.setFont(font_alias, 7.5)
            c.drawRightString(W - m_right, H - 46, " ".join(author.upper()))

        c.setFillColor(INK)
        c.setFont(font_alias, body_size)
        maxw = W - m_right - (HALF + m_text)
        para_gap = leading * 0.45

        # Blank lines in the YAML are paragraph breaks — dialogue needs them.
        paragraphs = [" ".join(blk.split())
                      for blk in str(texts[pg["n"]]).split("\n\n")
                      if blk.strip()]
        blocks = [wrap_measured(pa, font_alias, body_size, maxw)
                  for pa in paragraphs]

        total = (sum(len(b) for b in blocks) * leading
                 + max(0, len(blocks) - 1) * para_gap)
        y = H / 2 + total / 2 - leading / 2
        for bi, block in enumerate(blocks):
            for ln in block:
                c.drawString(HALF + m_text, y, ln)
                y -= leading
            if bi < len(blocks) - 1:
                y -= para_gap

        c.setFillColor(FAINT)
        c.setFont(font_alias, body_size - 4.5)
        c.drawRightString(W - m_right, 42, str(pg["n"]))
        c.showPage()

    c.save()
    print(f"Built [{lang}] {out_path}  ({os.path.getsize(out_path)//1024} KB, "
          f"{len(pages)+1} pages, font={font_alias}, mode={default_mode})")


if __name__ == "__main__":
    argv = sys.argv[1:]
    target = os.path.dirname(os.path.abspath(__file__))
    if "--dir" in argv:
        target = argv[argv.index("--dir") + 1]

    with open(os.path.join(target, "book.yaml"), encoding="utf-8") as f:
        _book = yaml.safe_load(f)

    if "--all" in argv:
        for _lang in _book["languages"]:
            build(target, _lang)
    elif "--lang" in argv:
        build(target, argv[argv.index("--lang") + 1])
    else:
        build(target)
