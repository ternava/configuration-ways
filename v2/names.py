"""Draw names.csv as a universe: one cluster per name given to a unit of variability
(option, flag, key, feature, variation point...), one dot per way that uses that name, coloured by binding time.

Run: python3 v2/names.py [out.svg]   (default: static/names.svg)
"""
import csv
import math
import sys
from collections import defaultdict
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
BIND = {"design": "design", "authoring": "design", "build": "build", "install": "deploy", "deploy": "deploy",
        "boot": "load", "session": "load", "startup": "load", "runtime": "run", "request": "run"}
ORDER = ["design", "build", "deploy", "load", "run"]
COLOR = {"design": "#9100dc", "build": "#0000dc", "deploy": "#00af3f", "load": "#f08c00", "run": "#f01928"}
LABEL = {"design": "design", "build": "build", "deploy": "deploy", "load": "load (start-up)", "run": "run"}
W, H, TOP = 1250, 860, 90       # canvas, and room for the header
STEP, DOT = 7.2, 4.6            # phyllotaxis spacing and dot radius inside a cluster

ways = {r["way"]: r for r in csv.DictReader(open(HERE / "ways.csv"))}
names = list(csv.DictReader(open(HERE / "names.csv")))
groups = defaultdict(list)
for n in names:
    groups[n["term"]].append(n)
bind = lambda w: BIND[ways[w]["binding"].split(";")[0]]

# each cluster is a disc of dots with its name underneath; pack the boxes along an outward spiral
clusters = []
for term, ms in sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0])):
    ms.sort(key=lambda m: ORDER.index(bind(m["way"])))
    n = len(ms)
    r = STEP * math.sqrt(n) + DOT
    fs = 11 + 9 * min(n, 28) / 28
    w = max(2 * r, len(term) * fs * 0.56) + 10
    h = 2 * r + fs + 10
    clusters.append({"term": term, "ms": ms, "r": r, "fs": fs, "w": w, "h": h})

placed = []
cx0, cy0 = W / 2, TOP + (H - TOP) / 2
for c in clusters:
    t = 0.0
    while True:
        x = cx0 + 1.75 * 4.0 * t * math.cos(t) - c["w"] / 2
        y = cy0 + 4.0 * t * math.sin(t) - c["h"] / 2
        box = (x, y, x + c["w"], y + c["h"])
        inside = box[0] > 10 and box[2] < W - 10 and box[1] > TOP and box[3] < H - 10
        if inside and not any(box[0] < b[2] and b[0] < box[2] and box[1] < b[3] and b[1] < box[3] for b in placed):
            placed.append((box[0] - 4, box[1] - 4, box[2] + 4, box[3] + 4))
            c["x"], c["y"] = x + c["w"] / 2, y + c["r"] + 2
            break
        t += 0.05
        if t > 400:
            raise SystemExit(f"no room for {c['term']}")

# trim the empty band the spiral leaves above and below
lo, hi = min(b[1] for b in placed), max(b[3] for b in placed)
for c in clusters:
    c["y"] += TOP + 6 - lo
H = int(hi - lo + TOP + 20)

out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="Helvetica, Arial, sans-serif" font-size="12">',
       '<style>.dot{cursor:pointer}.dot:hover{stroke:#111;stroke-width:1.5}.term{cursor:default}</style>',
       f'<rect width="{W}" height="{H}" fill="white"/>',
       f'<text x="20" y="26" font-size="15" font-weight="bold">{len(groups)} names for a unit of variability</text>',
       f'<text x="20" y="46" fill="#555">What each of the {len(names)} ways calls the thing you can vary. '
       'One dot per way, grouped by that name, coloured by binding time. Hover a dot or a name.</text>']
lx = 20
for b in ORDER:
    out.append(f'<circle cx="{lx + 5}" cy="66" r="5" fill="{COLOR[b]}"/><text x="{lx + 14}" y="70">{LABEL[b]}</text>')
    lx += 24 + len(LABEL[b]) * 6.5

for c in clusters:
    for i, m in enumerate(c["ms"]):
        a, rr = i * 2.39996, STEP * math.sqrt(i + 0.5) if len(c["ms"]) > 1 else 0
        x, y = c["x"] + rr * math.cos(a), c["y"] + rr * math.sin(a)
        tip = f"{m['way']}\ncalled: {m['term']}" + (f"\nalso: {m['also']}" if m["also"] else "")
        out.append(f'<circle class="dot" cx="{x:.1f}" cy="{y:.1f}" r="{DOT}" fill="{COLOR[bind(m["way"])]}">'
                   f'<title>{escape(tip)}</title></circle>')
    listing = f"{c['term']}: {len(c['ms'])} way{'s' * (len(c['ms']) > 1)}\n" + "\n".join(m["way"] for m in c["ms"])
    out.append(f'<text class="term" x="{c["x"]:.1f}" y="{c["y"] + c["r"] + c["fs"] + 2:.1f}" text-anchor="middle" '
               f'font-size="{c["fs"]:.1f}" fill="#1f2328">{escape(c["term"])}'
               f'{f" <tspan fill=\"#888\" font-size=\"{c["fs"] * 0.75:.1f}\">{len(c["ms"])}</tspan>" if len(c["ms"]) > 1 else ""}'
               f'<title>{escape(listing)}</title></text>')

out.append("</svg>")
dest = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent / "static" / "names.svg"
dest.write_text("\n".join(out))
print(f"{dest}: {len(groups)} names, {len(names)} ways")
