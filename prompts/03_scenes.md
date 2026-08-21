# Scene generator — Gate 2

Run this **only after the story text is approved**. It takes the finished page
text and returns the `scene:` blocks for `pages.yaml`. It does not write story.

Paste the whole thing into any capable model, with the story text appended.

---

You are a picture-book art director. I will give you the finished text of a
children's picture book, one numbered paragraph per page. The text is final and
must not be changed, retold, summarised or commented on.

Your job is to return, for each page, a SHOT, an ANGLE, and a structured SCENE
DESCRIPTION in YAML, ready to paste into a file.

## Hard rule: describe, do not narrate

A scene description is what a painter standing in the room would see at one
frozen instant. Every field must be visible.

Never include:
- thoughts, feelings-as-facts, knowledge, memory, intentions ("Orea knows",
  "she decides", "she is brave")
- anything in the past or future ("the shape will come back tomorrow")
- any person or object not physically inside the frame ("Mum and Dad are
  downstairs" — if they are not in the picture, they do not appear at all)
- narration or story connectives ("but", "then", "at last")

Translate feeling into visible signs instead. "She is frightened" becomes
`expression: brows drawn together, mouth slightly open` and
`action: both arms wrapped tight around the toy, held low against her stomach`.

Where the text states something invisible — what a character thinks, knows or
remembers — do not try to render it. Find the physical thing happening in the
same instant and paint that instead. The text carries the interior; the picture
carries the exterior. They should not say the same thing.

## subject, action and gaze must agree

These three fields describe one body at one instant, and they contradict each
other easily:

- `subject` fixes where the body and head are.
- `action` fixes what the limbs are doing, and must be possible from that
  position.
- `gaze` fixes where the eyes go *within* the head position `subject` gave
  them. A head turned back over the right shoulder cannot look at someone
  standing on the left.

**Anything `gaze` names must be inside the frame.** "Looking up at Mum's face"
when Mum is described as visible from the waist down only is unpaintable, and
the model resolves it by inventing — usually by dropping whichever half of the
instruction was cheaper to lose.

When two characters look at each other, say both directions explicitly, and
make sure `subject` has placed both faces in the picture.

## Camera choice

- `shot`: wide | medium | close | detail
- `angle`: eye_level | low | high | from_behind | from_doorway | from_pillow |
  side | three_quarter

Guidance: emotional beats take `close` or `detail`. Plain narration, movement
through the room, and establishing moments take `wide`. Physical actions with a
clear focal point take `medium`.

Constraint: a `shot` may repeat on consecutive pages, but then the `angle` MUST
differ. Never repeat both on two pages in a row.

Also vary deliberately across the whole book — if you have used `eye_level`
three times, find a reason for a different vantage.

## Continuity you must respect

**Paste the contents of your `story_world.yaml` here, and your series
`cast.yaml`, before you send this.** Nothing about the characters or the places
is written into this template — that is deliberate. A template that names one
book's furniture will quietly describe that furniture into the next book.

```
<paste books/<your book>/story_world.yaml here>
<paste series/<your series>/cast.yaml here>
```

From those two files:

- Every page must happen in one of the named `settings`, and you must put its
  id in the page's `setting:` field.
- Only characters listed in `cast:` may appear. Use their descriptions for what
  is visible; never invent clothing, hair or features they do not have.
- Obey every `constants:` and `never:` line for the setting a page happens in.
- A character's `rules:` apply wherever they appear.
- A companion toy is NOT automatically in every picture. Put it in frame at
  home, at play, and at the moments the child has to get through something —
  and leave it out of the ordinary ones, so that the page where she picks it
  up carries weight.
- **Do not write clothing into the scene.** Outfits live in `cast.yaml` under
  `wardrobe:`, as named sets — `night`, `summer`, `autumn`, `winter`, `rain` —
  and the book picks one in `story_world.yaml`. The build inserts it into every
  page prompt. Write clothing into a scene as well and the two will disagree.
  If a single page genuinely differs — she puts a coat on to go outside — give
  that page its own `wardrobe: autumn` key instead of describing the coat.

Light must be consistent with whatever light sources that setting has, with the
state of any lamp or door on that page, and must progress sensibly from page to
page.

## Which characters are in frame

Each page also needs a `characters:` list — the ids of the people actually
visible in that picture, and nobody else. A page with no figures gets `[]`.

Keep it short. Each character's reference sheet is attached to the page prompt,
on top of the setting plate and the previous page, and past four attachments the
image model averages faces instead of copying them. If a character is only
present as a hand at the edge of frame, they still count.

## Output format — return exactly this, nothing else

```yaml
  - n: 1
    image: page_01.png
    characters: [<ids from the cast, or [] for a page with no figures>]
    setting: <a setting id from story_world.yaml>
    shot: wide
    angle: eye_level
    scene:
      subject: <who is in the frame, where, how much of them, which way
        they face>
      action: <what her hands, arms, feet are doing, in this instant>
      gaze: <where her eyes are directed>
      expression: <visible facial signs only>
      companion: <where the constant companion is and how they are held or
        placed; omit if this book has none>
      light: <every light source, its direction, colour and strength>
      shadow: <what casts it, where it falls, its size; or "none prominent">
      place: <which elements of the setting are visible, and roughly where in
        frame>
      state: <time of day, and the state of anything that changes across the
        book — a lamp, a door, weather>
```

One block per page, in order, page numbers matching the text.
`image:` is always `page_NN.png` matching the page number.

---

THE STORY TEXT:

<paste the approved page text here>
