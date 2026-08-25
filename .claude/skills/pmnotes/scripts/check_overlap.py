#!/usr/bin/env python3
"""
check_overlap.py — how much of a page is lifted verbatim from its source?

Writing a week from a marked-up chapter pulls prose toward the source without
anyone deciding to copy anything. It happens most when you are chasing
completeness: you reach for the chapter to check a detail and the sentence comes
back with it. Eyeballing does not catch this — the drift is invisible from
inside. Measuring does.

The check: normalise both texts, slide an n-word window over the page, and flag
every run of n or more consecutive words that also appears in the source.

    python3 check_overlap.py --source raw_notes/ch2.txt --target weeks/week-02.qmd

Front matter, inline SVG, HTML tags and (optionally) an attributed block are
stripped before comparison, so what you measure is the exposition.

Reading the number:

    under ~2%   fine — quotations, proper nouns, standard definitions
    2-5%        look at the passages; some are probably unmarked
    over 5%     transcription, not writing. Rewrite the long runs.

Length matters more than the percentage. Any single run over ~25 words is either
a quotation that needs marking or a paragraph that needs rewriting. Judge the
passage list, not the headline figure.

A source PDF becomes text with:  pdftotext -layout source.pdf source.txt
"""
from __future__ import annotations
import argparse, pathlib, re, sys

TAG   = re.compile(r"<[^>]+>")
SVG   = re.compile(r"<svg.*?</svg>", re.S)
STYLE = re.compile(r"<style.*?</style>", re.S)
FM    = re.compile(r"\A---\n.*?\n---\n", re.S)


def normalise(text: str) -> list[str]:
    text = text.lower().replace("’", "'").replace("‘", "'").replace("`", "'")
    text = re.sub(r"[^a-z0-9' ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip().split()


def strip_markup(text: str, cut: str | None = None) -> str:
    text = STYLE.sub(" ", text)
    text = SVG.sub(" ", text)
    text = FM.sub(" ", text)
    if cut:
        text = re.sub(cut, " ", text, flags=re.S)
    return TAG.sub(" ", text)


def runs(target: list[str], source_ngrams: set[str], n: int) -> list[str]:
    """Maximal stretches of target that live inside the source."""
    found, i = [], 0
    while i <= len(target) - n:
        if " ".join(target[i:i + n]) in source_ngrams:
            j = i
            while j <= len(target) - n and " ".join(target[j:j + n]) in source_ngrams:
                j += 1
            found.append(" ".join(target[i:j + n - 1]))
            i = j
        else:
            i += 1
    return found


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", required=True, help="plain text of the chapter")
    ap.add_argument("--target", required=True, nargs="+", help="page(s) to check")
    ap.add_argument("-n", type=int, default=8, help="run length that counts as a match (default 8)")
    ap.add_argument("--cut", help="regex of a region to exclude, e.g. an attributed question block")
    ap.add_argument("--fail-over", type=float, default=None,
                    help="exit 1 if overlap exceeds this percentage")
    a = ap.parse_args()

    src = pathlib.Path(a.source)
    if not src.exists():
        print(f"source not found: {src}", file=sys.stderr)
        return 2
    words = normalise(src.read_text(encoding="utf8", errors="replace"))
    ngrams = {" ".join(words[i:i + a.n]) for i in range(len(words) - a.n + 1)}

    worst = 0.0
    for path in a.target:
        p = pathlib.Path(path)
        target = normalise(strip_markup(p.read_text(encoding="utf8"), a.cut))
        if len(target) < a.n:
            print(f"{p}: too short to check"); continue
        found = runs(target, ngrams, a.n)
        hit = sum(len(s.split()) for s in found)
        pct = 100 * hit / len(target)
        worst = max(worst, pct)
        print(f"\n{p}: {hit}/{len(target)} words in runs of >={a.n} ({pct:.1f}%), {len(found)} passage(s)")
        for s in sorted(found, key=len, reverse=True):
            w = len(s.split())
            mark = "  <-- rewrite or mark as a quotation" if w >= 25 else ""
            print(f"    [{w:3d}w] {s[:100]}{mark}")

    if a.fail_over is not None and worst > a.fail_over:
        print(f"\nFAIL: {worst:.1f}% exceeds --fail-over {a.fail_over}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
