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
    --charsheet     the character-sheet prompt, built from the cast
    --plate NAME    the setting-plate prompt for one setting
    --styles        list the style packs available in styles/
    --swatch PACK   the neutral style-swatch prompt for a pack

The book's style.yaml names a `pack:`; this merges styles/<pack>/pack.yaml
over it, so `style` and `edges` travel with the chosen medium.
"""

import sys
import os
import textwrap
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


def load(book_dir):
    def y(name):
        with open(os.path.join(book_dir, name), encoding="utf-8") as f:
            return yaml.safe_load(f)
    pages = y("pages.yaml")["pages"]
    style = y("style.yaml")
    world = y("story_world.yaml")

    packname = style.get("pack")
    if packname:
        pack = load_pack(packname)
        # the pack owns the medium: style + edges travel together
        for k in ("style", "edges"):
            if pack.get(k):
                style[k] = pack[k]
        style["_pack"] = pack
    return pages, style, world


def reference_path(style, world):
    """Where the style reference lives: the pack's swatch unless the book
    overrides it with its own file in art/."""
    override = world.get("style_reference_image")
    pack = style.get("_pack")
    if pack and override in (None, "reference.png"):
        return os.path.join("..", "..", "styles", pack["_name"],
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

def cast_phrase(world):
    """'Orea, a girl of four, and Whoof-Whoof, a soft beige stuffed toy dog'"""
    bits = []
    for c in world["cast"]:
        first = flat(c["description"]).split(".")[0].strip().rstrip(".")
        first = first[0].lower() + first[1:] if first else first
        bits.append(f"{c['name']}, {first}")
    if len(bits) == 1:
        return bits[0]
    return ", ".join(bits[:-1]) + " and " + bits[-1]


def cast_rules(world):
    out = []
    for c in world["cast"]:
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
    errors, warnings = [], []

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

        missing = [f for f in fields if f not in scene]
        if missing:
            warnings.append(f"page {n}: scene missing {', '.join(missing)}")

        banned = ("knows", "remembers", "decides", "tomorrow", "yesterday",
                  "thinks", "wonders")
        for k, v in scene.items():
            low = flat(v).lower()
            for b in banned:
                if b in low:
                    warnings.append(
                        f"page {n}: scene.{k} contains '{b}' — narration, not "
                        f"something visible in frame.")
    return errors, warnings


def render_scene(scene, style):
    out = []
    for key, label in style["scene_fields"]:
        if key in scene:
            out.append(textwrap.fill(f"{label}: {flat(scene[key])}", 78,
                                     subsequent_indent="    "))
    return "\n".join(out)


def render_page(pg, style, world, prev_n):
    s = style
    sname, setting = setting_for(pg, world)

    attach = ["charsheet.png", setting["plate"]]
    if prev_n is not None:
        attach.append(f"page_{prev_n:02d}.png")

    roles = [
        para(s["image_roles"]["characters"].format(characters=cast_phrase(world))),
        para(s["image_roles"]["setting"].format(
            setting=flat(setting["description"]).rstrip("."))),
        para(s["image_roles"]["previous_page"] if prev_n is not None
             else s["image_roles"]["no_previous"]),
    ]

    constants = list(setting.get("constants", [])) + cast_rules(world)
    nevers = list(s["never"]) + list(setting.get("never", []))

    parts = [
        "=" * 74,
        f"PAGE {pg['n']}   setting: {sname}   shot: {pg['shot']}   "
        f"angle: {pg['angle']}",
        f"attach: {', '.join(attach)}",
        "=" * 74,
        "",
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

    if constants:
        parts += ["MUST NOT CHANGE", bullets(constants), ""]

    for label, text in world.get("continuity", {}).items():
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


def render_charsheet(style, world):
    views = []
    for c in world["cast"]:
        for v in c.get("sheet_views", []):
            views.append(f"{c['name']}, {v}")
    numbered = "\n".join(f"{i}. {v}." for i, v in enumerate(views, 1))
    descriptions = "\n\n".join(
        para(f"{c['name']}: {flat(c['description'])}") for c in world["cast"])
    ref = reference_path(style, world)

    return "\n".join([
        "=" * 74,
        "CHARACTER SHEET",
        f"attach: {ref}   (style reference only)",
        "=" * 74,
        "",
        "Draw a CHARACTER REFERENCE SHEET on a plain white background.",
        "",
        "STYLE REFERENCE",
        para(style["style_reference"]),
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


def render_plate(name, style, world):
    settings = world.get("settings", {})
    if name not in settings:
        raise SystemExit(f"setting '{name}' not in story_world.yaml "
                         f"(have: {', '.join(settings)})")
    st = settings[name]
    ref = reference_path(style, world)
    parts = [
        "=" * 74,
        f"SETTING PLATE — {name}  ->  save as art/{st['plate']}",
        f"attach: {ref}   (style reference only)",
        "=" * 74,
        "",
        "Draw this place, empty. No people, no animals, no characters.",
        "",
        "STYLE REFERENCE",
        para(style["style_reference"]),
        "",
        "THE PLACE",
        para(st["description"]),
        "",
    ]
    if st.get("constants"):
        parts += ["MUST NOT CHANGE", bullets(st["constants"]), ""]
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
Show, side by side on a plain white background, with clear space between them:

1. A small child of about four, standing, full body, facing forward, in plain
   pyjamas, barefoot.
2. The same child, head and shoulders, larger, facing forward.
3. A soft stuffed toy animal on its own, sitting, facing forward.

These are generic figures for a style sample. Give them no distinctive
features, no logos, no accessories beyond the pyjamas."""


def render_swatch(pack_name):
    pack = load_pack(pack_name)
    return "\n".join([
        "=" * 74,
        f"STYLE SWATCH — {pack.get('name', pack_name)}",
        f"attach: nothing   ->  save as styles/{pack_name}/"
        f"{pack.get('reference', 'reference.png')}",
        "=" * 74,
        "",
        "Draw a STYLE SAMPLE for a children's picture book.",
        "",
        SWATCH_SUBJECT,
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
    if not os.path.isfile(os.path.join(d, "pages.yaml")):
        raise SystemExit(f"no pages.yaml in {d} — pass --dir books/<book>")

    pages, style, world = load(d)

    if "--charsheet" in sys.argv:
        print(render_charsheet(style, world))
        return
    if "--plate" in sys.argv:
        print(render_plate(sys.argv[sys.argv.index("--plate") + 1], style, world))
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
