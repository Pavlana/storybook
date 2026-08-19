# Making a book — step by step

This guide walks through one complete book from nothing to a finished PDF,
using a real example: **Orea and the dentist**.

---

## First, what this actually is

There are two halves and it helps to keep them separate in your head.

**The repo is a workshop, not a robot.** The scripts in `bin/` do two jobs:
they *write prompts* for you, and they *lay out the finished PDF*. They never
call an AI. They have no API key and need no account.

**You are the one talking to the AI.** You take the prompts the scripts print,
paste them into Claude or ChatGPT, and put what comes back into files. The
scripts then check your work and build the book.

So the loop is always the same:

```
run a script  →  get a prompt  →  paste into AI  →  save the answer  →  repeat
```

You do not "connect the folder to an AI and ask it for a story". You could,
and it makes the copying easier — see *Working with the folder connected*
below — but nothing requires it.

---

## What you need

- **Python 3.10 or newer.** Check with `python3 --version`.
- **A text AI** for words: Claude or ChatGPT. Claude Opus 5 is what these
  prompts were written against.
- **An image AI** for pictures: ChatGPT's image generation, or Gemini. It must
  accept **several attached images at once** — that is what holds the character
  steady, and a tool without it will not work here.
- A text editor. Any will do; YAML is just indented text.

Set up once:

```bash
git clone <the repo>
cd storybook
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`python3 -m venv .venv` makes a private space for this project's libraries.
On a Mac, plain `pip install` is usually blocked by the system Python — this
avoids the problem entirely.

**Every new terminal window, run `source .venv/bin/activate` first.** If you
forget, the scripts will tell you what to do rather than showing an error.

Check it works by rebuilding the finished example:

```bash
python3 bin/build.py --dir books/orea-01-goodnight --all
```

Two PDFs appear inside that book's folder. If they do, everything is working.

---

## The example we are building

> Orea is four. She is frightened of going to the dentist for a check-up.
> She walks to the appointment through the park with Mum and Whoof-Whoof.
> At the surgery she asks to see each tool before it is used, and counts her
> own teeth out loud.

Same child, same toy, **new settings**. That matters: she already exists as a
character sheet, so we reuse her and skip the hardest step.

---

# Step 1 — Make the book folder

```bash
cp -r templates/new-book books/orea-02-dentist
```

Copy the style across too, so book two looks like book one:

```bash
cp books/orea-01-goodnight/style.yaml books/orea-02-dentist/style.yaml
```

You do **not** copy the character sheets. They live once, in
`series/orea/charsheet/`, and every book in the series points at them.

> **This is the whole point of a series.** A character sheet is the most
> expensive thing in the project and the hardest to get right. Keeping one copy
> means book two costs a fraction of book one, and Orea looks like herself
> across both books — not merely similar. It also means that if you ever
> repaint her sheet, every future book gets the better one automatically.

---

# Step 2 — Write the brief

Open `books/orea-02-dentist/brief.md` and fill it in. This one is already
written for you as an example:

```
Child:        Orea, four, a girl
Companion:    Whoof-Whoof, a beige toy dog with long floppy ears — constant
Family:       Mum. (Dad exists but is not in this story.)
Settings:     park — Orea walks there with Mum and Whoof-Whoof
              surgery — the dentist's room, where the check-up happens
The problem:  Orea is frightened of going to the dentist for a check-up
The method:   She looks at the tools and lets the dentist show her each one
              before it is used, and counts her own teeth out loud
Pages:        8
Reading age:  3-4
Tone:         warm, calm, short sentences, present tense
Never:        never lose or harm Whoof-Whoof; never promise it will not hurt;
              never say there is nothing to be scared of
```

**Be strict about `Family` and `Never`.** Anything you leave vague, the model
fills in — usually with an extra adult, a sibling, or a reassurance you did not
want. "Never promise it will not hurt" is doing real work there.

**`The method` is the most important line.** It is the thing the child can do
again next time. Without it the book is a description of a fear rather than a
help with one.

---

# Step 3 — Write the story  ·  **Gate 1**

Open `prompts/01_story.md`. Copy the whole thing below the `---` line, paste it
into Claude, and paste your brief where it says to.

You get back eight numbered paragraphs. **Read them properly.** This is the
cheapest moment in the entire process to change your mind — a wrong word here
costs a retype, and the same wrong idea discovered after the art exists costs
you a day.

Check:

- Does it use only the names in the brief? No invented sibling, no named dentist
  unless you asked for one.
- Is the child the one who does the thing? Mum may be there. Mum may be held
  onto. Mum does not fix it.
- Does it avoid promising the fear will not come back?
- Would a four-year-old follow it read aloud?

When you are happy, save it into `books/orea-02-dentist/text/en.yaml`:

```yaml
title: "Orea and the Dentist"

pages:
  1: >
    <the first paragraph>
  2: >
    <the second paragraph>
```

Indentation matters. Two spaces before the number, four before the text.

> **Do not go on until you are happy with these words.** Everything after this
> point is derived from them.

---

# Step 4 — Describe the world

Open `prompts/02_world.md`, paste it into Claude, and paste your **approved
story text** at the bottom.

It returns YAML describing the cast and the settings. Save it as
`books/orea-02-dentist/story_world.yaml`.

Now edit two things by hand:

**One. Delete any `cast:` descriptions it wrote and replace them with ids.** The
model will have re-described Orea from your story, and small differences here
become drift in the pictures. The real descriptions live in
`series/orea/cast.yaml` and no book repeats them:

```yaml
series: orea
cast: [orea, whoof, mum, dentist]
```

If your story has someone new in it — the dentist, in this book — add them to
`series/orea/cast.yaml` first, then list their id here. Give them a plain,
permanent id: `dentist`, not `nice_lady`. Every future book will use it.

**Two.** Check you have both settings:

```yaml
settings:
  park:
    plate: park.png
    description: >
      A town park on a bright cool morning: a wide paved path, mown grass,
      autumn trees, a green bench, low iron railings.
    constants:
      - The path is pale grey paving, the bench green, the railings black.

  surgery:
    plate: surgery.png
    description: >
      A small, calm dentist's room in daylight: one dental chair in pale blue,
      a bright adjustable lamp on an arm, a low tray of clean instruments, a
      window with a plain blind, pale walls.
    constants:
      - The chair is pale blue, the walls pale, the room bright and uncluttered.
    never:
      - Nothing sharp or medical-looking in close-up. No needles. No blood.
        No open mouths in distress.
```

> That `never` block is not decoration. Left to itself an image model will make
> a dentist's room look clinical and frightening, which is the exact opposite of
> what this book is for.

---

# Step 5 — Choose the style

```bash
python3 bin/prompts.py --styles
```

You will see `watercolour`, and whether it has a reference swatch yet.

**If it says `NO REF`**, generate the swatch once — it is shared by every book
you will ever make:

```bash
python3 bin/prompts.py --swatch watercolour
```

Paste that into your image AI with **nothing attached**. Save the result as
`styles/watercolour/reference.png`.

For this book, since Orea already has an approved sheet, point the style
reference at that instead — a finished sheet in the right style is a stronger
reference than a generic swatch. In `story_world.yaml`, as a path from the repo
root:

```yaml
style_reference_image: series/orea/charsheet/charsheet_orea_dog.png
```

Delete that line and it falls back to the pack swatch.

---

# Step 6 — Draw the characters

Every character in `series/orea/cast.yaml` needs one approved **character
sheet**: a single image showing them two or three times, in different poses,
against plain white. That sheet is what you attach to every page prompt for the
rest of the book. It is the reason the character stops drifting.

There is no character-sheet file to open. The prompt is **built for you** out of
three things — the style pack from `style.yaml`, the character's description
from `series/orea/cast.yaml`, and the sheet wording in `bin/prompts.py`:

```bash
python3 bin/prompts.py --dir books/orea-02-dentist --charsheet dentist
```

The argument is the **id** from the cast file, not the name. Ask for a character
who is not in this book and it will tell you which ids are valid.

To write it to a file instead of the screen:

```bash
python3 bin/prompts.py --dir books/orea-02-dentist --charsheet dentist --out out/
```

Now paste that prompt into your image AI, and read the `attach:` line at the top
of it:

- **`attach: nothing`** — the character has never been drawn. Run the prompt on
  its own. The style pack's wording is doing all the work.
- **`attach: <some image>`** — the character already exists in a picture
  somewhere, and `cast.yaml` points at it. Attach that image. **Always do this
  when it is offered.** A likeness reference beats any amount of description;
  it is the single largest quality difference in the whole pipeline.

Mum is the worked example. She was never given a sheet in book one — she just
appeared on page two. So her cast entry says:

```yaml
mum:
  sheet: charsheet_mum.png
  reference: books/orea-01-goodnight/art/page_02.png
```

and her prompt tells you to attach that page. The result is the same woman, not
a woman who resembles her.

Save the finished sheet **exactly where the prompt's last line says**, which is
always `series/orea/charsheet/<the sheet filename from cast.yaml>`. If you save
it anywhere else, the page prompts will not find it.

You can also print every missing sheet at once:

```bash
python3 bin/prompts.py --dir books/orea-02-dentist --charsheet
```

> **Judge a sheet hard.** Full body, plain white background, no scenery, no
> shadow story, the same face in every pose. Everything downstream inherits it,
> so a sheet you are only *fairly* happy with will make forty pictures you are
> only fairly happy with. Regenerating now costs one prompt; regenerating after
> the pages costs all of them.

Orea and Whoof-Whoof share one sheet — they are always drawn together — which is
why both entries name the same file. That is allowed and it saves an attachment
slot on every page.

---

# Step 7 — Paint the settings

One command per place:

```bash
python3 bin/prompts.py --dir books/orea-02-dentist --plate park
python3 bin/prompts.py --dir books/orea-02-dentist --plate surgery
```

Each prints a prompt for an **empty** place — no people, no toys. Attach the
style reference named on the `attach:` line, run it, and save the results as
`books/orea-02-dentist/art/park.png` and `art/surgery.png`.

Accept a plate only when it matches its `constants` and looks like the same
world as the character sheet. These two images fix the colours for every page
that happens there, so a mistake now repeats eight times.

---

# Step 8 — Describe every picture  ·  **Gate 2**

Open `prompts/03_scenes.md`, paste it into Claude with your approved story text.

It returns one block per page: which setting, how close the camera is, where it
is standing, and a description of what is in the frame.

Paste the result into `books/orea-02-dentist/pages.yaml` under `pages:`.

Read these too. The rule that matters: **every line must be something a painter
could see.** "Orea knows Mum is waiting outside" cannot be painted. "Orea's
hand gripping the arm of the chair" can.

---

# Step 9 — Let the computer check your work

```bash
python3 bin/prompts.py --dir books/orea-02-dentist --check
```

It will refuse, loudly, if:

- a page names a setting that does not exist
- a camera angle is misspelled
- **two pages in a row use the same shot from the same angle** — the thing that
  made the first draft of book one look like eight photographs of one corner
- a scene field reads like story rather than picture

Fix `pages.yaml` until this passes. It takes seconds and saves re-rolls.

---

# Step 10 — Get the page prompts

```bash
python3 bin/prompts.py --dir books/orea-02-dentist --out out/
```

Eight files in `out/`, one per page. Each begins with an `attach:` line telling
you exactly which images to attach.

---

# Step 11 — Generate the pictures, in order

**Page 1:** attach exactly what the `attach:` line names — the character sheets
for whoever is in that picture, and the setting plate. Paste `out/page_01.md`.
Save the result as `art/page_01.png`.

**Every page after:** the same, **plus the page you just approved.** The
`attach:` line lists it for you.

**Keep it to four images.** Beyond that the model starts averaging faces instead
of copying them. If a page needs more, it is because every character in the book
is being attached to every page — so tell that page who is actually in frame, in
`pages.yaml`:

```yaml
- n: 3
  image: page_03.png
  characters: []            # nobody — this page is a close-up of the tools
- n: 4
  image: page_04.png
  characters: [orea, whoof, dentist]
```

Leave `characters:` out and every character in the book gets attached, which is
usually too many. `--check` warns you when a page goes over four.

**Check each page before starting the next.** Look for:

- Orea's face and hair matching the sheet
- Whoof-Whoof present, with his red collar and navy bow
- nothing cropped at the edges
- the setting's colours unchanged
- no text anywhere in the picture

A bad page becomes the reference for the next one, and the error compounds.

> **Expect to generate each page more than once.** Two to four attempts is
> normal. Holding the character steady and getting the model to obey the scene
> are two different problems, and chaining only solves the first. Instructions
> phrased as *not* doing something — "her face is not visible", "no one else in
> the room" — are the ones most often ignored.

---

# Step 12 — The cover, last

Open `prompts/04_cover.md`. Attach the character sheet and two or three finished
pages you are pleased with. Save the result as `art/page_00.png`.

The cover shows Orea and Whoof-Whoof looking warm and appealing. It does **not**
show the dentist, the chair, or the fear. The cover is the promise, not the plot.

---

# Step 13 — Build the book

Add the title and language settings to `books/orea-02-dentist/book.yaml`:

```yaml
languages:
  en:
    font: CenturySchoolbook
    title_size: 29
    body_size: 13
    leading: 20.5
    output: "Orea and the Dentist.pdf"
```

Then:

```bash
python3 bin/build.py --dir books/orea-02-dentist
```

The PDF appears in the book's folder. Illustration left, text right, cover first.

---

# Step 14 — Another language, optional

Ask Claude to translate `text/en.yaml`, keeping the page numbers. Save as
`text/ru.yaml`. Add a language block to `book.yaml` — **Cyrillic needs Lora;
Century Schoolbook has no Cyrillic letters at all** — then:

```bash
python3 bin/build.py --dir books/orea-02-dentist --all
```

Both languages, same pictures, same layout.

---

## Changing your mind later

Not everything costs the same to undo.

| You want to change | What you have to redo |
|---|---|
| A word, a sentence, the whole text | Nothing. Edit and rebuild. |
| Font, colour, page size | Nothing. Edit and rebuild. |
| Add a language | Nothing. New text file, rebuild. |
| One picture you dislike | That page only. |
| A setting plate | Every page in that setting. |
| The character sheet | All the pictures. |
| The style pack | All the pictures. |

The top three are free and instant. That is the reason the text, the layout and
the art direction live in separate files.

**Use git.** Commit after each gate. Then "I preferred the earlier version" is a
question you can answer.

---

## Working with the folder connected

If you use Claude with the folder connected, or any AI tool with file access,
you can skip the copying: ask it to read `prompts/01_story.md`, follow it, and
write the result straight into `text/en.yaml`. Same steps, same gates, less
clipboard.

The image generation still has to happen wherever your image model lives. No
tool currently does the words, the pictures and the files in one place.

---

## When something goes wrong

**`no pages.yaml in ...`** — you forgot `--dir books/<your-book>`.

**`setting 'x' not in story_world.yaml`** — a page names a place you have not
described. Check spelling; these are case-sensitive.

**`same setting, shot AND angle as page N`** — working as intended. Change one
of the two angles.

**Text overflows the page** — your paragraph is too long for the space. Shorten
it, or reduce `body_size` in `book.yaml`.

**Cyrillic prints as blank boxes** — you are using a Latin-only font. Switch
that language to `Lora`.

**The character drifts halfway through** — you attached the wrong previous page,
or attached more than three images, or accepted a page you should have
re-rolled. Go back to the last good page and chain forward from there.

---

## How long this really takes

Words and structure: under an hour, most of it reading and deciding.

Pictures: the rest. Eight pages at two to four attempts each is the honest
number, and it is the only slow part. Everything else is minutes.
