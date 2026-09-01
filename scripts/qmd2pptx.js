#!/usr/bin/env node
/**
 * qmd2pptx.js — turn a revealjs slide source into a PowerPoint deck.
 *
 * The .qmd under slides/ stays the single source of truth: this reads it and
 * emits a .pptx you can present from offline, in PowerPoint or Keynote, with no
 * browser and no network. Nothing here is published — the site still serves the
 * revealjs version.
 *
 *   npm install pptxgenjs          # once
 *   node scripts/qmd2pptx.js 1     # writes _pptx/week-01.pptx
 *   node scripts/qmd2pptx.js --all
 *
 * Understood from the source: `#` section divider, `##` slide, `-`/`1.` lists,
 * `>` quote, pipe tables, ::: {.aside} callouts, and **bold** / *italic* /
 * `code` inline. Reveal's `. . .` fragment markers are dropped — a printed
 * slide has no increments. A `<figure>` holding an inline SVG is rasterized
 * with Playwright's Chromium when that is installed, and falls back to a
 * captioned placeholder box when it is not — so the export works either way,
 * and says which you got.
 *
 *   npm install playwright     # optional: turns the placeholders into figures
 */
const fs = require("fs");
const path = require("path");
const PptxGenJS = require("pptxgenjs");

const GREEN = "0F5A4B";      // $primary, matches styles.scss
const INK = "1A2022";        // $body-color
const MUTED = "5C6A66";      // $secondary
const TINT = "F1F7F4";       // the .tutor callout wash
const RULE = "D5DBD7";
const YELLOW = "FFC72C";     // NDSU yellow, used only as an accent
const SERIF = "Cambria";     // metric-safe stand-ins for Spectral / Source Sans 3
const SANS = "Calibri";

const W = 13.33, H = 7.5, M = 0.9;

// ---------------------------------------------------------------- parsing

function frontMatter(text) {
  const m = /^---\n([\s\S]*?)\n---\n/.exec(text);
  if (!m) return [{}, text];
  const meta = {};
  for (const line of m[1].split("\n")) {
    const kv = /^(\w[\w-]*):\s*(.*)$/.exec(line);
    if (kv) meta[kv[1]] = kv[2].replace(/^["']|["']$/g, "");
  }
  return [meta, text.slice(m[0].length)];
}

/** Split the body into slides at `#` (section) and `##` (content) headings. */
function parseSlides(body) {
  const slides = [];
  let cur = null;
  for (const line of body.split("\n")) {
    const h = /^(#{1,2})\s+(.*)$/.exec(line);
    if (h) {
      if (cur) slides.push(cur);
      cur = { section: h[1].length === 1, title: h[2].trim(), lines: [] };
    } else if (cur) {
      cur.lines.push(line);
    }
  }
  if (cur) slides.push(cur);
  return slides.map((s) => ({ ...s, blocks: parseBlocks(s.lines) }));
}

/** Group a slide's lines into typed blocks. */
function parseBlocks(lines) {
  const blocks = [];
  let i = 0;
  const isTable = (l) => /^\s*\|.*\|\s*$/.test(l);
  while (i < lines.length) {
    const line = lines[i];
    if (!line.trim() || /^\s*\.\s*\.\s*\.\s*$/.test(line)) { i++; continue; }

    if (/^::: *\{\.aside\}/.test(line)) {
      const buf = [];
      i++;
      while (i < lines.length && !/^:::/.test(lines[i])) buf.push(lines[i++]);
      i++;
      blocks.push({ type: "aside", text: buf.join(" ").trim() });
      continue;
    }
    if (/^:::/.test(line)) { i++; continue; }

    // A raw <figure> wraps an inline SVG, which has no PowerPoint equivalent
    // here. Swallow the markup and keep the figure's accessible title, so the
    // slide says what is missing instead of printing the SVG source.
    if (/^\s*<figure\b/.test(line)) {
      const buf = [];
      while (i < lines.length && !/<\/figure>/.test(lines[i])) buf.push(lines[i++]);
      if (i < lines.length) buf.push(lines[i++]);
      const raw = buf.join("\n");
      const t = /<title[^>]*>([\s\S]*?)<\/title>/.exec(raw);
      const svg = /<svg[\s\S]*<\/svg>/.exec(raw);
      blocks.push({ type: "figure", text: t ? t[1].trim() : "Figure",
                    svg: svg ? svg[0] : null });
      continue;
    }

    if (isTable(line)) {
      const rows = [];
      while (i < lines.length && isTable(lines[i])) {
        const cells = lines[i].trim().replace(/^\||\|$/g, "").split("|").map((c) => c.trim());
        if (!cells.every((c) => /^:?-{2,}:?$/.test(c) || c === "")) rows.push(cells);
        i++;
      }
      blocks.push({ type: "table", rows });
      continue;
    }
    if (/^\s*>/.test(line)) {
      const buf = [];
      while (i < lines.length && /^\s*>/.test(lines[i])) buf.push(lines[i++].replace(/^\s*>\s?/, ""));
      blocks.push({ type: "quote", text: buf.join(" ").trim() });
      continue;
    }
    if (/^\s*([-*]|\d+\.)\s+/.test(line)) {
      const items = [];
      while (i < lines.length && /^\s*([-*]|\d+\.)\s+/.test(lines[i])) {
        const m = /^(\s*)([-*]|\d+\.)\s+(.*)$/.exec(lines[i]);
        items.push({ text: m[3].trim(), indent: Math.floor(m[1].length / 2), num: /\d/.test(m[2]) });
        i++;
        // fold hanging continuation lines into the item above
        while (i < lines.length && lines[i].trim() && !/^\s*([-*]|\d+\.)\s+/.test(lines[i])
               && !isTable(lines[i]) && /^\s{2,}/.test(lines[i])) {
          items[items.length - 1].text += " " + lines[i].trim();
          i++;
        }
      }
      blocks.push({ type: "list", items });
      continue;
    }
    const buf = [];
    while (i < lines.length && lines[i].trim() && !isTable(lines[i])
           && !/^\s*([-*]|\d+\.)\s+/.test(lines[i]) && !/^:::/.test(lines[i])
           && !/^\s*<figure\b/.test(lines[i])
           && !/^\s*>/.test(lines[i]) && !/^\s*\.\s*\.\s*\.\s*$/.test(lines[i])) {
      buf.push(lines[i++]);
    }
    if (buf.length) blocks.push({ type: "para", text: buf.join(" ").trim() });
  }
  return blocks;
}

/** **bold** / *italic* / `code` -> pptxgenjs rich-text runs. */
function runs(md, base = {}) {
  const out = [];
  const re = /(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g;
  let last = 0, m;
  const push = (text, opts) => { if (text) out.push({ text, options: { ...base, ...opts } }); };
  while ((m = re.exec(md))) {
    push(md.slice(last, m.index), {});
    const tok = m[0];
    if (tok.startsWith("**")) push(tok.slice(2, -2), { bold: true });
    else if (tok.startsWith("`")) push(tok.slice(1, -1), { fontFace: "Consolas", color: GREEN });
    else push(tok.slice(1, -1), { italic: true });
    last = re.lastIndex;
  }
  push(md.slice(last), {});
  return out.length ? out : [{ text: md, options: base }];
}

const plain = (md) => md.replace(/\*\*|\*|`/g, "");

// ---------------------------------------------------------------- rendering

function titleSlide(pptx, meta) {
  const s = pptx.addSlide();
  s.background = { color: GREEN };
  // bottom-anchored and tall enough for a two-line title: one-line titles keep
  // the same baseline, long ones grow upward instead of spilling over.
  s.addText(runs(meta.title || "Untitled", { fontSize: 40, bold: true, color: "FFFFFF", fontFace: SERIF }),
    { x: M, y: 1.6, w: W - 2 * M, h: 1.9, valign: "bottom", margin: 0 });
  if (meta.subtitle)
    s.addText(meta.subtitle, { x: M, y: 3.6, w: W - 2 * M, h: 0.5,
      fontSize: 20, color: TINT, fontFace: SANS, margin: 0 });
  s.addShape(pptx.ShapeType.rect, { x: M, y: 4.35, w: 1.1, h: 0.05, fill: { color: YELLOW } });
  const foot = [meta.author, meta.date].filter(Boolean).join("  ·  ");
  if (foot)
    s.addText(foot, { x: M, y: 4.7, w: W - 2 * M, h: 0.4,
      fontSize: 14, color: "C8D8D2", fontFace: SANS, margin: 0 });
}

function sectionSlide(pptx, slide) {
  const s = pptx.addSlide();
  s.background = { color: GREEN };
  s.addText(runs(slide.title, { fontSize: 34, bold: true, color: "FFFFFF", fontFace: SERIF }),
    { x: M, y: 3.0, w: W - 2 * M, h: 1.4, valign: "middle", margin: 0 });
}

function contentSlide(pptx, slide, meta, num) {
  const s = pptx.addSlide();
  s.background = { color: "FFFFFF" };
  s.addText(runs(slide.title, { fontSize: 30, bold: true, color: GREEN, fontFace: SERIF }),
    { x: M, y: 0.55, w: W - 2 * M, h: 0.85, valign: "top", margin: 0 });

  let y = 1.65;
  const bottom = H - 0.85;
  const asides = slide.blocks.filter((b) => b.type === "aside");
  const body = slide.blocks.filter((b) => b.type !== "aside");
  const room = bottom - (asides.length ? 0.5 : 0);

  for (const b of body) {
    if (y >= room - 0.2) break;
    if (b.type === "table") {
      const [head, ...rest] = b.rows;
      const rows = [
        head.map((c) => ({ text: plain(c), options: { bold: true, color: "FFFFFF", fill: { color: GREEN } } })),
        ...rest.map((r, i) =>
          r.map((c) => ({ text: plain(c), options: { fill: { color: i % 2 ? "FFFFFF" : TINT } } }))),
      ];
      const h = Math.min(rows.length * 0.42, room - y);
      s.addTable(rows, { x: M, y, w: W - 2 * M, h, colW: null,
        fontSize: 14, fontFace: SANS, color: INK, valign: "middle",
        border: { type: "solid", color: RULE, pt: 1 }, margin: 6 });
      y += h + 0.3;
    } else if (b.type === "quote") {
      const h = 0.5 + 0.32 * Math.ceil(plain(b.text).length / 78);
      s.addShape(pptx.ShapeType.rect, { x: M, y, w: 0.045, h, fill: { color: GREEN } });
      s.addText(runs(b.text, { fontSize: 19, italic: true, color: INK, fontFace: SERIF }),
        { x: M + 0.28, y, w: W - 2 * M - 0.28, h, valign: "middle", margin: 0 });
      y += h + 0.3;
    } else if (b.type === "figure") {
      if (b.png) {
        const box = figureBox(b.svg, W - 2 * M, room - y - 0.15);
        s.addImage({ data: b.png, x: (W - box.w) / 2, y, w: box.w, h: box.h,
                     altText: b.text });
        y += box.h + 0.3;
      } else {
        const h = Math.min(1.6, room - y);
        s.addShape(pptx.ShapeType.rect, { x: M, y, w: W - 2 * M, h,
          fill: { color: TINT }, line: { color: RULE, width: 1, dashType: "dash" } });
        s.addText(runs(b.text + " — diagram, see the web deck",
                       { fontSize: 15, italic: true, color: MUTED, fontFace: SANS }),
          { x: M + 0.3, y, w: W - 2 * M - 0.6, h, valign: "middle", align: "center", margin: 0 });
        y += h + 0.3;
      }
    } else if (b.type === "list") {
      const items = b.items.map((it, i) => ({
        text: runs(it.text, { fontSize: 17, color: INK, fontFace: SANS }),
        options: { bullet: it.num ? { type: "number" } : true,
                   indentLevel: it.indent, paraSpaceAfter: 8,
                   breakLine: i < b.items.length - 1 },
      }));
      const flat = [];
      for (const it of items) it.text.forEach((r, j) =>
        flat.push({ text: r.text, options: { ...r.options, ...(j === 0 ? it.options : { breakLine: false }),
                    ...(j === it.text.length - 1 ? { breakLine: it.options.breakLine } : { breakLine: false }) } }));
      const h = Math.min(b.items.reduce((a, it) =>
        a + 0.34 * Math.ceil(plain(it.text).length / 88) + 0.12, 0.1), room - y);
      s.addText(flat, { x: M, y, w: W - 2 * M, h, valign: "top", margin: 0 });
      y += h + 0.25;
    } else {
      const h = Math.min(0.34 * Math.ceil(plain(b.text).length / 92) + 0.12, room - y);
      s.addText(runs(b.text, { fontSize: 17, color: INK, fontFace: SANS }),
        { x: M, y, w: W - 2 * M, h, valign: "top", margin: 0 });
      y += h + 0.25;
    }
  }

  for (const a of asides)
    s.addText(runs(a.text, { fontSize: 11, color: MUTED, fontFace: SANS, italic: true }),
      { x: M, y: bottom - 0.42, w: W - 2 * M, h: 0.4, valign: "bottom", margin: 0 });

  s.addText(meta.subtitle || "", { x: M, y: H - 0.55, w: W - 2 * M - 0.6, h: 0.3,
    fontSize: 10, color: MUTED, fontFace: SANS, margin: 0 });
  s.addText(String(num), { x: W - M - 0.5, y: H - 0.55, w: 0.5, h: 0.3,
    fontSize: 10, color: MUTED, fontFace: SANS, align: "right", margin: 0 });
}

// ---------------------------------------------------------------- figures

/**
 * Rasterize each figure's SVG to a PNG, in one browser for the whole run.
 * Optional by design: without Playwright installed the blocks keep `png`
 * unset and render as placeholder boxes instead.
 *
 * The deck's SVGs are sized in reveal's 1280x720 stage, which is exactly the
 * 13.33x7.5in slide at 96dpi — so a figure's px height maps straight onto
 * inches, and `figureBox` below can size it without guessing.
 */
async function renderFigures(blocks) {
  const figs = blocks.filter((b) => b.type === "figure" && b.svg);
  if (!figs.length) return true;

  let chromium;
  try { ({ chromium } = require("playwright")); } catch { return false; }

  // Playwright pins a browser build its own version expects; this repo's
  // container may carry a different one, so fall back to whatever is there.
  let exe;
  try {
    exe = chromium.executablePath();
    if (!fs.existsSync(exe)) exe = undefined;
  } catch { /* not downloaded */ }
  if (!exe) {
    const root = process.env.PLAYWRIGHT_BROWSERS_PATH || "";
    const dir = root && fs.existsSync(root)
      ? fs.readdirSync(root).filter((d) => /^chromium-/.test(d)).sort().pop() : null;
    if (dir) {
      const c = path.join(root, dir, "chrome-linux", "chrome");
      if (fs.existsSync(c)) exe = c;
    }
  }

  let browser;
  try { browser = await chromium.launch(exe ? { executablePath: exe } : {}); }
  catch { return false; }

  try {
    const page = await browser.newPage({ deviceScaleFactor: 2 });
    for (const b of figs) {
      const [w, h] = svgBox(b.svg);
      // INK resolves the SVGs' currentColor the way the deck's body text does
      await page.setContent(
        `<body style="margin:0;color:#${INK}">` +
        `<div id="f" style="width:${w}px;height:${h}px">${b.svg}</div>`);
      const shot = await page.locator("#f").screenshot({ omitBackground: true });
      b.png = "data:image/png;base64," + shot.toString("base64");
    }
    return true;
  } finally { await browser.close(); }
}

/** Natural px size of a figure: its inline height, and the viewBox ratio. */
function svgBox(svg) {
  const vb = /viewBox="0 0 ([\d.]+) ([\d.]+)"/.exec(svg);
  const px = /height:\s*(\d+)px/.exec(svg);
  const h = px ? Number(px[1]) : 400;
  const ratio = vb ? Number(vb[1]) / Number(vb[2]) : 1.6;
  return [Math.round(h * ratio), h];
}

/** Fit a figure into the room left on the slide, at 96dpi and centred. */
function figureBox(svg, maxW, maxH) {
  const [pw, ph] = svgBox(svg);
  let w = pw / 96, h = ph / 96;
  const k = Math.min(1, maxW / w, maxH / h);
  return { w: w * k, h: h * k };
}

// ---------------------------------------------------------------- driver

async function build(src, destDir) {
  const [meta, body] = frontMatter(fs.readFileSync(src, "utf8"));
  const pptx = new PptxGenJS();
  pptx.layout = "LAYOUT_WIDE";
  pptx.author = meta.author || "";
  pptx.title = meta.title || path.basename(src, ".qmd");

  const slides = parseSlides(body);
  const blocks = slides.flatMap((s) => s.blocks);
  const drawn = await renderFigures(blocks);
  const figs = blocks.filter((b) => b.type === "figure").length;
  if (figs && !drawn)
    console.warn(`  ${figs} figure(s) left as placeholders — \`npm install playwright\` to draw them`);

  titleSlide(pptx, meta);
  let n = 1;
  for (const slide of slides) {
    if (slide.section) sectionSlide(pptx, slide);
    else contentSlide(pptx, slide, meta, ++n);
  }
  fs.mkdirSync(destDir, { recursive: true });
  const out = path.join(destDir, path.basename(src, ".qmd") + ".pptx");
  return pptx.writeFile({ fileName: out }).then(() => out);
}

const root = path.resolve(__dirname, "..");
const dest = path.join(root, "_pptx");
const args = process.argv.slice(2);
const srcs = args.includes("--all")
  ? fs.readdirSync(path.join(root, "slides")).filter((f) => f.endsWith(".qmd")).sort()
      .map((f) => path.join(root, "slides", f))
  : args.map((a) => path.join(root, "slides", `week-${String(a).padStart(2, "0")}.qmd`));

if (!srcs.length) {
  console.error("usage: node scripts/qmd2pptx.js <week-number>... | --all");
  process.exit(1);
}
(async () => {
  for (const s of srcs) {
    if (!fs.existsSync(s)) { console.error(`no such deck: ${path.relative(root, s)}`); continue; }
    console.log(`${path.relative(root, await build(s, dest))}`);
  }
})();
