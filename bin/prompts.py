#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
prompts.py — assembles image prompts from three files that never overlap:

    style.yaml   craft rules. No names, no places, no colours. Reusable in any
                 book, any setting. Contains placeholders, not facts.
    story_world.yaml   this story's cast, settings and continuity rules.
    pages.yaml   per page: which setting, which camera, and the scene.

This file decides only the ORDER sections appear in. To change what the rules
say, edit style.yaml. To change who and where, edit story_world.yaml.

Usage:
    python3 bin/prompts.py --dir books/<book> [command]

Commands:
    (none)          validate, then print every page prompt
    5               print page 5 only
    --check         validate only; exit 1 on failure
    --out DIR       write one .md file per page into DIR
    --charsheet         sheet prompt for the whole cast together
    --charsheet <id>    sheet prompt for one character, using their own
                        likeness reference from series/<series>/cast.yaml
    --plate NAME    the setting-plate prompt for one setting
    --styles        list the style packs available in styles/
    --swatch PACK   the neutral style-swatch prompt for a pack

The book's style.yaml names a `pack:`; this merges styles/<pack>/pack.yaml
over it, so `style` and `edges` travel with the chosen medium.
"""

import sys
import os
import textwrap

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

import yaml


REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STYLES = os.path.join(REPO, "styles")


def list_packs():
    if not os.path.isdir(STYLES):
        return []
    return sorted(d for d in os.listdir(STYLES)
                  if os.path.isfile(os.path.join(STYLES, d, "pack.yaml")))


def load_pack(name):
    path = os.path.join(STYLES, name, "pack.yaml")
    if not os.path.isfile(path):
        raise SystemExit(f"style pack '{name}' not found in styles/ "
                         f"(have: {', '.join(list_packs()) or 'none'})")
    with open(path, encoding="utf-8") as f:
        pack = yaml.safe_load(f)
    pack["_dir"] = os.path.join(STYLES, name)
    pack["_name"] = name
    return pack


def load_series_cast(world):
    """Resolve the book's `cast: [ids]` against series/<series>/cast.yaml.
    One character, one definition, shared by every book in the series."""
    name = world.get("series")
    if not name:
        return world.get("cast", [])          # legacy: cast inline in the book
    path = os.path.join(REPO, "series", name, "cast.yaml")
    if not os.path.isfile(path):
        raise SystemExit(f"series cast not found: {path}")
    with open(path, encoding="utf-8") as f:
        book_of_people = yaml.safe_load(f)["cast"]
    out = []
    for cid in world.get("cast", []):
        if cid not in book_of_people:
            raise SystemExit(
                f"character '{cid}' not in series/{name}/cast.yaml "
                f"(have: {', '.join(book_of_people)})")
        entry = dict(book_of_people[cid])
        entry["id"] = cid
        entry["_series"] = name
        out.append(entry)
    return out


BOOK_DIR = ""


def load(book_dir):
    global BOOK_DIR
    BOOK_DIR = os.path.relpath(os.path.abspath(book_dir), REPO)
    def y(name):
        with open(os.path.join(book_dir, name), encoding="utf-8") as f:
            return yaml.safe_load(f)
    try:
        pages = y("pages.yaml")["pages"] or []
    except FileNotFoundError:
        pages = []          # --charsheet and --plate run before scenes exist
    style = y("style.yaml")
    world = y("story_world.yaml")
    world["cast"] = load_series_cast(world)

    packname = style.get("pack")
    if packname:
        pack = load_pack(packname)
        # the pack owns the medium: style + edges travel together
        for k in ("style", "edges"):
            if pack.get(k):
                style[k] = pack[k]
        style["_pack"] = pack
    return pages, style, world


PASTE = "-" * 26 + "  PASTE FROM HERE  " + "-" * 27


def header(title, attach, save=None):
    """Operator instructions. None of this goes into the chat window — the
    model has no filesystem and a repo path means nothing to it."""
    lines = ["=" * 74, title, "=" * 74, "FOR YOU, NOT FOR THE MODEL"]
    for label, items in (("drag in", attach), ("save as", save)):
        if not items:
            continue
        items = [items] if isinstance(items, str) else items
        for i, it in enumerate(items):
            lines.append(f"  {label + ':' if i == 0 else '':9} {it}")
    return "\n".join(lines + [PASTE, ""])


def plate_reference(style, world):
    """Plates prefer the pack swatch even when the book overrides the style
    reference with a character sheet. A sheet is a figure on white: it says
    nothing about how this style paints distance, foliage or sky, so a plate
    anchored on one falls back to the model's default landscape look."""
    pack = style.get("_pack")
    if pack:
        swatch = os.path.join("styles", pack["_name"],
                              pack.get("reference", "reference.png"))
        if os.path.exists(os.path.join(REPO, swatch)):
            return swatch, ""
    ref, _ = named_reference(style, world)
    return ref, ("  <-- NOT A LANDSCAPE REFERENCE. Generate the pack swatch "
                 "first:\n            bin/prompts.py --swatch <pack>\n"
                 "            A plate anchored on a character sheet has "
                 "nothing to copy for trees,\n            distance or sky, "
                 "and will come out in the model's default\n            "
                 "landscape style rather than yours.")


def named_reference(style, world):
    """The style reference as it should appear inside a prompt body: the actual
    filename, so a pasted prompt still says which image to attach."""
    ref = reference_path(style, world)
    missing = "" if os.path.exists(os.path.join(REPO, ref)) else \
        "  <-- THIS FILE DOES NOT EXIST YET. Generate it first: " \
        "bin/prompts.py --swatch <pack>"
    return ref, missing


def reference_path(style, world):
    """Where the style reference lives, as a path from the repo root: the
    pack's swatch unless the book overrides it with a file of its own."""
    override = world.get("style_reference_image")
    pack = style.get("_pack")
    if pack and override in (None, "reference.png"):
        return os.path.join("styles", pack["_name"],
                            pack.get("reference", "reference.png"))
    return override or "reference.png"


def flat(v):
    return " ".join(str(v).split())


def para(v):
    return textwrap.fill(flat(v), 78)


def bullets(items):
    return "\n".join(
        textwrap.fill(flat(i), 78, initial_indent="- ", subsequent_indent="  ")
        for i in items)


# --------------------------------------------------------------------------
# world helpers
# --------------------------------------------------------------------------

def cast_phrase(world, ids=None):
    """'Orea, a girl of four, and Whoof-Whoof, a soft beige stuffed toy dog'.
    Restricted to `ids` when given — a page must never be told about a
    character whose sheet is not attached to it."""
    bits = []
    for c in world["cast"]:
        if ids is not None and c["id"] not in ids:
            continue
        # The WHOLE description. Truncating to the first sentence once put a
        # child in pyjamas in a public park, because "out of doors she wears a
        # coat and shoes" sat after the first full stop and never arrived.
        d = flat(c["description"]).strip().rstrip(".")
        if d.split(" ")[0] in ("A", "An", "The"):
            d = d[0].lower() + d[1:]
        bits.append(f"{c['name']} — {d}")
    return "\n\n".join(bits)


def cast_rules(world, ids=None):
    out = []
    for c in world["cast"]:
        if ids is not None and c["id"] not in ids:
            continue
        out.extend(c.get("rules", []))
        if c.get("constant") and not c.get("rules"):
            out.append(f"{c['name']} appears in every illustration.")
    return out


def setting_for(pg, world):
    name = pg.get("setting")
    settings = world.get("settings", {})
    if name not in settings:
        raise SystemExit(f"page {pg.get('n')}: setting '{name}' not in "
                         f"story_world.yaml (have: {', '.join(settings)})")
    return name, settings[name]


# --------------------------------------------------------------------------

def validate(pages, style, world):
    shots, angles = style["shots"], style["angles"]
    fields = [f[0] for f in style["scene_fields"]]
    settings = world.get("settings", {})
    errors, warnings, heavy = [], [], []

    for i, pg in enumerate(pages):
        n = pg.get("n")
        shot, angle = pg.get("shot"), pg.get("angle")

        if shot not in shots:
            errors.append(f"page {n}: unknown shot '{shot}'")
        if angle not in angles:
            errors.append(f"page {n}: unknown angle '{angle}'")
        if pg.get("setting") not in settings:
            errors.append(f"page {n}: setting '{pg.get('setting')}' not in "
                          f"story_world.yaml (have: {', '.join(settings)})")

        if i > 0:
            prev = pages[i - 1]
            same_place = pg.get("setting") == prev.get("setting")
            if same_place and shot == prev.get("shot") and angle == prev.get("angle"):
                errors.append(
                    f"page {n}: same setting, shot AND angle as page "
                    f"{prev.get('n')}. Repeating the shot is fine — change the "
                    f"angle.")

        scene = pg.get("scene")
        if not isinstance(scene, dict):
            errors.append(f"page {n}: scene must be a mapping of {fields}")
            continue

        page_ids = pg.get("characters") or [c["id"] for c in world["cast"]]
        lead = next((c["id"] for c in world["cast"] if c.get("lead")), None)
        companions = [c["id"] for c in world["cast"]
                      if c["id"] in page_ids and c["id"] != lead
                      and c.get("companion_of")]
        optional = set() if companions else {"companion"}
        missing = [f for f in fields if f not in scene and f not in optional]
        if missing:
            warnings.append(f"page {n}: scene missing {', '.join(missing)}")

        ids = pg.get("characters") or [c["id"] for c in world["cast"]]
        sheet_ids = pg["sheets"] if "sheets" in pg else page_ids
        n_sheets = len({c["sheet"] for c in world["cast"]
                        if c["id"] in sheet_ids and c.get("sheet")})
        n_attach = n_sheets + 2
        if n_attach >= 5:
            heavy.append((n, n_attach))

        sname_v, setting_v = setting_for(pg, world)
        outfit = wardrobe_for(pg, setting_v, world)
        if outfit is None:
            warnings.append(
                f"page {n}: no wardrobe set. Add `wardrobe: <name>` to "
                f"story_world.yaml so the model is told what to paint instead "
                f"of copying the outfit on the character sheet.")
        else:
            for c in world["cast"]:
                if c["id"] in page_ids and c.get("wardrobe") is not None \
                        and outfit not in c["wardrobe"]:
                    errors.append(
                        f"page {n}: {c['name']} has no '{outfit}' outfit in "
                        f"cast.yaml (has: "
                        f"{', '.join(c['wardrobe']) or 'none'}).")

        banned = ("knows", "remembers", "decides", "tomorrow", "yesterday",
                  "thinks", "wonders")
        for k, v in scene.items():
            low = flat(v).lower()
            for b in banned:
                if b in low:
                    warnings.append(
                        f"page {n}: scene.{k} contains '{b}' — narration, not "
                        f"something visible in frame.")
    for c in world["cast"]:
        r = c.get("reference")
        if r and not os.path.exists(os.path.join(REPO, r)):
            errors.append(f"cast: {c['name']}'s reference does not exist: {r}")
        sh = c.get("sheet")
        if sh:
            shp = os.path.join("series", c["_series"], "charsheet", sh)
            if not os.path.exists(os.path.join(REPO, shp)):
                warnings.append(
                    f"cast: {c['name']}'s sheet is not generated yet: {shp}"
                    f"   (bin/prompts.py --dir <book> --charsheet {c['id']})")

    if heavy:
        listed = ", ".join(f"{n} ({k})" for n, k in heavy)
        warnings.append(
            f"{len(heavy)} page(s) attach five or more images: {listed}. "
            f"Watch the faces there. Two ways down: give the page a `sheets:` "
            f"list naming only the characters whose faces are in frame, or "
            f"drop the previous-page attachment — the sheets and the plate "
            f"still carry identity and world; the chain only carries style.")
    return errors, warnings


def render_scene(scene, style):
    out = []
    for key, label in style["scene_fields"]:
        if key in scene:
            out.append(textwrap.fill(f"{label}: {flat(scene[key])}", 78,
                                     subsequent_indent="    "))
    return "\n".join(out)


def wardrobe_for(pg, setting, world):
    """Which named outfit this page uses. Page beats setting beats book —
    a book is usually one season, a setting occasionally differs (indoors in
    winter), a single page rarely."""
    return (pg.get("wardrobe") or setting.get("wardrobe")
            or world.get("wardrobe"))


def wearing(world, ids, outfit):
    """One line per character in frame saying what they have on. Without this
    the model dresses everyone from the character sheet, which shows exactly
    one outfit and is usually the wrong one."""
    out = []
    for c in world["cast"]:
        if c["id"] not in ids:
            continue
        w = c.get("wardrobe") or {}
        if outfit and outfit in w:
            out.append(f"{c['name']} is wearing {flat(w[outfit]).rstrip('.')}.")
    return out


def role_characters(style, world, ids, n_sheets):
    """The characters block: an intro line, then one indented paragraph per
    character. Joining them into a single sentence ran their descriptions
    together with no punctuation between."""
    tmpl = style["image_roles"]["characters"]
    intro, _, tail = tmpl.partition("{characters}")
    if n_sheets > 1:
        intro = intro.replace("The character sheet shows",
                              "The character sheets show")
    lines = [flat(intro).strip()]
    for c in world["cast"]:
        if c["id"] not in ids:
            continue
        d = flat(c["description"]).strip().rstrip(".")
        lines.append(textwrap.fill(f"- {c['name']} — {d}.", 78,
                                   subsequent_indent="  "))
    tail = flat(tail).strip().lstrip(".,; ").strip()
    if tail:
        lines.append("")
        lines.append(para(tail[0].upper() + tail[1:]))
    return "\n".join(lines)


def render_page(pg, style, world, prev_n):
    s = style
    sname, setting = setting_for(pg, world)

    # Which characters are in this page? Default: everyone in the book.
    ids = pg.get("characters") or [c["id"] for c in world["cast"]]
    sheet_ids = pg["sheets"] if "sheets" in pg else ids
    sheets, seen = [], set()
    for c in world["cast"]:
        if c["id"] in sheet_ids and c.get("sheet") and c["sheet"] not in seen:
            seen.add(c["sheet"])
            sheets.append(f"series/{c['_series']}/charsheet/{c['sheet']}")

    art = lambda f: os.path.join(BOOK_DIR, "art", f)
    attach = sheets + [art(setting["plate"])]
    if prev_n is not None:
        attach.append(art(f"page_{prev_n:02d}.png"))

    roles = [
        role_characters(s, world, ids, len(sheets)),
        para(s["image_roles"]["setting"].format(
            setting=flat(setting["description"]).rstrip("."))),
        para(s["image_roles"]["previous_page"] if prev_n is not None
             else s["image_roles"]["no_previous"]),
    ]

    constants = list(setting.get("constants", [])) + cast_rules(world, ids)
    nevers = list(s["never"]) + list(setting.get("never", []))

    parts = [
        header(f"PAGE {pg['n']}   setting: {sname}   shot: {pg['shot']}   "
               f"angle: {pg['angle']}",
               attach, art(pg["image"])),
        "Draw one illustration for a children's picture book.",
        para(s["aspect"]),
        "",
        "IMAGE ROLES",
        "\n\n".join(roles),
        "",
        para(s["shots"][pg["shot"]]),
        para(s["angles"][pg["angle"]]),
        "",
        "COMPOSITION",
        para(s["composition"]),
        "",
        "EDGES",
        para(s["edges"]),
        "",
    ]

    outfit = wardrobe_for(pg, setting, world)
    dressed = wearing(world, ids, outfit)
    if dressed:
        parts += ["WEARING",
                  bullets(dressed) + "\n\nThe character sheet may show a "
                  "different outfit. This page overrides it. Faces, hair, "
                  "build and colouring still come from the sheet exactly.",
                  ""]

    if constants:
        parts += ["MUST NOT CHANGE", bullets(constants), ""]

    # Global continuity, then anything belonging to this page's setting only.
    # A note about the dentist's room must not appear on a page in the park.
    for src in (world.get("continuity", {}), setting.get("continuity", {})):
        for label, text in src.items():
            parts += [label.upper(), para(text), ""]

    parts += [
        "STYLE",
        para(s["style"]),
        "",
        "NEVER",
        bullets(nevers),
        "",
        "THE SCENE FOR THIS PAGE",
        render_scene(pg["scene"], s),
    ]
    return "\n".join(parts)


def render_one_charsheet(style, world, cid):
    who = next((c for c in world["cast"] if c["id"] == cid), None)
    if who is None:
        raise SystemExit(f"'{cid}' is not in this book's cast "
                         f"(have: {', '.join(c['id'] for c in world['cast'])})")
    ref = who.get("reference")
    numbered = "\n".join(f"{i}. {who['name']}, {v}."
                          for i, v in enumerate(who.get("sheet_views", []), 1))

    if ref:
        # Two jobs, and they are not always the same image. The likeness
        # reference may be older art in an earlier palette; the style swatch is
        # current. Attaching only the likeness quietly imports its style too.
        style_ref, missing = named_reference(style, world)
        attach = [f"{ref}   (LIKENESS — who this is)"]
        role = ("One attached image is an existing illustration of this "
                "character — the LIKENESS reference. Copy their face, hair, "
                "build, colouring and markings from it exactly; this is the "
                "same person. Do not copy its background, its composition or "
                "any other character in it.")
        if os.path.normpath(style_ref) != os.path.normpath(ref):
            attach.append(f"{style_ref}   (STYLE — how it is painted){missing}")
            role += (" A second attached image is the STYLE reference. Take "
                     "the medium, the paper texture, the palette, the line "
                     "quality and the level of detail from THAT one, not from "
                     "the likeness reference, whose colours may be stronger "
                     "than this book's. Where the two disagree about how "
                     "something is painted, the style reference wins; where "
                     "they disagree about who this person is, the likeness "
                     "reference wins.")
    else:
        # Nobody has drawn this character yet. Invent the face, but do not
        # invent the style: attach whatever the book uses as its look anchor,
        # or every page this character is on will be painted differently from
        # the rest of the book.
        _ref, _missing = named_reference(style, world)
        attach = f"{_ref}   (style reference only){_missing}"
        role = ("One attached image is a STYLE REFERENCE. "
                + style["style_reference"]
                + " This character has never been "
                "drawn. Invent their face and build, guided only by the "
                "description below — do not copy the face or the clothing of "
                "anyone in the attached image. Take the medium, the palette "
                "and the line quality from it, and nothing else.")

    return "\n".join([
        header(f"CHARACTER SHEET — {who['name']}", attach,
               f"series/{who['_series']}/charsheet/"
               f"{who.get('sheet','sheet.png')}"),
        f"Draw a CHARACTER REFERENCE SHEET for one character, on a plain white "
        f"background.",
        "",
        "REFERENCE",
        para(role),
        "",
        "Show, side by side, with clear space between them:",
        "",
        numbered,
        "",
        para(f"{who['name']}: {flat(who['description'])}"),
        "",
        "STYLE",
        para(style["style"]),
        "",
        "Plain white background. No scenery, no furniture, no props, no other "
        "characters. No text, no letters, no numbers, no labels anywhere in "
        "the image.",
    ])


def render_charsheet(style, world):
    views = []
    for c in world["cast"]:
        for v in c.get("sheet_views", []):
            views.append(f"{c['name']}, {v}")
    numbered = "\n".join(f"{i}. {v}." for i, v in enumerate(views, 1))
    descriptions = "\n\n".join(
        para(f"{c['name']}: {flat(c['description'])}") for c in world["cast"])
    ref, missing = named_reference(style, world)

    return "\n".join([
        header("CHARACTER SHEET — whole cast",
               f"{ref}   (style only){missing}"),
        "Draw a CHARACTER REFERENCE SHEET on a plain white background.",
        "",
        "STYLE REFERENCE",
        para("One attached image is a STYLE REFERENCE. "
             + style["style_reference"]),
        "",
        "Show, side by side, with clear space between them:",
        "",
        numbered,
        "",
        descriptions,
        "",
        "STYLE",
        para(style["style"]),
        "",
        "Plain white background. No scenery, no furniture, no props. No text, "
        "no letters, no numbers, no labels anywhere in the image.",
    ])


PLATE_RESTRAINT = """\
This is a stage, not a finished painting. A child will be painted on top of it
on every page that happens here, so it has to stay quiet and it has to leave
her somewhere to stand.

- Resolve detail in ONE place only: the object named below as the one painted
  in full. Everything else goes in broad, soft, simplified washes.
- Draw the mass of a thing, not its parts. A few marks at its edge stand for
  the rest. No individual leaves, bricks, floorboards, railings or objects on
  a shelf.
- Keep everything behind the near object pale and low in contrast. Save the
  darkest darks for one or two small accents at the front.
- Leave roughly a third of the picture almost empty, with no incident in it at
  all. The lower half is the best place for that emptiness — it is where the
  child will stand or sit.
- Line work, if this style uses it, belongs only on the near object. Nothing
  behind it is drawn in line.

A plate that looks impressive on its own is usually a plate that will fight
the character. Under-paint it deliberately."""


def render_plate(name, style, world):
    settings = world.get("settings", {})
    if name not in settings:
        raise SystemExit(f"setting '{name}' not in story_world.yaml "
                         f"(have: {', '.join(settings)})")
    st = settings[name]
    ref, missing = plate_reference(style, world)
    parts = [
        header(f"SETTING PLATE — {name}",
               f"{ref}   (style only){missing}",
               os.path.join(BOOK_DIR, "art", st["plate"])),
        "Draw this place, empty. No people, no animals, no characters.",
        "",
        "HOW MUCH TO PAINT",
        PLATE_RESTRAINT,
        "",
        "STYLE REFERENCE",
        para("One attached image is a STYLE REFERENCE. "
             + style["style_reference"]),
        "",
        "THE PLACE",
        para(st["description"]),
        "",
    ]
    plate_constants = list(st.get("constants", [])) + \
        list(st.get("plate_constants", []))
    if plate_constants:
        parts += ["MUST NOT CHANGE", bullets(plate_constants), ""]
    parts += [
        para(style["aspect"]),
        "",
        "STYLE",
        para(style["style"]),
        "",
        "NEVER",
        bullets(list(style["never"]) + list(st.get("never", []))),
    ]
    return "\n".join(parts)


SWATCH_SUBJECT = """\
This one sheet has to show how this style handles a figure AND how it handles
a place, because both kinds of picture will be matched against it later.

On a plain white background, arranged with clear space between them:

1. Top left — a small child of about four, standing, full body, facing
   forward, in plain pyjamas, barefoot.
2. Top right — a soft stuffed toy animal on its own, sitting, facing forward.
3. The whole lower half — a small landscape vignette: a path curving away
   between trees under an open sky, with one bench beside it. No people. Let
   this vignette fade softly into the white paper at its edges rather than
   sitting in a box.

The figures are generic. Give them no distinctive features, no logos, no
accessories beyond the pyjamas.

The landscape is the more important half, and it must be UNDER-painted. Every
setting in every book will be matched against it, so if it is busy, they will
all be busy."""


SWATCH_RESTRAINT = """\
Paint the landscape the way this style would paint a background that a
character is later placed on top of:

- Resolve ONE object only — the bench. Everything else is broad, soft,
  simplified wash.
- No individual leaves, no individual blades of grass, no individual flowers.
  Draw the mass of a tree; a few leaves at its edge stand for the rest.
- The middle distance is pale and almost featureless. The sky is nearly empty.
- Leave bare paper showing in several places, including a large quiet area of
  open ground with nothing in it at all.
- Line work only on the bench. Nothing else is drawn in line.

Aim for roughly a third of the marks you would normally make. If it looks
slightly unfinished on its own, it is correct — it is a background, and
everything painted from it will inherit its busyness."""


def render_swatch(pack_name):
    pack = load_pack(pack_name)
    return "\n".join([
        header(f"STYLE SWATCH — {pack.get('name', pack_name)}",
               "nothing — this is the one prompt with no attachment",
               f"styles/{pack_name}/{pack.get('reference','reference.png')}"),
        "Draw a STYLE SAMPLE for a children's picture book.",
        "",
        SWATCH_SUBJECT,
        "",
        "HOW MUCH TO PAINT",
        SWATCH_RESTRAINT,
        "",
        "STYLE",
        para(pack["style"]),
        "",
        "EDGES",
        para(pack["edges"]),
        "",
        "Plain white background. No room, no furniture, no scenery, no props.",
        "No text, no letters, no numbers, no labels anywhere in the image.",
        "Do not imitate or reference any specific named book, character,",
        "illustrator or franchise.",
    ])


def main():
    argv = sys.argv[1:]

    if "--styles" in argv:
        packs = list_packs()
        if not packs:
            print("no style packs in styles/")
            return
        for name in packs:
            pack = load_pack(name)
            ref = os.path.join(pack["_dir"], pack.get("reference", "reference.png"))
            mark = "ok     " if os.path.isfile(ref) else "NO REF "
            print(f"{mark} {name:<14} {pack.get('name','')}")
        return

    if "--swatch" in argv:
        print(render_swatch(argv[argv.index("--swatch") + 1]))
        return

    if "--dir" in argv:
        d = os.path.abspath(argv[argv.index("--dir") + 1])
    else:
        d = os.getcwd()
    if not os.path.isfile(os.path.join(d, "style.yaml")):
        raise SystemExit(f"no style.yaml in {d} — pass --dir books/<book>")

    pages, style, world = load(d)

    def emit(text, default_name):
        if "--out" in argv:
            outdir = argv[argv.index("--out") + 1]
            os.makedirs(outdir, exist_ok=True)
            path = os.path.join(outdir, default_name)
            with open(path, "w", encoding="utf-8") as f:
                f.write(text + "\n")
            print(f"wrote {path}")
        else:
            print(text)

    if "--charsheet" in argv:
        i = argv.index("--charsheet")
        who = (argv[i + 1] if len(argv) > i + 1
               and not argv[i + 1].startswith("-") else None)
        emit(render_one_charsheet(style, world, who) if who
             else render_charsheet(style, world),
             f"charsheet_{who}.md" if who else "charsheet_all.md")
        return
    if "--plate" in argv:
        pname = argv[argv.index("--plate") + 1]
        emit(render_plate(pname, style, world), f"plate_{pname}.md")
        return

    errs, warns = validate(pages, style, world)
    for w in warns:
        print("warning: " + w, file=sys.stderr)
    if errs:
        print("\nVALIDATION FAILED:\n", file=sys.stderr)
        for e in errs:
            print("  - " + e, file=sys.stderr)
        sys.exit(1)
    if "--check" in sys.argv:
        print(f"OK — {len(pages)} pages across "
              f"{len({p['setting'] for p in pages})} setting(s).")
        return

    outdir = None
    if "--out" in sys.argv:
        outdir = sys.argv[sys.argv.index("--out") + 1]
        os.makedirs(outdir, exist_ok=True)

    only = next((int(a) for a in sys.argv[1:] if a.isdigit()), None)
    for i, pg in enumerate(pages):
        if only and pg["n"] != only:
            continue
        prev_n = None if i == 0 else pages[i - 1]["n"]
        text = render_page(pg, style, world, prev_n)
        if outdir:
            path = os.path.join(outdir, f"page_{pg['n']:02d}.md")
            with open(path, "w", encoding="utf-8") as f:
                f.write(text + "\n")
            print(f"wrote {path}")
        else:
            print(text)
            print()


if __name__ == "__main__":
    main()
