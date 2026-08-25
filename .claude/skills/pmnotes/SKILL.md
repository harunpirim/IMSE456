---
name: pmnotes
description: Build a week of IMSE 456/656 course material from a marked-up chapter — the lecture notes, the revealjs deck, the PowerPoint export, the studio sheet, and an HTML version, as one coherent set. Use this whenever the user drops a chapter scan, raw notes, or highlighted PDF into raw_notes/ and asks for notes, slides, a deck, a lab, a studio, or "week N", even if they only name one of those artifacts — they are produced together and drift apart if built separately. Also use when revising an existing week's material.
---

# Building a week

A week of this course is **four artifacts built as one set**, from one source:

| Artifact | Path | Notes |
|---|---|---|
| Lecture notes | `weeks/week-NN.qmd` | the substance; everything else derives from it |
| Deck | `slides/week-NN.qmd` | revealjs on the site |
| PowerPoint | `_pptx/week-NN.pptx` | generated from the deck source; gitignored |
| Studio sheet | `labs/lab-NN.qmd` | the Thursday session |
| HTML | published Artifact | a shareable reading version of the notes |

The user often asks for one of these. Build all five anyway and say so — they are
read side by side, and a deck built a week after its notes contradicts them in
small ways that are annoying to find later.

## Before writing anything, read the whole source

The source lands in `raw_notes/` (gitignored, along with `*.pdf` — **never commit
it**). Read every page before drafting. Partial reads produce notes that are
detailed about the first third and thin after.

While reading, settle two questions:

**Is this scanned textbook pages, or the instructor's own notes?** Highlighted
page images with figure numbers and end-of-chapter questions are the book. That
matters because everything here compiles to a **public** website — see
*Attribution* below.

**Do the figure captions match their figures?** In at least one chapter they were
offset by one, so the level-of-effort chart carried the uncertainty figure's
caption. Match each figure to the concept it actually depicts and tell the user
what you found.

## Attribution — the part that is easy to get wrong

Rewording is not authorship. The structure, the substance, the figures and the
examples are the chapter's, and the page should say so plainly rather than leave
a reader to infer it from a reference list at the bottom.

Every week page carries:

- **A source note at the top**, before the content, naming author, title,
  edition, publisher and chapter, and stating exactly what was done: exposition
  reworded, figures redrawn, questions reproduced as written.
- **A citation on every top-level section**, so a student landing mid-page sees
  the source without scrolling.
- **A credit in every figure caption** — *"Figure redrawn from Larson & Gray,
  Ch. 1, Figure 1.1 [1]."*
- **Inline attribution on quotations**, not just a bracket number.
- **A reference list** at the foot. Claims the chapter borrows from elsewhere —
  the Standish Group, Krasner, PMI — are cited to their own source, not to the
  chapter.

The deck needs its own attribution, because it circulates separately from the
notes: a source aside under the title, per-section asides, and a closing sources
slide.

### Redraw figures, do not reproduce them

Build every figure fresh as inline SVG conveying the same idea. Use
`currentColor` for structure and `#0F5A4B` (the site primary) for emphasis so it
holds in light and dark. Caption it as redrawn.

Where the book's figure encodes a claim you disagree with, redraw it to match the
text and **tell the user you changed it and why**. Example: the socio-technical
yin-yang implies the two dimensions trade off; the text argues you need both, so
two overlapping circles carry the argument better.

### Measure the prose against the source

Do this before committing, every time. Chasing completeness pulls sentences back
toward the source without any decision to copy — it is invisible from inside the
writing, and it happened badly enough once to need a whole rewrite pass.

```bash
pdftotext -layout raw_notes/ch2.pdf raw_notes/ch2.txt
python3 .claude/skills/pmnotes/scripts/check_overlap.py \
  --source raw_notes/ch2.txt --target weeks/week-02.qmd slides/week-02.qmd
```

Under ~2% is fine — quotations, proper nouns, standard definitions. Any single
run over ~25 words is either a quotation that needs marking or a paragraph that
needs rewriting. Judge the passage list, not the headline number.

**End-of-chapter review questions and exercises are reproduced verbatim** — the
instructor holds the matching answer keys — with a note crediting the source.
Exclude that block from the measurement with `--cut`.

## The notes

Organise by the chapter's **own learning objectives** if it states them. It gives
students something to map onto the reading, and it stops the notes drifting into
a personal reorganisation of the material.

Use the site's classes rather than inventing markup: `.week-meta`, `.chips`,
`.case` with a nested `.qn`, `.studio`, `.tutor` / `.editor` / `.roommate`,
`.tabular`. Prose is plain, declarative and unhedged — match it.

Every week's front matter carries the same keys, and **the release date must be
identical across the week, the deck and the studio**, or the three open on
different days:

```yaml
week: 2
release: "2026-08-31"
title: "Week 2 · ..."
chapter: "Larson Ch. 2"
dates: "1 and 3 September"
reading: "Larson Ch. 2"
session-a: "..."      # Tuesday
session-b: "..."      # Thursday — must match the studio's title
video: {provider: none, id: ""}
slides: true
lab: true
```

The Thursday session title appears in **four** places that have to agree:
`session-b`, the `.week-meta` Thursday row, the `.studio` blurb heading, and the
deck's closing slide.

## The studio

Studios are **evaluated inside the Thursday session** — no deadline, nothing
submitted afterwards. Do not reintroduce a due date; the `.week-meta` row reads:

```html
<dt>Studio</dt><dd>Evaluated in the Thursday session — nothing to submit afterwards</dd>
```

Conceptual assignments, final-project deliverables and the midterm **do** keep
their dates. When a week's row lists both, the date belongs to the CA.

The Week 1 studio is the pattern worth following: **do it unaided first, then
bring the model in, then reconcile and account for the difference.** What gets
graded is the reconciliation — where the model was wrong, where it changed your
mind — because that is the part a machine cannot produce. A tight output limit
(one page) is what makes it work; anything longer can be generated without
thinking. Give the student an honest exit: if the model made no errors, they
report that as the finding rather than inventing one.

Every studio ends with the AI acknowledgement block from the syllabus, and the
standing rule: **the check is graded, not the output.**

Do not invent assets. If a sheet tells students to open a supplied file or run a
`verify()` cell, that file must exist in the repo or the session stalls. Build
the studio from tools students install themselves, or ask the user for the asset.

## Generating and verifying

```bash
python3 scripts/check_public.py          # must pass — runs in CI before gate.py
python3 scripts/gate.py --date 2026-08-31   # confirm the week goes live when intended
npm install pptxgenjs                    # once
node scripts/qmd2pptx.js 2               # -> _pptx/week-02.pptx
```

`check_public.py` fails on instructor-facing content in `weeks/`, `slides/` or
`labs/`. If it flags something you wrote, rewrite the phrase — do not loosen the
pattern to get a green build. It catches real leaks; it also catches innocent
phrasing, and rewording costs less than a weakened guard.

The guard only knows the phrasings someone thought of. Read the page once as a
student would before you ship it.

**No `::: {.notes}` blocks in decks.** Speaker notes ship inside the published
HTML and open with `S`. The speaking script belongs in `private/teaching/`.

For the `.pptx`, validate and check geometry — long titles wrapping to two lines
have overflowed their box before. If LibreOffice can render, look at it; if it
cannot, say plainly that no visual pass was possible rather than implying one.

## The HTML

Load the `artifact-design` skill, then publish the notes as an Artifact. Honour
the site's own system rather than inventing one: `#0F5A4B` primary, `#1A2022`
ink, `#5C6A66` muted, Spectral + Source Sans 3 + IBM Plex Mono, all from
`styles.scss`. Keep the same file path across republishes so the URL is stable.

## Week skeletons

Weeks not yet written keep front matter, `.week-meta` and the `<!-- VIDEO -->`
marker and nothing else. `write_schedule()` builds the schedule from front
matter, so those files are what keep every week's row on the schedule and the
semester legible to students. Do not delete them, and do not fill them in
speculatively — each week is written from its own chapter when its turn comes.

## Finishing

Commit the source `.qmd` files; `_pptx/`, `raw_notes/`, `*.pdf` and `private/`
stay out. Send the `.pptx` to the user — it is gitignored, so the copy you
generated is the only one — and give them the Artifact URL.

Then tell them plainly what you did not verify.
