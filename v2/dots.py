"""Draw ways.csv as dots: one dot per way, stacked by year, coloured by binding time, with lineage links.

Hover a dot for all its fields. Run: python3 v2/dots.py [out.svg]   (default: static/dots.svg)
"""
import csv
import re
import sys
from collections import defaultdict
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
X0, X1 = 1960, 2025
S = 85                                  # px per cm of the slide layout this mirrors
DX, DY, R = 0.2 * S, 0.212 * S, 0.088 * S
LEFT, BASE = 40, 470                    # x of 1960, y of the axis

# product-line binding times, merged from the finer lanes of the catalog
BIND = {"design": "design", "authoring": "design", "build": "build", "install": "deploy", "deploy": "deploy",
        "boot": "load", "session": "load", "startup": "load", "runtime": "run", "request": "run"}
ORDER = ["design", "build", "deploy", "load", "run"]
COLOR = {"design": "#9100dc", "build": "#0000dc", "deploy": "#00af3f", "load": "#f08c00", "run": "#f01928"}
LABEL = {"design": "design", "build": "build", "deploy": "deploy", "load": "load (start-up)", "run": "run"}

# the mechanisms variability research mentions most: (label, side of the line, label height in slide cm)
NAMED = {
    "C preprocessor": ("#ifdef", "r", 0.5),
    "CLI options": ("command-line options", "c", 0.95),
    "Environment variables": ("environment variables", "l", 1.4),
    "INI files": ("config files", "l", 1.85),
    "Dynamic plugins (dlopen)": ("plug-ins", "l", 2.25),
    "Feature models (FODA)": ("feature models", "l", 2.65),
    "Strategy pattern": ("design patterns", "l", 3.05),
    "AspectJ": ("aspects", "l", 1.85),
    "Kconfig": ("Linux Kconfig", "l", 3.45),
    "FeatureC++": ("feature modules", "l", 3.85),
    "Feature toggles": ("feature toggles", "l", 4.25),
    "Kubernetes ConfigMap": ("Kubernetes", "r", 2.75),
    "AGENTS.md": ("AGENTS.md", "l", 2.3),
}

rows = list(csv.DictReader(open(HERE / "ways.csv")))
bind = lambda r: BIND[r["binding"].split(";")[0]]
dated = sorted((r for r in rows if r["year"].strip()),
               key=lambda r: (int(r["year"]), r["way"] in NAMED, ORDER.index(bind(r))))
undated = sorted((r for r in rows if not r["year"].strip()), key=lambda r: (ORDER.index(bind(r)), r["way"]))
stacks = defaultdict(list)
for r in dated:
    stacks[int(r["year"])].append(r)

px = lambda year: LEFT + (year - X0) * DX
py = lambda cm: BASE - cm * S
top = {y: len(ws) * 0.212 + 0.06 for y, ws in stacks.items()}   # slide cm

pos = {}
for year, ws in stacks.items():
    for k, r in enumerate(ws):
        pos[r["way"]] = (px(year), py((k + 0.5) * 0.212 + 0.06))
ux = px(X1) + 0.4 * S
for k, r in enumerate(undated):
    pos[r["way"]] = (ux + (k % 4) * DX, py((k // 4 + 0.5) * 0.212 + 0.06))

width, height = int(ux + 4 * DX + 30), BASE + 40
slug = lambda s: re.sub("[^A-Za-z0-9]", "", s)


def tooltip(r):
    keys = ["binding", "binding_detail", "carrier", "expressiveness", "constraints", "set_by", "effect",
            "status", "mechanism", "domain", "origin_type", "versioned", "reload", "layering", "determinism"]
    span = (f"{r['year']}-{r['ended']}" if r["ended"] else r["year"]) or "no clear year"
    links = [f"{f.replace('_', ' ')}: {r[f].replace(';', ', ')}" for f in ("replaces", "inspired_by") if r[f]]
    return f"{r['way']} ({span}, {r['origin']})\n" + "\n".join([f"{k}: {r[k]}" for k in keys if r[k]] + links)


out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
       f'font-family="Helvetica, Arial, sans-serif" font-size="12">',
       '<style>.lk{fill:none;opacity:.35}.lk.on{opacity:1;stroke-width:2}.dot{cursor:pointer}'
       '.dot:hover{stroke:#111;stroke-width:1.5}</style>',
       '<defs><marker id="a1" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
       '<path d="M0,0 L10,5 L0,10 z" fill="#333"/></marker>'
       '<marker id="a2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
       '<path d="M0,0 L10,5 L0,10 z" fill="#888"/></marker></defs>',
       f'<rect width="{width}" height="{height}" fill="white"/>',
       f'<text x="{LEFT}" y="24" font-size="15" font-weight="bold">{len(rows)} ways to configure software</text>',
       f'<text x="{LEFT}" y="44" fill="#555">One dot per way, at the year it appeared. '
       'Colour is the binding time. Hover a dot for all its fields and links.</text>']

# legend
lx = LEFT
for b in ORDER:
    out.append(f'<circle cx="{lx + 5}" cy="63" r="5" fill="{COLOR[b]}"/>'
               f'<text x="{lx + 14}" y="67">{LABEL[b]}</text>')
    lx += 24 + len(LABEL[b]) * 6.5
lx += 16
out.append(f'<line x1="{lx}" y1="63" x2="{lx + 28}" y2="63" stroke="#333" stroke-width="1.3" marker-end="url(#a1)"/>'
           f'<text x="{lx + 34}" y="67">replaces</text>')
lx += 100
out.append(f'<line x1="{lx}" y1="63" x2="{lx + 28}" y2="63" stroke="#888" stroke-width="1.2" stroke-dasharray="3 2" '
           f'marker-end="url(#a2)"/><text x="{lx + 34}" y="67">inspired by</text>')

# axis
out.append(f'<line x1="{LEFT - 10}" y1="{BASE}" x2="{px(X1) + 10}" y2="{BASE}" stroke="#aaa"/>')
for y in range(X0, X1 + 1, 10):
    out.append(f'<line x1="{px(y)}" y1="{BASE}" x2="{px(y)}" y2="{BASE + 5}" stroke="#aaa"/>'
               f'<text x="{px(y)}" y="{BASE + 19}" text-anchor="middle" fill="#666">{y}</text>')
out.append(f'<text x="{ux + 1.5 * DX}" y="{BASE + 19}" text-anchor="middle" fill="#666">no year</text>')

# lineage links, arcing above the dots, under them in the drawing order
for r in rows:
    for field, dashed in (("replaces", False), ("inspired_by", True)):
        for src in filter(None, r[field].split(";")):
            (x1, y1), (x2, y2) = pos[src], pos[r["way"]]
            lift = 25 + 0.25 * abs(x2 - x1)
            mx, my = (x1 + x2) / 2, min(y1, y2) - lift
            style = ('stroke="#888" stroke-width="1.1" stroke-dasharray="3 2" marker-end="url(#a2)"' if dashed
                     else 'stroke="#333" stroke-width="1.3" marker-end="url(#a1)"')
            out.append(f'<path class="lk" data-a="{slug(src)}" data-b="{slug(r["way"])}" '
                       f'd="M{x1:.1f},{y1:.1f} Q{mx:.1f},{my:.1f} {x2:.1f},{y2:.1f}" {style}/>')

# named labels
anchor = {"l": "end", "r": "start", "c": "middle"}
nudge = {"l": 0.08, "r": -0.08, "c": 0.0}
for r in dated:
    if r["way"] in NAMED:
        label, side, ly = NAMED[r["way"]]
        year = int(r["year"])
        x = px(year)
        out.append(f'<line x1="{x:.1f}" y1="{py(top[year] + 0.02):.1f}" x2="{x:.1f}" y2="{py(ly):.1f}" '
                   f'stroke="#999" stroke-width="0.8"/>'
                   f'<text x="{x + nudge[side] * S:.1f}" y="{py(ly) - 3:.1f}" text-anchor="{anchor[side]}" '
                   f'fill="#1f2328"{" font-weight=" + chr(34) + "bold" + chr(34) if r["way"] == "Feature toggles" else ""}>'
                   f'{escape(label)}</text>')

# dots
for r in rows:
    x, y = pos[r["way"]]
    out.append(f'<circle class="dot" data-id="{slug(r["way"])}" cx="{x:.1f}" cy="{y:.1f}" r="{R:.1f}" '
               f'fill="{COLOR[bind(r)]}"><title>{escape(tooltip(r))}</title></circle>')

out.append("</svg>")
dest = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent / "static" / "dots.svg"
dest.write_text("\n".join(out))
print(f"{dest}: {len(rows)} dots, {sum(1 for o in out if 'class=\"lk\"' in o)} links")
