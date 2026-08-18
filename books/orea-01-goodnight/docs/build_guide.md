# Orea and the Click — build guide

Tool: **Gemini image generation (Nano Banana)**, in a normal chat. **Not Storybook.**
Storybook cannot accept prior pages as input, which is the whole mechanism here.

Work in ONE long chat. Do not start new chats between pages.

---

## PRE-FLIGHT

1. **Rename your reference file.** The last run printed the filename into the story text
   on page 10. Rename it to `reference.png`. Nothing descriptive, nothing with words
   the model can mistake for content.
2. Have these ready as separate files: the reference room image, and nothing else.
3. Turn off any "search the web" tool in the chat. It only adds noise.

---

## STEP 1 — Build the character sheet (one generation)

Attach `reference.png`. Send this:

> Using the attached image only as a guide to the girl and the toy dog, draw a
> CHARACTER REFERENCE SHEET on a plain white background.
>
> Show, side by side, with clear space between them:
> 1. The girl, standing, full body, facing forward.
> 2. The same girl, standing, full body, in profile facing left.
> 3. The girl's head and shoulders, larger, facing forward.
> 4. The toy dog on its own, sitting, facing forward.
> 5. The toy dog on its own, lying on its side.
>
> The girl is four years old. She has blonde wavy shoulder-length hair, rosy cheeks,
> and blue eyes. She wears pale blue button-up pyjamas, long sleeves, long trousers,
> plain with no pattern. She is barefoot.
>
> The toy dog is a soft beige stuffed dog with very long floppy ears, a small black
> nose, a red collar, and a small navy blue bow on the top of his head.
>
> Style: soft watercolour with fine ink linework, muted natural colours, gentle
> realism, warm and calm. Early-twentieth-century English picture book tradition.
> Do not imitate or reference any specific named book, character or franchise.
>
> Plain white background. No room, no furniture, no scenery. No text, no letters,
> no numbers, no labels anywhere in the image.

**Accept only when:** hair, pyjama colour, ear length, collar and bow are all clear
and consistent between the views. Re-roll until they are. Everything downstream
inherits this, so do not compromise here.

Save the result as `charsheet.png`.

---

## STEP 2 — Build the room plate (one generation)

Attach `reference.png`. Send this:

> Draw an empty child's bedroom at night. No people, no toys, no animals in this picture.
>
> The room: white walls, a plain brown wooden door on the left standing slightly open,
> one window with a cream roll-up blind, a tall white wardrobe, a wooden bookshelf,
> a lilac table with a matching lilac chair, plain wooden floorboards, and a small
> pale round rug.
>
> Layout, follow exactly: a child's wooden bed with a plain LIGHT BLUE blanket sits against
> the right-hand wall. The lilac table stands directly beside the bed, within arm's
> reach of a child lying in it. A small lamp stands on the lilac table. The tall white
> wardrobe stands against the same wall behind the lilac table. The window is on the
> far wall. Outside the window is a bare tree.
>
> The lamp on the lilac table is switched ON, casting warm yellow light.
>
> Style: soft watercolour with fine ink linework, muted natural colours, gentle
> realism, warm and calm. Early-twentieth-century English picture book tradition.
> Do not imitate or reference any specific named book, character or franchise.
>
> No text, no letters, no numbers anywhere in the image. No pictures or frames on
> the walls.

**Accept only when:** the lilac table is beside the bed AND in front of the wardrobe.
That geometry is what makes pages 4 and 10 work — the table has to be the thing that
throws the tall shadow up the wardrobe wall.

Save as `room.png`.

---

## STEP 3 — Generate the ten pages, chained

For **every** page, attach exactly three images:

| Slot | File | Role |
|---|---|---|
| 1 | `charsheet.png` | who Orea and Whoof-Whoof are |
| 2 | `room.png` | what the room is |
| 3 | `page_NN.png` — the approved image for the page immediately before this one | what the last page looked like |

**Slot 3, precisely:**

- Save each page the moment you approve it, named `page_01.png`, `page_02.png`, and so on.
- When generating page N, slot 3 is always `page_(N-1).png` — the one page directly
  before it. Generating page 6 means attaching `page_05.png`.
- **Attach one previous page only, never several.** Adding more dilutes the reference
  and the character starts averaging out.
- If you re-rolled a page, attach the version you approved. Never attach a rejected one.
- **Page 1 has no previous page.** Attach only slots 1 and 2 for it.

There are **two** blocks below. Block A is pasted once, for page 1 only, because page 1
has no previous page to point at. Block B is pasted for pages 2 to 10, unchanged, every
single time. The only difference between them is the IMAGE ROLES paragraph — everything
after it is identical.

Paste the whole block, then the page's own scene line underneath. Do not shorten the
block on later pages. Shortening it is what caused the drift last time.

---

### BLOCK A — page 1 only. Attach `charsheet.png` and `room.png`.

> Draw one illustration for a children's picture book. Portrait format.
>
> IMAGE ROLES: Image 1 is the character sheet — the girl is Orea and the beige toy dog
> is Whoof-Whoof. Copy their appearance from it exactly. Image 2 is the room — copy the
> room, the furniture, the layout and the colours from it exactly. There are two
> attached images only. There is no third image.
>
> This is the first page of the book. Every later page will be matched to it, so keep
> the style clean and simple enough to repeat.
>
> NEVER CHANGE THESE:
> - The walls are white. The door is brown. The wardrobe is white. The table and
>   chair are lilac. The blanket is plain LIGHT BLUE with no pattern, no flowers, no
>   patchwork and no stripes. The blind is cream.
> - Orea has blonde wavy hair and plain pale blue pyjamas.
> - Whoof-Whoof is beige with very long floppy ears, a red collar and a navy bow.
>   He appears in every illustration. He is never lost, never dropped, never swapped
>   for another toy, never damaged.
>
> SHADOWS: shadows are flat, soft-edged and completely featureless. Never draw a face,
> eyes, a mouth, teeth, claws, fingers or hands in a shadow. A shadow is never a
> creature and never looks like one.
>
> STYLE: soft watercolour with fine ink linework, muted natural colours, gentle realism,
> warm and calm. Early-twentieth-century English picture book tradition. Do not imitate
> or reference any specific named book, character, illustrator or franchise. Do not put
> any other book's characters, toys, pictures or merchandise anywhere in the room.
>
> NEVER: no text, no letters, no words, no numbers anywhere in the image, including
> on book spines and inside picture frames. No pictures or frames on the walls.
> Do not mention or refer to the attached files or their names.
>
> THE SCENE FOR THIS PAGE:
> It is evening and the lamp on the lilac table is switched on, filling the room with
> warm yellow light. Orea stands on the wooden floor of her bedroom, facing us, holding
> Whoof-Whoof in both arms against her chest. She is calm and happy. Show the whole
> room around her — the brown door, the window with the cream blind, the white wardrobe,
> the lilac table and chair, and her bed with the plain light blue blanket.

That is the complete page 1 prompt. Nothing else to add — the scene line is already
inside it.

**Judge page 1 harder than any other page.** It is doing the
job that Image 3 does everywhere else, so every later page inherits its style, its light
and its colours. Re-roll it until it is right. Once you approve it and save it as
`page_01.png`, do not go back and re-roll it — everything after it would have to be
redone.

---

### BLOCK B — pages 2 to 10. Attach `charsheet.png`, `room.png`, and the previous page.

> Draw one illustration for a children's picture book. Portrait format.
>
> IMAGE ROLES: Image 1 is the character sheet — the girl is Orea and the beige toy dog
> is Whoof-Whoof. Copy their appearance from it exactly. Image 2 is the room — copy the
> room, the furniture, the layout and the colours from it exactly. Image 3 is the
> previous page of this same book — match its style, its lighting and its colours
> exactly, so the two pages look like they were painted by the same artist on the
> same day.
>
> NEVER CHANGE THESE:
> - The walls are white. The door is brown. The wardrobe is white. The table and
>   chair are lilac. The blanket is plain LIGHT BLUE with no pattern, no flowers, no
>   patchwork and no stripes. The blind is cream.
> - Orea has blonde wavy hair and plain pale blue pyjamas.
> - Whoof-Whoof is beige with very long floppy ears, a red collar and a navy bow.
>   He appears in every illustration. He is never lost, never dropped, never swapped
>   for another toy, never damaged.
>
> SHADOWS: shadows are flat, soft-edged and completely featureless. Never draw a face,
> eyes, a mouth, teeth, claws, fingers or hands in a shadow. A shadow is never a
> creature and never looks like one.
>
> STYLE: soft watercolour with fine ink linework, muted natural colours, gentle realism,
> warm and calm. Early-twentieth-century English picture book tradition. Do not imitate
> or reference any specific named book, character, illustrator or franchise. Do not put
> any other book's characters, toys, pictures or merchandise anywhere in the room.
>
> NEVER: no text, no letters, no words, no numbers anywhere in the image, including
> on book spines and inside picture frames. No pictures or frames on the walls.
> Do not mention or refer to the attached files or their names.
>
> THE SCENE FOR THIS PAGE:

### Page scene lines

Page 1's scene line is already built into Block A above — don't paste it twice.
Each line below goes directly underneath Block B, after `THE SCENE FOR THIS PAGE:`.

**1.** It is evening and the lamp on the lilac table is switched on, filling the room with warm yellow light. Orea stands on the wooden floor of her bedroom, facing us, holding Whoof-Whoof in both arms against her chest. She is calm and happy. Show the whole room around her — the brown door, the window with the cream blind, the white wardrobe, the lilac table and chair, and her bed with the plain light blue blanket.

**2.** Mum's hand is just leaving the lamp on the lilac table and the lamp is now off. Mum is sitting on the bed, looking at Orea with a warm smile and wishing her a good night. Orea is looking at her Mom with a warm smile. The room has gone grey and dim. Orea lies in her bed with the teal blanket, Whoof-Whoof under her arm, eyes open.

**3.** The room is dim and grey, the door is closed. Orea sitting up in her bed holding Whoof-Whoof, her chin lifted a little, her face steady and decided. The plain grey shapes are still on the white wall behind her, quiet and featureless.

**4.** Orea leaning out of her bed in the dim room, one arm stretched out towards the lamp on the lilac table, her other arm holding Whoof-Whoof tight against her. Her fingertips are just touching the lamp.

**5.** The lamp on the lilac table is ON and the room is warm and yellow again. The shapes are gone from the white wall. The lilac table stands where the tall shape had been, and beside it are her bookshelf with books and a few soft toys. Orea looking back at the wall holding Whoof-Whoof, and see there is no shape of the tree.

**6.** The room is warm, the lamp is turned ON. Orea is standing in front of the door, on the round beige carpet, in front of the bed. She looks at the door, holding Whoof-whoof by one hand, another hand opens the door holding the holder. We see Orea from her back, she leaves the gap through which the light from the corridor is projected on the floor. The door is narrowly opened.

**7.** The room is dim, the door is narrowly opened and through the gap the warm light is projected making the room slightly dim and warm. Orea holding Whoof-Whoof is standing at the lilac table and leaning towards the lamp, turning it OFF. The lamp is turned off. The shade from the tree on the wall next to the door is projected again, but it is dimmed and slightly grey. Orea is not scared, she is smiling and feel good about herself. 

**8.** The room is dim, the door is narrowly opened, the dimmed light is coming through the door's gap. Orea is in bed holding Whoof-Whoof with eyes closed, warm light smile on the face. She is asleep. Nothing to fear.

## STEP 4 — Check every page before moving on

Do not generate page N+1 until page N passes all of these. If it fails, re-roll page N.
A bad page becomes the reference for the next one and the error compounds.

- [ ] Blanket is plain LIGHT BLUE. Not floral, not patchwork, not white, not green.
- [ ] Walls white, door brown, wardrobe white, table and chair lilac.
- [ ] Whoof-Whoof present, beige, long ears, red collar, navy bow.
- [ ] Orea's hair and pyjamas match the character sheet.
- [ ] No shadow has a face, fingers, hands, eyes or claws.
- [ ] No text anywhere, including book spines and frames.
- [ ] No other book's characters, toys or pictures anywhere in the room.
- [ ] Room layout matches `room.png`.

---

## STEP 5 — Assemble

Once all ten pass, hand the ten files back and I'll lay them out as a PDF —
illustration left, text right, matching your existing book.

---

## RUN LOG — observed degradation, ChatGPT image generation

Recorded from the first full chained run. These are what actually happened, not predictions.

**The chain works. It is not free.** Character and room consistency held across all pages —
Orea, Whoof-Whoof, the red collar, the blue bow, the room layout, the furniture positions.
This is a genuine improvement over both Canva and Storybook, which could not hold three
pages. But it required **multiple iterations per page**. A page rarely came back correct
on the first generation. Budget re-rolls for every page, not just the difficult ones.

**Consistency and instruction-following are two different problems, and the chain only
fixes the first.** Holding the look steady does not make the model obey the scene line.
Concrete example from this run: the scene line specified *"Mum is seen only from behind,
walking out through the brown door, and her face is not visible."* The model produced Mum
seated on the edge of the bed, facing the viewer, full face, in a jumper and trousers.
Every consistency rule was honoured and the actual instruction was ignored. Re-rolling
does not reliably fix this; rewriting the scene line does.

**Prompt adherence degrades on negative and restrictive instructions.** "Do not show her
face", "seen only from behind", "no person in the doorway" are the instructions most often
dropped. Positive instructions — draw this, put that here — survive far better. Where a
page depends on something *not* being shown, expect to fight for it, and consider removing
the element from the illustration entirely rather than spending five re-rolls on it.

**Wall colour drifts with lighting and does not fully return.** The walls read white in the
lamp-on pages and blue-grey in the dim pages. Some of that is legitimate night lighting,
but the drift exceeds it — the dim pages are bluer than the light level alone explains.
Wardrobe tone moves between cream and grey the same way.

**Resolution ceiling.** Generated pages came out around 1000–1150 pixels wide. That is
comfortable for a screen PDF and **too small for print** — roughly 3.5 inches wide at
300 dpi. Print requires either upscaling or regenerating at a higher resolution.

---

## WHAT WILL PROBABLY STILL GO WRONG

**Pages 7 and 8 are the danger zone.** In the last run those were the two worst pages.
Chaining should fix it, but watch them hardest.

**Page 2 is the riskiest by design** because it needs Mum. Any person other than Orea
invites the model to invent a character and a name. If it misbehaves, cut Mum from
the illustration entirely — show only the switched-off lamp and the open door — and
let the words carry her.

**Text continuity worth deciding now:** page 4 puts the tall shape on the wall beside
the wardrobe, and page 10 says the lilac table stood where that shape had been. Those
only agree if the table sits between the bed and the wardrobe wall. Step 2 forces that
layout. If you'd rather change the words instead, page 10 could read "there was her
lilac table, standing in front of the wardrobe just as it always did".
