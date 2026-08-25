#!/usr/bin/env python3
"""
gate.py — build-time release gating for the IMSE 456/656 course site.

Copies the source tree to _build/, then in that copy:
  * replaces the body of any week / slide / lab whose `release:` date is in the
    future with a short "opens on ..." stub,
  * expands the <!-- VIDEO --> marker into the right embed for each week's
    `video.provider`,
  * regenerates schedule.qmd from every week's front matter.

The source tree is never modified, so this is safe to run locally.

    python3 scripts/gate.py                      # gate as of today, America/Chicago
    python3 scripts/gate.py --date 2026-10-06    # preview the site as it will look in Week 7
    python3 scripts/gate.py --all                # ungate everything (end-of-term archive)
    quarto preview _build                        # then look at it

Requires: pyyaml
"""
from __future__ import annotations
import argparse, datetime as dt, pathlib, re, shutil, sys

try:
    import yaml
except ImportError:
    sys.exit("gate.py needs pyyaml:  pip install pyyaml")

try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("America/Chicago")
except Exception:                                    # pragma: no cover
    TZ = None

ROOT   = pathlib.Path(__file__).resolve().parent.parent
BUILD  = ROOT / "_build"
SKIP   = {"_build", "_site", ".quarto", "_freeze", ".git", "__pycache__", ".venv",
          "private"}   # private/ holds answer keys — never let it near a build tree
FM     = re.compile(r"\A---\n(.*?)\n---\n(.*)\Z", re.S)


def read_fm(path: pathlib.Path):
    m = FM.match(path.read_text(encoding="utf8"))
    if not m:
        return None, None, None
    try:
        meta = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return None, None, None
    return meta, m.group(1), m.group(2)


def video_block(meta: dict) -> str:
    v = meta.get("video") or {}
    provider = str(v.get("provider", "none")).lower()
    vid = str(v.get("id") or "").strip()
    title = meta.get("title", "Lecture recording")
    if provider == "youtube" and vid:
        return (f'{{{{< video https://www.youtube.com/embed/{vid} '
                f'title="{title}" aria-label="Recorded lecture: {title}" >}}}}\n')
    if provider == "kaltura" and vid:
        return ('::: {.callout-note appearance="simple"}\n'
                f'**Recorded lecture** — [watch on NDSU Kaltura]({vid}) '
                "(NDSU login required).\n:::\n")
    if provider in ("file", "local") and vid:
        return f'{{{{< video {vid} title="{title}" >}}}}\n'
    return ('::: {.callout-note appearance="simple"}\n'
            "**Recording** — posts after the session.\n:::\n")


def stub(meta: dict) -> str:
    a = meta.get("session-a") or ""
    b = meta.get("session-b") or ""
    plan = ""
    if a or b:
        rows = []
        if a:
            rows.append(f"<dt>Tuesday</dt><dd>{a}</dd>")
        if b:
            rows.append(f"<dt>Thursday</dt><dd>{b}</dd>")
        if meta.get("reading"):
            rows.append(f"<dt>Reading</dt><dd>{meta['reading']}</dd>")
        plan = ("\n\n::: {.week-meta}\n<dl>\n" + "\n".join(rows) + "\n</dl>\n:::\n")
    return ('::: {.gated}\n'
            '<span class="lock">Not posted yet</span>\n\n'
            'Notes, slides, and the recording for this week are not published yet.\n:::\n'
            f'{plan}\n'
            "See the [schedule](../schedule.qmd) for everything that is live now.\n")


def as_date(v) -> dt.date | None:
    if isinstance(v, dt.date):
        return v
    if isinstance(v, str):
        try:
            return dt.date.fromisoformat(v.strip())
        except ValueError:
            return None
    return None


def copy_tree() -> None:
    """Refresh _build/ from the source tree.

    Prefers a clean rebuild, but falls back to overwriting in place on systems
    where the directory cannot be removed (some sandboxed or synced volumes).
    """
    if BUILD.exists():
        try:
            shutil.rmtree(BUILD)
        except (PermissionError, OSError):
            pass
    shutil.copytree(ROOT, BUILD, dirs_exist_ok=True,
                    ignore=lambda d, names: [n for n in names if n in SKIP])


def gate(today: dt.date, ungate_all: bool) -> tuple[list[dict], dict]:
    weeks = []
    assets: dict[str, dict[int, str]] = {"slides": {}, "labs": {}}
    for sub in ("weeks", "slides", "labs"):
        folder = BUILD / sub
        if not folder.is_dir():
            continue
        for path in sorted(folder.glob("*.qmd")):
            meta, fm_text, body = read_fm(path)
            if meta is None:
                continue
            rel = as_date(meta.get("release"))
            gated = bool(rel and not ungate_all and rel > today)

            if sub == "weeks":
                weeks.append({"meta": meta, "file": path.name,
                              "release": rel, "gated": gated})
            elif not gated:
                # week number from the filename: slides/week-05.qmd, labs/lab-05.qmd
                n = re.search(r"(\d+)", path.stem)
                if n:
                    assets[sub][int(n.group(1))] = path.name

            if gated:
                body = stub(meta)
            else:
                body = body.replace("<!-- VIDEO -->", video_block(meta))
            path.write_text(f"---\n{fm_text}\n---\n\n{body}", encoding="utf8")
    return weeks, assets


def write_schedule(weeks: list[dict], assets: dict) -> None:
    weeks.sort(key=lambda w: w["meta"].get("week", 0))
    rows = []
    for w in weeks:
        m, n = w["meta"], w["meta"].get("week", 0)
        title = re.sub(r"^Week \d+ · ", "", str(m.get("title", "")))
        links = []
        if not w["gated"]:
            links.append(f'[notes](weeks/{w["file"]})')
            if assets["slides"].get(n):
                links.append(f'[slides](slides/{assets["slides"][n]})')
            if assets["labs"].get(n):
                links.append(f'[studio](labs/{assets["labs"][n]})')
        rows.append(
            f'| <span class="tabular">{n:02d}</span> '
            f'| <span class="tabular">{m.get("dates","")}</span> '
            f'| {title} | {m.get("reading","—") or "—"} '
            f'| {" · ".join(links)} |')

    body = f"""---
title: "Schedule"
subtitle: "IMSE 456/656 · Fall 2026"
toc: false
---

Tuesday and Thursday, 3:30–4:45 p.m., Ag Hill Center 240. Notes, slides, and studio sheets
appear in the last column as each week is posted.

| Wk | Sessions | Topic | Reading | Resources |
|:--|:--|:--|:--|:--|
{chr(10).join(rows)}

: {{tbl-colwidths="[6,18,36,20,20]"}}

## Key dates

| Date | What |
|:--|:--|
| <span class="tabular">Tue 25 Aug</span> | First class |
| <span class="tabular">Fri 11 Sep</span> | FP0 — team formed, industry partner confirmed |
| <span class="tabular">Fri 2 Oct</span> | FP1 — project charter and WBS |
| <span class="tabular">Thu 15 Oct</span> | **Midterm**, in class, closed notes, no computers |
| <span class="tabular">Fri 30 Oct</span> | FP2 — schedule model and budget baseline |
| <span class="tabular">Fri 20 Nov</span> | FP3 — risk register and EVM status report |
| <span class="tabular">Thu 26 Nov</span> | *No class — Thanksgiving* |
| <span class="tabular">Tue 8 &amp; Thu 10 Dec</span> | Final presentations |
| <span class="tabular">Fri 11 Dec</span> | Final report and Medium article due, 11:59 p.m. |

: {{tbl-colwidths="[24,76]"}}

## Assignments

**Conceptual assignments (CA1–CA8, 25%)** close Sunday 11:59 p.m. Lowest score dropped.

**Studio assignments (SA1–SA14, 25%)** are evaluated **in the Thursday session** — no deadline,
nothing to submit afterwards. Graded complete or incomplete. Two lowest dropped.

**Late work is not accepted** for the work that has a deadline: conceptual assignments and the
final project deliverables.
"""
    (BUILD / "schedule.qmd").write_text(body, encoding="utf8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Gate the IMSE 456 site by release date.")
    ap.add_argument("--date", help="Pretend today is this date (YYYY-MM-DD).")
    ap.add_argument("--all", action="store_true", help="Publish every week regardless of date.")
    args = ap.parse_args()

    if args.date:
        today = dt.date.fromisoformat(args.date)
    elif TZ:
        today = dt.datetime.now(TZ).date()
    else:
        today = dt.date.today()

    copy_tree()
    weeks, assets = gate(today, args.all)
    write_schedule(weeks, assets)

    live = [w for w in weeks if not w["gated"]]
    print(f"gate.py · today={today} · {len(live)}/{len(weeks)} weeks live")
    for w in weeks:
        mark = "  live" if not w["gated"] else f"gated→{w['release']}"
        print(f"  week {w['meta'].get('week'):02d}  {mark}")


if __name__ == "__main__":
    # Die quietly when piped into `head`, the way a normal Unix tool does.
    try:
        import signal
        if hasattr(signal, "SIGPIPE"):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    except Exception:
        pass
    main()
