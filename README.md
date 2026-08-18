# storybook

A repeatable pipeline for making illustrated children's books with AI, and a
layout engine that turns the results into a PDF.

The tools generate **prompts**, not pictures. You run those prompts in whatever
image model you use, drop the results into `art/`, and build. Nothing here calls
an API or needs a key.

```bash
git clone <this repo> && cd storybook
pip install -r requirements.txt
python3 bin/build.py --dir books/orea-01-goodnight --all
```

That rebuilds the example book, English and Russian, from its art and text.

---

## Layout

```
bin/          build.py, prompts.py — the engine, book-agnostic
prompts/      the pipeline's prompt templates, in order
styles/       style packs: wording + a reference swatch, shared by all books
books/        one folder per book
templates/    skeleton to copy for a new book
```

A book folder:

```
books/<book>/
  book.yaml          layout, and one typography block per language
  style.yaml         which style pack; craft rules with no story facts in them
  story_world.yaml   this story's cast, settings and continuity
  pages.yaml         per page: setting, camera, and the scene description
  text/<lang>.yaml   title and page text, one file per language
  art/               charsheet.png, the setting plates, page_00..NN.png
```

### Why four files and not one

They change at different times and invalidate different things.

| You change | You must redo |
|---|---|
| `text/<lang>.yaml` | nothing — rebuild |
| `book.yaml` (font, tint, size) | nothing — rebuild |
| a new language | nothing — rebuild |
| one page's `scene` | that page's art |
| a setting plate | every page in that setting |
| `charsheet.png` | all the art |
| the style pack | all the art |

The first three are the common cases, and none of them touch a single pixel.

---

## Making a book

Two approval gates. Nothing downstream runs until the gate before it is signed
off, because a mistake in the text costs one regeneration and a mistake in the
character sheet costs all of them.

| # | Step | Tool | Prompt / command |
|---|---|---|---|
| 1 | Write the brief | you | `books/<book>/brief.md` |
| 2 | **Story text** — *Gate 1* | Claude Opus 5 | `prompts/01_story.md` → `text/en.yaml` |
| 3 | Story world | Claude Opus 5 | `prompts/02_world.md` → `story_world.yaml` |
| 4 | Choose a style pack | you | `bin/prompts.py --styles`, set `pack:` in `style.yaml` |
| 5 | Style swatch — skip if the pack already has one | image model | `bin/prompts.py --swatch <pack>` |
| 6 | Character sheet | image model | `bin/prompts.py --dir books/<book> --charsheet` → `art/charsheet.png` |
| 7 | Setting plate, one per setting | image model | `bin/prompts.py --dir books/<book> --plate <name>` |
| 8 | **Scenes** — *Gate 2* | Claude Opus 5 | `prompts/03_scenes.md` → `pages.yaml` |
| 9 | Validate | — | `bin/prompts.py --dir books/<book> --check` |
| 10 | Emit page prompts | — | `bin/prompts.py --dir books/<book> --out out/` |
| 11 | Page art, chained | image model | → `art/page_NN.png` |
| 12 | Cover, last | image model | `prompts/04_cover.md` → `art/page_00.png` |
| 13 | Translate | Claude Opus 5 | → `text/<lang>.yaml` |
| 14 | Build | — | `bin/build.py --dir books/<book> --all` |

### Chaining, step 11

Generate pages in order. For each page attach **the character sheet, the setting
plate, and the previous approved page** — three images, never more. The emitted
prompt names them on its `attach:` line.

Check each page before generating the next. A bad page becomes the reference for
the one after it, and the error compounds.

---

## Two things learned the hard way

**References beat descriptions.** Prose about a medium — paper grain, pigment
bleed, palette — moves the output a little. An attached reference image moves it
completely. Wording is for what a picture cannot state: what must never change,
what must stay out of frame.

**Consistency and instruction-following are separate problems.** Chaining holds
the character and the room steady. It does nothing to make the model obey the
scene. Expect several attempts per page, and expect negative instructions
("her face is not visible") to be the ones dropped.

---

## Requirements

Python 3.10+, `reportlab`, `pyyaml`, `pillow`. Fonts come from the system:
Century Schoolbook, Bookman and Palatino via the URW Type 1 set, Lora and
Caladea via TrueType. Century Schoolbook is Latin-only — Cyrillic needs Lora.
