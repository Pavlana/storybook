# storybook

A repeatable pipeline for making illustrated children's books with AI, and a
layout engine that turns the results into a PDF.

The tools generate **prompts**, not pictures. You run those prompts in whatever
image model you use, drop the results into `art/`, and build. Nothing here calls
an API or needs a key.

```bash
git clone <this repo> && cd storybook
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 bin/build.py --dir books/orea-01-goodnight --all
```

The virtual environment matters on macOS: the system Python refuses
`pip install` these days, and a venv sidesteps it. Activate it
(`source .venv/bin/activate`) in each new terminal before running anything.

That rebuilds the example book, English and Russian, from its art and text.

**New here? Read [USER_GUIDE.md](USER_GUIDE.md).** It walks through one whole
book from a blank folder to a finished PDF, with a worked example.

---

## Layout

```
bin/          build.py, prompts.py — the engine, book-agnostic
prompts/      the pipeline's prompt templates, in order
styles/       style packs: wording + a reference swatch, shared by all books
series/       one folder per series: the shared cast and their character sheets
books/        one folder per book
templates/    skeleton to copy for a new book
```

A book folder:

```
books/<book>/
  book.yaml          layout, and one typography block per language
  style.yaml         which style pack; craft rules with no story facts in them
  story_world.yaml   which cast ids appear; this story's settings, continuity
  pages.yaml         per page: setting, camera, who is in frame, the scene
  text/<lang>.yaml   title and page text, one file per language
  art/               the setting plates, page_00..NN.png
```

A series folder:

```
series/<series>/
  cast.yaml          who these people are — the only place they are described
  charsheet/         one approved sheet per character, shared by every book
```

Books never describe or store a character. They name ids, and the ids resolve
here. Add a character once and every later book gets them, looking the same.

### Why four files and not one

They change at different times and invalidate different things.

| You change | You must redo |
|---|---|
| `text/<lang>.yaml` | nothing — rebuild |
| `book.yaml` (font, tint, size) | nothing — rebuild |
| a new language | nothing — rebuild |
| one page's `scene` | that page's art |
| a setting plate | every page in that setting |
| a character sheet | all the art in every book they appear in |
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
| 6 | Character sheets, one per new character | image model | `bin/prompts.py --dir books/<book> --charsheet <id>` → `series/<series>/charsheet/` |
| 7 | Setting plate, one per setting | image model | `bin/prompts.py --dir books/<book> --plate <name>` |
| 8 | **Scenes** — *Gate 2* | Claude Opus 5 | `prompts/03_scenes.md` → `pages.yaml` |
| 9 | Validate | — | `bin/prompts.py --dir books/<book> --check` |
| 10 | Emit page prompts | — | `bin/prompts.py --dir books/<book> --out out/` |
| 11 | Page art, chained | image model | → `art/page_NN.png` |
| 12 | Cover, last | image model | `prompts/04_cover.md` → `art/page_00.png` |
| 13 | Translate | Claude Opus 5 | → `text/<lang>.yaml` |
| 14 | Build | — | `bin/build.py --dir books/<book> --all` |

### Character sheets, step 6

There is no character-sheet file to open — the prompt is assembled at run time
from the style pack, the character's description in `series/<series>/cast.yaml`,
and the sheet wording in `bin/prompts.py`.

```bash
python3 bin/prompts.py --dir books/<book> --charsheet <id>      # one character
python3 bin/prompts.py --dir books/<book> --charsheet           # all of them
python3 bin/prompts.py --dir books/<book> --charsheet <id> --out out/
```

The argument is the **id** from `cast.yaml`, not the name. There is always one
image to attach, and the `attach:` line says which job it is doing:

- a character with `reference:` — an illustration they already appear in —
  attaches that, as likeness *and* style. Copy the face exactly.
- a character without one attaches the book's style reference instead. Invent
  the face from the description; take only the paint.

`reference:` means *this is the same person*. Never point it at somebody else's
picture to borrow a style — that is what the style reference is for. Save the
result exactly where the prompt's last line says.

### Chaining, step 11

Generate pages in order. For each page attach **the sheets of the characters in
that picture, the setting plate, and the previous approved page** — four images,
never more. The emitted prompt names them on its `attach:` line.

Which sheets get attached comes from that page's `characters:` list in
`pages.yaml`. Omit the list and every character in the book is attached, which
overshoots four fast and makes the model average faces instead of copying them.
`--check` warns when a page goes over.

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
