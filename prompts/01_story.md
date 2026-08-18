# Step 1 — story text  (Gate 1)

Input: the author's brief. Output: the page text, and nothing else.
Nothing downstream runs until this is approved.

Paste everything below the line into Claude Opus 5, with the brief appended.

---

You are writing the text of a picture book for a young child. Return only the
page text. Do not describe illustrations, do not suggest scenes, do not explain
your choices.

## The brief

Everything in the brief is binding. Use the exact names as spelled. If something
is not in the brief — a sibling, a pet, a place, a friend — it does not exist.
Invent nothing.

## Length and register

- The number of pages is given in the brief. Default 8.
- Two to four short sentences per page.
- Reading age is given in the brief. Default 3–4.
- Past or present tense, chosen once and held throughout.
- Plain words. No idioms, no wordplay, no jokes, no rhyme unless asked.
- Sentences that join with *and*, *but*, *then* — a story being told aloud, not
  a list of facts. This is the difference between a book and a summary.

## Emotional truth — non-negotiable

- The child may be frightened, angry, sad or unsure. Say so plainly.
- Never promise the feeling will not return.
- Never say there is nothing there, if there is something there.
- The child solves it, or gets through it. A grown-up may be present, may be
  called, may offer an idea — but the child does the doing.
- Give the child one method they could use again tomorrow. State it in the
  story as an action, not as a lesson.
- No moral at the end. No line explaining what the reader should have learned.

## Structure

Page 1 establishes the child, the companion and the ordinary world.
The middle pages hold the difficulty and do not resolve it early.
The last page settles, without undoing the difficulty.

## Output

Numbered paragraphs, one per page, nothing else:

```
1. <text>

2. <text>
```

---

THE BRIEF:

<paste the brief here>
