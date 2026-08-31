# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Quarto website — the course site for IMSE 456/656 (Project Management, NDSU, Fall 2026),
published to <https://harunpirim.github.io/IMSE456>. There is no application code: the "build"
is a Python pre-processor (`scripts/gate.py`) followed by `quarto render`.

## Commands

```bash
pip install -r scripts/requirements.txt   # pyyaml, the only dependency
```

```bash
python3 scripts/gate.py                   # gate as of today (America/Chicago), writes _build/
```

```bash
python3 scripts/gate.py --date 2026-10-06 # preview the site as students see it that day
```

```bash
python3 scripts/gate.py --all             # ungate everything (end-of-term archive)
```

```bash
quarto preview _build                     # ALWAYS preview _build, never the repo root
```

```bash
python3 scripts/check_public.py           # fails if instructor content reached weeks/slides/labs
```

```bash
npm install pptxgenjs                     # once
node scripts/qmd2pptx.js 1                # slides/week-01.qmd -> _pptx/week-01.pptx
node scripts/qmd2pptx.js --all
```

```bash
python3 scripts/qmd2docx.py               # syllabus.qmd -> _docx/syllabus.docx
python3 scripts/qmd2docx.py project ai    # any top-level page
```

`gate.py` prints a per-week live/gated table. Read that output before pushing any change to a
`release:` date. There are no tests; the gate output plus a visual pass in `quarto preview` is
the verification loop.

## The two-tree model — the thing to understand first

The repo root is **source**. `_build/` is a **derived copy** that `gate.py` rewrites, and it is
the only tree Quarto should ever render. `gate.py` copies root → `_build/` (skipping `_build`,
`_site`, `.quarto`, `_freeze`, `.git`, `__pycache__`, `.venv`, `private`) and then, in the copy
only:

1. **Gates** any file under `weeks/`, `slides/`, or `labs/` whose `release:` date is in the
   future — the body is replaced by a "Not posted yet" stub built from its front matter.
2. **Expands** the literal `<!-- VIDEO -->` marker in ungated pages into a YouTube embed, a
   Kaltura callout, or a "posts after the session" placeholder, per the page's `video:` block.
3. **Generates `schedule.qmd`** from every week's front matter, plus a hand-maintained key-dates
   table that lives *inside the `write_schedule()` f-string in `scripts/gate.py`*.

**No page ever announces a future date.** A gated week says only that it is not posted yet, and
its schedule row leaves the Resources column empty. This is deliberate — the release dates are a
build input, not a promise to students. Do not reintroduce "opens on ..." copy.

The schedule's **Resources** column is the one index students use: for each released week it emits
`notes · slides · studio`, including only the pieces that actually exist and are released
(week 3 has no deck, weeks 8 and 16 have no lab). Additional per-week resources belong in this
column — extend the `links` list in `write_schedule()`.

Consequences that bite:

- **`schedule.qmd` does not exist in the source tree.** It is referenced by the navbar in
  `_quarto.yml`, so rendering the repo root produces a site with a broken Schedule link. Editing
  the schedule table, the key dates, or the assignment blurb means editing `write_schedule()`,
  not a `.qmd`. (`_site/` at the root is a stale artifact of doing this wrong; it is gitignored.)
- **The source tree is never modified by `gate.py`**, so running it locally is always safe.
- **Gating is cosmetic, not access control.** A gated week's `.qmd` is still readable in this
  public repo. Nothing with an answer in it may live here (see "Content boundary").

## Directories that are not part of the site

- `private/` — **gitignored and excluded from `_build`.** Holds the live-session decks with case
  answers in them, and `private/teaching/week-NN.md`, the teaching plans. Nothing here may ever be
  committed or published.
- `raw_notes/` — gitignored, along with `*.pdf`. Source material a week is written *from*
  (marked-up chapter scans and the like) stays out of the repository; only the notes written from
  it are committed.

## Current state of the content — read this before assuming a week exists

**Only Week 1 has a body.** Weeks 2–16 are deliberately reduced to a skeleton: front matter, the
`.week-meta` block, and the `<!-- VIDEO -->` marker, and nothing else. `labs/` and `slides/` hold
only `lab-01.qmd` and `week-01.qmd`.

Each week is written from its own marked-up chapter (dropped into the gitignored `raw_notes/`)
shortly before it opens, following the Week 1 pattern: notes, deck and studio produced as one set.

The skeleton exists because `write_schedule()` builds the schedule table from every week's front
matter — so all sixteen rows keep showing week number, dates, title and chapter, and students keep
the map of the semester, while the Resources column stays empty until the pieces exist. Do not
delete those files, and do not "helpfully" fill them in.

`slides:`/`lab:` still read `true` on weeks whose deck and studio have not been written yet. Those
keys are documentation of intent, not wiring — nothing reads them, and the schedule's Resources
column tests for the file on disk.

## Front matter contract

Week pages (`weeks/week-NN.qmd`) drive everything downstream. All sixteen carry the same keys:

```yaml
week: 5                       # int; sorts the schedule table
release: "2026-09-21"         # ISO date; gates the page and its slides/lab
title: "Week 5 · ..."         # the "Week N · " prefix is stripped for the schedule row
chapter: "Larson Ch. 5"       # "—" for non-content weeks
dates: "22 and 24 September"  # free text, rendered in the schedule
reading: "Larson Ch. 5"
session-a: "..."              # Tuesday; reused in the gated stub
session-b: "..."              # Thursday; reused in the gated stub
video: {provider: none|youtube|kaltura|file, id: ""}
slides: true                  # declarative only — not read by gate.py
lab: true                     # declarative only — not read by gate.py
```

Labs carry `title`, `subtitle`, `week`, `release` — mirror the week's `release` date so the pair
opens together. Slide decks now carry `week` and `release` too, so a deck gates with its week
instead of staying reachable by direct URL while the week is locked. All three dates for a week
must match; `check_public.py` does not verify this, so check it by eye when you move a date.

`slides:`/`lab:` are documentation for the author, not wiring — the actual links are hand-written
markdown in the week body (`../labs/lab-05.qmd`, `../slides/week-05.qmd`). Weeks 8 and 16 declare
`lab: true` with no lab file (midterm and final presentations); weeks 3, 8, 9, 14, 16 have no deck.

Adding a recording: set `provider: youtube` and `id:` to the 11-character ID (Kaltura takes the
full watch URL in `id:`), leave the `<!-- VIDEO -->` marker in place, push.

## Publishing

`.github/workflows/publish.yml` runs on push to `main`, daily at `0 11 * * *` UTC, and on
`workflow_dispatch`. It installs pyyaml, runs `gate.py`, renders with **Quarto pinned to 1.6.43**,
and pushes `_build/_site` to the `gh-pages` branch. Two standing caveats: the cron is UTC and
DST-blind (06:00 Central, 05:00 after 1 November), and GitHub disables scheduled workflows after
60 days of repository inactivity — over a long break the daily release build silences itself.

The locally installed Quarto is older than the CI pin; if something renders here but not in CI (or
vice versa), check the version before chasing the markup.

## Writing conventions

Prose style across the site is plain, declarative, and unhedged — match it. Content pages compose
a small set of custom classes defined in `styles.scss`; use these rather than inventing markup:

- `.week-meta` — the `<dl>` fact block at the top of a week or lab page
- `.chips` / `.chip` — the "concepts introduced" row
- `.case` with a nested `.qn` — a case vignette and its discussion question
- `.studio` — the Thursday studio callout on a week page
- `.part` — a numbered section of a lab sheet
- `.tutor` / `.editor` / `.roommate` — the three AI-role callouts
- `.tabular` — tabular-nums wrapper for dates and numbers in tables
- `.gated`, `.lock`, `.pill*` — generated or schedule-only; do not hand-author

Raw HTML inside `:::` divs is normal here. Cross-directory links use relative paths
(`../syllabus.qmd#how-to-disclose`). Slide decks are revealjs and inherit `slides/_metadata.yml`.

Every lab sheet repeats the assignment's AI level from the Generative AI Acceptable Use Scale
(studios are Level 4, the final project Level 5, midterm and conceptual assignments Level 1). If
you touch that policy, it appears in three places — `syllabus.qmd`, `ai.qmd`, and each lab's
`.week-meta` block — and they must agree.

## Content boundary

**Gating is a release schedule, not a privacy boundary.** Everything under `weeks/`, `slides/` and
`labs/` compiles to public HTML that students read. Making the repo private would not change this —
it would only hide the `.qmd` source (and on a Free plan it disables GitHub Pages outright, since
Pages from a private repo needs Pro/Team/Enterprise; even on Pro the published site stays public).
So the boundary is enforced by *what goes in the file*, not by repo visibility.

Two consequences that have already bitten once:

- **Revealjs speaker notes are public.** A `::: {.notes}` block ships inside the deck's own HTML and
  any viewer can open it with `S`. Decks must contain no `.notes` blocks; the speaking script lives
  in `private/teaching/`.
- **Write for the student, always.** No facilitation plans, timings, "In-class activity" or
  "Assessment hook" sections, and nothing in the third person about students. Activity write-ups
  routinely name the answer they are meant to surface ("almost every team omits contingency"), which
  is the actual leak. Those live in `private/teaching/week-NN.md`.

`scripts/check_public.py` enforces both and runs in CI ahead of `gate.py`. If it fails, move the
content to `private/` — do not loosen the pattern to get a green build.

Never add: solution keys, exam items, auto-marking scripts, anything derived from the Larson
instructor manual or image library, or any student name, grade, submitted work, or recording
(FERPA). Those live in a separate private repository.

## Slides: two outputs, one source

`slides/week-NN.qmd` is the single source. Quarto renders it to revealjs for the site;
`scripts/qmd2pptx.js` renders the same file to `_pptx/week-NN.pptx` for presenting offline. `_pptx/`
is generated and gitignored — never commit or publish it, and never hand-edit a `.pptx` (the next
run overwrites it). The converter reads `#`/`##` headings, lists, quotes, pipe tables, `.aside`
callouts and inline `**bold**`/`*italic*`/`` `code` ``; it drops reveal's `. . .` fragment markers,
since a printed slide has no increments. Its palette is pinned to `styles.scss` (`#0F5A4B`), using
Cambria/Calibri as metric-safe stand-ins for Spectral/Source Sans 3.

`scripts/qmd2docx.py` does the same job for a top-level page: `syllabus.qmd` → `_docx/syllabus.docx`,
for anyone who asks for the syllabus as a document rather than a URL. `_docx/` is generated and
gitignored on the same terms. It fixes two things that are right on a web page and wrong in Word —
relative `.qmd` links become published URLs, and the `.week-meta` `<dl>` becomes a two-column table
instead of twenty loose paragraphs. Both happen in a temp copy, so the source tree is untouched.
Word populates the table of contents when it opens the file; it looks empty until then.
