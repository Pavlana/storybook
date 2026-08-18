# Step 4 — cover

Output: `art/page_00.png`.

Generate the cover **last**, once the interior pages exist. It is the one image
that has to represent the whole book, and you cannot judge that until you have
seen the book.

Attach: `art/charsheet.png`, the style reference from your pack, and two or
three finished interior pages you are happy with.

---

Draw the COVER illustration for a children's picture book.

IMAGE ROLES
The character sheet shows the cast — copy their appearance from it exactly. The
other attached images are finished interior pages from this same book: match
their style, palette, light and level of detail exactly. Do not copy any of
their compositions; the cover is a new image.

THE COVER
A single warm, inviting image of the lead character with their constant
companion. Show them together, calm and appealing, looking towards the viewer.
This is the image that makes a parent pick the book up.

Do not illustrate the story's problem. No fear, no darkness, no tension, no
moment from the plot. The cover is the promise, not the plot.

COMPOSITION
Portrait format, 3:4. Keep every character whole and inside the frame with a
generous margin — nothing may touch or run off any edge.

Leave the right-hand third of the image quiet and uncluttered. The title is set
beside the image, and a busy edge there fights it.

NEVER
No text, no letters, no words, no numbers, no title, no author name anywhere in
the image. The title is typeset by the build script, not painted.

---

## Accept only when

- The cast matches the character sheet.
- The style matches the interior pages, not just approximately.
- Nothing is cropped at any edge.
- There is no text in the image, including on any object.
- It gives nothing away about the difficulty in the story.

Save as `art/page_00.png`, then `python3 bin/build.py --dir books/<book> --all`.
