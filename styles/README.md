# Style packs

One folder per look. A pack is **wording plus a reference image** — both are
needed. The wording alone only nudges the model within its existing prior; the
image relocates it. Neither works alone.

```
styles/<pack>/
  pack.yaml       name, style paragraph, edges rule
  reference.png   the swatch — generate once, commit it
```

A book selects its pack with one line in its `style.yaml`:

```yaml
pack: watercolour
```

`bin/prompts.py` merges the pack's `style` and `edges` over `style.yaml`, and
attaches `styles/<pack>/reference.png` to the character-sheet and setting-plate
prompts. Switching a book's look is one word — but it means regenerating the
character sheet and therefore all the art, so decide before you start.

## Why `edges` lives in the pack

"Watercolour vignette, wash fading at the edges" is meaningless for cartoon or
anime, which want a clean rectangular border. Edge treatment is a property of
the medium, so it travels with the medium.

## Adding a pack

1. `mkdir styles/<name>` and write a `pack.yaml` with `name`, `style`, `edges`.
2. Generate the swatch:

   ```bash
   python3 bin/prompts.py --swatch <name>
   ```

   Run the printed prompt with **nothing attached**. Save the result as
   `styles/<name>/reference.png`.
3. Commit both files. Every future book can now choose it.

## The swatch must be neutral

Every pack's reference shows the **same** neutral subject — one generic child
and one generic soft toy, on plain white, no scenery. That is deliberate. A
reference showing a bedroom will drag bedroom-ness into a forest book; a
reference showing a specific character will fight your own cast. The swatch
carries medium, palette and line quality, and nothing else.

`--swatch` emits that fixed subject automatically, so all packs stay comparable.

## Generate your swatches, do not collect them

Use the `--swatch` prompt. Do not use a photograph of a real illustrator's work
as a reference image. It is an IP problem, and it directly contradicts the
"do not imitate any named illustrator" line that appears in every prompt this
repo produces.

## Packs in this repo

| pack | look |
|---|---|
| `watercolour` | Traditional watercolour, paper grain, ink linework, muted. Soft vignette edges. |
| `pencil` | Coloured pencil over a light wash. Visible strokes, handmade. Fades to bare paper. |
| `cartoon` | Bold even outlines, flat bright fills, simple shapes. Hard border. |
| `anime` | Soft slice-of-life anime, cel shading, painted backgrounds. Hard border. |
| `gouache` | Opaque matte gouache on toned paper, mid-century palette. Hard border. |

`reference.png` is missing from each until you generate it. `--check` will tell
you which packs are incomplete.
