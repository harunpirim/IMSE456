#!/usr/bin/env python3
"""
check_public.py — fail the build if instructor-facing content reaches the public tree.

Gating is a release schedule, not a privacy boundary: every page under weeks/,
slides/ and labs/ is compiled into public HTML and served to students. Speaker
notes ship inside the deck's own HTML and open with `S`. So teaching plans,
facilitation timings, and the answers an in-class activity is meant to surface
have to live in private/, which is gitignored and excluded from _build.

This is the check that keeps them there.

    python3 scripts/check_public.py     # exit 1 on any hit

Run it before pushing; CI runs it ahead of gate.py.
"""
from __future__ import annotations
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PUBLIC = ("weeks", "slides", "labs")

# (pattern, why it must not be public)
RULES: list[tuple[str, str]] = [
    (r"::: *\{\.notes\}", "revealjs speaker notes ship in the published HTML and open with S"),
    (r"^#{2,6} +In-class activity", "facilitation plan, and it usually names the answer"),
    (r"^#{2,6} +Assessment hook", "tells students what the exam is going to ask"),
    (r"put this on the board", "instructor staging direction"),
    (r"\bdebrief\b(?! on the course)", "instructor facilitation language"),
    (r"\b(give|giv(e|ing)) students\b", "addresses the instructor, not the reader"),
    (r"\b(make|have|ask|tell|show|give) students\b", "addresses the instructor, not the reader"),
    # "the class" as an audience, but not "the class base rate" (a reference class)
    (r"\b(ask|tell|show|give|remind|poll) the class\b", "addresses the instructor, not the reader"),
    (r"\bstudents (assume|always|conflate|garble|do this|should be able|making)\b",
     "talks about students in the third person"),
    (r"\bteams (must|build|crash|work|score|design)\b", "facilitation instruction"),
    (r"\bhand out\b", "facilitation instruction"),
    (r"\bbe honest with students\b", "addresses the instructor"),
    (r"\bpedagogic(al)?\b", "authoring commentary"),
    (r"\bthe (lesson|debrief) is\b", "gives away what the activity is meant to surface"),
    (r"\bworth \d+ minutes of lecture\b", "authoring commentary"),
    (r"private/", "path into the private tree"),
]

COMPILED = [(re.compile(p, re.I | re.M), why) for p, why in RULES]


def main() -> int:
    hits = 0
    for sub in PUBLIC:
        for path in sorted((ROOT / sub).glob("*.qmd")):
            text = path.read_text(encoding="utf8")
            lines = text.split("\n")
            for rx, why in COMPILED:
                for m in rx.finditer(text):
                    n = text[: m.start()].count("\n") + 1
                    print(f"{path.relative_to(ROOT)}:{n}: {m.group(0).strip()!r} — {why}")
                    print(f"    {lines[n - 1].strip()[:110]}")
                    hits += 1
    if hits:
        print(f"\n{hits} instructor-facing item(s) in the public tree. "
              f"Move them to private/ — the site is public and gating does not hide them.")
        return 1
    print(f"check_public: clean — no instructor-facing content in {'/, '.join(PUBLIC)}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
