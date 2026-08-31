#!/usr/bin/env python3
"""qmd2docx.py — render a top-level page to Word, for people who need a file.

The .qmd stays the single source of truth: this reads it and emits a .docx you
can email, print, or hand to a department that asks for the syllabus as a
document. Nothing here is published — the site still serves the HTML version.

    python3 scripts/qmd2docx.py            # syllabus.qmd -> _docx/syllabus.docx
    python3 scripts/qmd2docx.py project    # project.qmd  -> _docx/project.docx
    python3 scripts/qmd2docx.py --all

Two things are fixed on the way out, because they are right for a web page and
wrong for a document:

1. A link to `schedule.qmd` is meaningful on the site and dead in Word, so every
   relative .qmd link is rewritten to its published URL, taken from `site-url`
   in _quarto.yml.
2. The `.week-meta` <dl> flattens into alternating unlabelled paragraphs, which
   for the contact block means twenty of them. It becomes a two-column table.

Both happen in a temp copy; the source tree is never modified, exactly as with
gate.py.

Gating does not apply — these pages carry no `release:` date and are live from
the first build.
"""

import html
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "_docx"
PAGES = ["syllabus", "project", "ai", "index"]

# (schedule.qmd#key-dates) and href="../syllabus.qmd#how-to-disclose" both appear.
MD_LINK = re.compile(r"\]\(((?:\.\./)*)([\w-]+)\.qmd(#[\w-]*)?\)")
HTML_LINK = re.compile(r'href="((?:\.\./)*)([\w-]+)\.qmd(#[\w-]*)?"')

DL_BLOCK = re.compile(r"<dl>(.*?)</dl>", re.S)
DL_ROW = re.compile(r"<dt>(.*?)</dt>\s*<dd>(.*?)</dd>", re.S)


def site_url() -> str:
    cfg = yaml.safe_load((ROOT / "_quarto.yml").read_text())
    url = cfg.get("website", {}).get("site-url", "").rstrip("/")
    if not url:
        sys.exit("qmd2docx: no website.site-url in _quarto.yml")
    return url


def absolutise(text: str, base: str) -> tuple[str, int]:
    """Point every relative .qmd link at the published site."""
    count = 0

    def md(m):
        nonlocal count
        count += 1
        return f"]({base}/{m.group(2)}.html{m.group(3) or ''})"

    def html(m):
        nonlocal count
        count += 1
        return f'href="{base}/{m.group(2)}.html{m.group(3) or ""}"'

    text = MD_LINK.sub(md, text)
    text = HTML_LINK.sub(html, text)
    return text, count


def inline_to_markdown(fragment: str) -> str:
    """The <dd> cells carry <strong> and <a>; everything else is plain text."""
    text = re.sub(r"<a\s+href=\"([^\"]+)\"[^>]*>(.*?)</a>", r"[\2](\1)", fragment, flags=re.S)
    text = re.sub(r"</?(?:strong|b)>", "**", text)
    text = re.sub(r"</?(?:em|i)>", "*", text)
    text = re.sub(r"<[^>]+>", "", text)
    return html.unescape(" ".join(text.split())).replace("|", r"\|")


def tabulate_definitions(text: str) -> tuple[str, int]:
    """A <dl> is a clean two-column layout on the web and loose prose in Word."""
    count = 0

    def convert(m):
        nonlocal count
        rows = DL_ROW.findall(m.group(1))
        if not rows:
            return m.group(0)
        count += 1
        lines = ["| | |", "|:--|:--|"]
        lines += [f"| **{inline_to_markdown(k)}** | {inline_to_markdown(v)} |" for k, v in rows]
        lines.append("")
        lines.append(': {tbl-colwidths="[26,74]"}')
        return "\n".join(lines)

    return DL_BLOCK.sub(convert, text), count


def render(name: str, base: str) -> Path:
    src = ROOT / f"{name}.qmd"
    if not src.exists():
        sys.exit(f"qmd2docx: {src.relative_to(ROOT)} does not exist")

    body, rewritten = absolutise(src.read_text(), base)
    body, tabulated = tabulate_definitions(body)
    OUT.mkdir(exist_ok=True)

    # Render in a temp directory so a stray _files/ directory never lands in the
    # source tree, and so the rewritten copy is thrown away afterwards.
    with tempfile.TemporaryDirectory() as tmp:
        staged = Path(tmp) / f"{name}.qmd"
        staged.write_text(body)
        for asset in ("styles.scss", "images"):
            source = ROOT / asset
            if source.is_dir():
                shutil.copytree(source, Path(tmp) / asset)
            elif source.exists():
                shutil.copy(source, Path(tmp) / asset)

        result = subprocess.run(
            ["quarto", "render", staged.name, "--to", "docx", "--toc"],
            cwd=tmp,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            sys.exit(f"qmd2docx: quarto failed on {name}.qmd\n{result.stderr}")

        produced = Path(tmp) / f"{name}.docx"
        target = OUT / f"{name}.docx"
        shutil.copy(produced, target)

    size = target.stat().st_size // 1024
    print(
        f"  {name}.qmd -> _docx/{name}.docx  ({size} KB, "
        f"{rewritten} links absolutised, {tabulated} fact blocks tabulated)"
    )
    return target


def main() -> None:
    args = [a for a in sys.argv[1:] if a != "--all"]
    names = PAGES if "--all" in sys.argv else (args or ["syllabus"])
    base = site_url()
    print(f"qmd2docx · links resolve against {base}")
    for name in names:
        render(name.removesuffix(".qmd"), base)


if __name__ == "__main__":
    main()
