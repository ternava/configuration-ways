"""Draw ways.csv as a history: binding-time lanes, lineage, lifelines, events, and decade trends."""
import csv
import sys
from collections import Counter
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
LANES = ["design", "authoring", "build", "install", "deploy", "boot", "session", "startup", "runtime", "request"]
Y0, Y1, NOW = 1958, 2027, 2026
LEFT, PX_YEAR, ROW, CHAR = 110, 30, 17, 6.0
TOP = 150

DOMAINS = {
    "parameters in code": "#e15759", "conditional compilation": "#f28e2b", "code generation and templates": "#edc948",
    "composition and plugins": "#b07aa1", "build options": "#9c755f", "computing environment": "#4e79a7",
    "command-line arguments": "#d37295", "environment variables": "#ff9da7", "configuration files": "#59a14f",
    "settings stores and services": "#76b7b2", "per-request selection": "#499894", "variability models": "#bab0ac",
    "tool and agent instructions": "#7b3294",
}
ORIGINS = ["open-source", "vendor", "research", "standard", "community"]

rows = list(csv.DictReader(open(HERE / "ways.csv")))
events = list(csv.DictReader(open(HERE / "events.csv")))
dated = [r for r in rows if r["year"]]
by_name = {r["way"]: r for r in rows}


def x(year):
    return LEFT + (year - Y0) * PX_YEAR


def marker(kind, cx, cy, r, fill, stroke, title):
    t = f"<title>{escape(title)}</title>"
    style = f'fill="{fill}" stroke="{stroke}" stroke-width="1.4"'
    if kind == "vendor":
        return f'<rect x="{cx-r}" y="{cy-r}" width="{2*r}" height="{2*r}" {style}>{t}</rect>'
    if kind == "research":
        return f'<polygon points="{cx},{cy-r-1} {cx+r+1},{cy+r} {cx-r-1},{cy+r}" {style}>{t}</polygon>'
    if kind == "standard":
        return f'<polygon points="{cx},{cy-r-1.5} {cx+r+1.5},{cy} {cx},{cy+r+1.5} {cx-r-1.5},{cy}" {style}>{t}</polygon>'
    if kind == "community":
        return f'<polygon points="{cx-r-1},{cy-r} {cx+r+1},{cy-r} {cx},{cy+r+1}" {style}>{t}</polygon>'
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" {style}>{t}</circle>'


def tooltip(r):
    keys = ["binding", "binding_detail", "carrier", "expressiveness", "constraints", "set_by", "effect",
            "status", "mechanism", "domain", "origin_type", "versioned", "reload", "layering", "determinism"]
    span = f"{r['year']}-{r['ended']}" if r["ended"] else r["year"]
    return f"{r['way']} ({span}, {r['origin']})\n" + "\n".join(f"{k}: {r[k]}" for k in keys)


# place items in lanes, packing rows so labels and lifelines never overlap
items = {lane: [] for lane in LANES}
for r in dated:
    binds = sorted(r["binding"].split(";"), key=LANES.index)
    label = r["way"] + (f"  [{' + '.join(binds)}]" if len(binds) > 1 else "")
    detail = f" ({r['binding_detail']})" if r["binding_detail"] else ""
    for i, b in enumerate(binds):
        items[b].append({"r": r, "year": int(r["year"]), "primary": i == 0,
                         "label": label if i == 0 else "", "detail": detail if i == 0 else ""})

lane_top, y, right_edge = {}, TOP, x(Y1)
for lane in LANES:
    ends = []
    for it in sorted(items[lane], key=lambda i: (i["year"], not i["primary"])):
        start = x(it["year"]) - 8
        end = x(it["year"]) + 12 + len(it["label"] + it["detail"]) * CHAR
        if it["r"]["ended"] and it["primary"]:
            end = max(end, x(int(it["r"]["ended"])) + 10)
        for k, e in enumerate(ends):
            if start > e:
                ends[k] = end
                break
        else:
            k = len(ends)
            ends.append(end)
        it["row"] = k
        right_edge = max(right_edge, end)
    lane_top[lane] = y
    y += max(len(ends), 1) * ROW + 20
lanes_bottom = y
width = int(right_edge) + 40


def cy(lane, it):
    return lane_top[lane] + 16 + it["row"] * ROW


pos = {}
for lane in LANES:
    for it in items[lane]:
        if it["primary"]:
            pos[it["r"]["way"]] = (x(it["year"]), cy(lane, it))

# decade panel geometry
DECADES = list(range(1960, 2030, 10))
PANELS = [
    ("origin_type", "Origin", ["research", "standard", "vendor", "open-source", "community"],
     ["#9c755f", "#4e79a7", "#e15759", "#59a14f", "#bab0ac"]),
    ("versioned", "Versioned with the code", ["in-repo", "both", "external"],
     ["#59a14f", "#edc948", "#e15759"]),
    ("reload", "Change takes effect after", ["n/a", "rebuild", "reinstall", "redeploy", "reboot", "new-session", "restart", "on-signal", "live"],
     ["#d9d9d9", "#08306b", "#08519c", "#2171b5", "#4292c6", "#6baed6", "#9ecae1", "#c6dbef", "#fd8d3c"]),
    ("layering", "Override layers", ["none", "levels", "overlays"], ["#d9d9d9", "#4e79a7", "#f28e2b"]),
    ("determinism", "Effect", ["deterministic", "randomized", "advisory", "interpreted"],
     ["#d9d9d9", "#f28e2b", "#edc948", "#7b3294"]),
]
PW, BAR, PGAP = 300, 16, 80
panel_top = lanes_bottom + 110
height = panel_top + 60 + len(DECADES) * (BAR + 4) + 30 + 18 * 2 + 20
width = max(width, LEFT + len(PANELS) * (PW + PGAP))

out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
       f'font-family="Helvetica, Arial, sans-serif" font-size="11">',
       '<defs>'
       '<marker id="arr" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto">'
       '<path d="M0,0 L8,4 L0,8 z" fill="#333"/></marker>'
       '<marker id="arr2" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto">'
       '<path d="M0,0 L8,4 L0,8 z" fill="#999"/></marker></defs>',
       f'<rect width="{width}" height="{height}" fill="white"/>',
       f'<text x="{LEFT}" y="30" font-size="18" font-weight="bold">A timeline of ways to configure software</text>',
       f'<text x="{LEFT}" y="50" fill="#555">{len(rows)} ways by year of appearance and binding time. '
       'Color is the mechanism, with the number of ways in each. Hover a mark for all its fields.</text>']

# legends
lx = LEFT
mech_count = Counter(r["mechanism"] for r in rows)
for name, color in DOMAINS.items():
    text = f"{name} ({mech_count[name]})"
    out.append(f'<rect x="{lx}" y="66" width="11" height="11" fill="{color}"/>'
               f'<text x="{lx+15}" y="76">{escape(text)}</text>')
    lx += 22 + len(text) * 6.0
lx = LEFT
for kind in ORIGINS:
    out.append(marker(kind, lx + 5, 96, 4.5, "#888", "#555", kind) + f'<text x="{lx+15}" y="100">{kind}</text>')
    lx += 30 + len(kind) * 6.2
lx += 20
legend2 = [
    (lambda X: f'<line x1="{X}" y1="96" x2="{X+30}" y2="96" stroke="#333" stroke-width="1.3" marker-end="url(#arr)"/>', "replaces", 38),
    (lambda X: f'<line x1="{X}" y1="96" x2="{X+30}" y2="96" stroke="#999" stroke-width="1.2" stroke-dasharray="3 2" marker-end="url(#arr2)"/>', "inspired by", 38),
    (lambda X: f'<line x1="{X}" y1="96" x2="{X+30}" y2="96" stroke="#e15759" stroke-width="5" opacity="0.35"/><text x="{X+30}" y="100" text-anchor="middle" font-weight="bold" fill="#555">x</text>', "lifetime until it ended", 42),
    (lambda X: f'<circle cx="{X+5}" cy="96" r="4.5" fill="white" stroke="#4e79a7" stroke-width="1.4"/>', "legacy or dead", 15),
    (lambda X: f'<line x1="{X+5}" y1="86" x2="{X+5}" y2="106" stroke="#aaa" stroke-dasharray="2 2"/>', "same way, several binding times", 15),
    (lambda X: "", "italic label: effect not deterministic", 0),
    (lambda X: f'<text x="{X}" y="100" fill="#888">(compile)</text>', "build or load sub-phase", 56),
]
for draw, text, w in legend2:
    italic = ' font-style="italic"' if not w else ""
    out.append(draw(lx) + f'<text x="{lx + w}" y="100"{italic}>{text}</text>')
    lx += w + len(text) * 6.2 + 28

# lane backgrounds and labels
for i, lane in enumerate(LANES):
    nxt = lane_top[LANES[i + 1]] if i + 1 < len(LANES) else lanes_bottom
    if i % 2 == 0:
        out.append(f'<rect x="0" y="{lane_top[lane]}" width="{width}" height="{nxt - lane_top[lane]}" fill="#f4f5f8"/>')
    out.append(f'<text x="12" y="{lane_top[lane] + 20}" font-weight="bold">{lane}</text>')

for year in range(1960, Y1, 10):
    out.append(f'<line x1="{x(year)}" y1="{TOP}" x2="{x(year)}" y2="{lanes_bottom}" stroke="#d0d4dc"/>'
               f'<text x="{x(year)}" y="{lanes_bottom + 16}" text-anchor="middle">{year}</text>')

# context events
ev_ends = []
for e in events:
    ex = x(int(e["year"]))
    text_w = len(f'{e["event"]} ({e["year"]})') * 5.6
    for k, end in enumerate(ev_ends):
        if ex - text_w / 2 > end + 8:
            ev_ends[k] = ex + text_w / 2
            break
    else:
        k = len(ev_ends)
        ev_ends.append(ex + text_w / 2)
    ty = TOP - 12 - k * 14
    out.append(f'<line x1="{ex}" y1="{ty + 4}" x2="{ex}" y2="{lanes_bottom}" stroke="#c44" stroke-width="1" '
               f'stroke-dasharray="1 4" opacity="0.7"/>'
               f'<text x="{ex}" y="{ty}" text-anchor="middle" fill="#b33" font-size="10.5">'
               f'{escape(e["event"])} ({e["year"]})</text>')

# connectors between binding times of the same way
for r in dated:
    ys = [cy(l, it) for l in LANES for it in items[l] if it["r"] is r]
    if len(ys) > 1:
        out.append(f'<line x1="{x(int(r["year"]))}" y1="{min(ys)}" x2="{x(int(r["year"]))}" y2="{max(ys)}" '
                   f'stroke="#aaa" stroke-width="1" stroke-dasharray="2 2"/>')

# lifelines
for r in dated:
    if r["ended"] and r["way"] in pos:
        x1, y1 = pos[r["way"]]
        x2 = x(int(r["ended"]))
        color = DOMAINS[r["mechanism"]]
        out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y1}" stroke="{color}" stroke-width="5" opacity="0.35"/>'
                   f'<text x="{x2}" y="{y1 + 4}" text-anchor="middle" font-weight="bold" fill="#555">x</text>')

# lineage arrows
for r in dated:
    for field, dashed in (("replaces", False), ("inspired_by", True)):
        for src in filter(None, r[field].split(";")):
            if src not in pos or r["way"] not in pos:
                continue
            (x1, y1), (x2, y2) = pos[src], pos[r["way"]]
            dx = max(abs(x2 - x1) / 2, 40)
            style = ('stroke="#999" stroke-width="1.1" stroke-dasharray="3 2" marker-end="url(#arr2)"' if dashed
                     else 'stroke="#333" stroke-width="1.3" marker-end="url(#arr)"')
            out.append(f'<path d="M{x1},{y1} C{x1 + dx},{y1} {x2 - dx},{y2} {x2 - 6},{y2}" fill="none" {style} opacity="0.8"/>')

# marks and labels
for lane in LANES:
    for it in items[lane]:
        r = it["r"]
        px, py = x(it["year"]), cy(lane, it)
        color = DOMAINS[r["mechanism"]]
        gone = r["status"] in ("legacy", "dead")
        size = 4.5 if it["primary"] else 3
        out.append(marker(r["origin_type"], px, py, size, "white" if gone else color, color if gone else "#333", tooltip(r)))
        if it["label"]:
            italic = ' font-style="italic"' if r["determinism"] != "deterministic" else ""
            extra = f'<tspan fill="#888">{escape(it["detail"])}</tspan>' if it["detail"] else ""
            out.append(f'<text x="{px + 9}" y="{py + 4}" fill="#222"{italic}>{escape(it["label"])}{extra}</text>')

undated = [r["way"] for r in rows if not r["year"]]
note, lines = "No clear first year, not drawn: " + ", ".join(undated), [""]
for word in note.split(" "):
    if len(lines[-1]) + len(word) > (width - LEFT - 40) / 5.8:
        lines.append("")
    lines[-1] += word + " "
for k, line in enumerate(lines):
    out.append(f'<text x="{LEFT}" y="{lanes_bottom + 36 + k * 15}" fill="#666">{escape(line.strip())}</text>')

# decade trends
out.append(f'<text x="{LEFT}" y="{panel_top}" font-size="15" font-weight="bold">How ways changed, by decade of appearance</text>'
           f'<text x="{LEFT}" y="{panel_top + 18}" fill="#555">Share of ways that appeared in each decade. '
           'Bar label is the number of ways.</text>')
dec_rows = {d: [r for r in dated if d <= int(r["year"]) < d + 10] for d in DECADES}
for p, (field, title, cats, colors) in enumerate(PANELS):
    px0 = LEFT + p * (PW + PGAP)
    py0 = panel_top + 44
    out.append(f'<text x="{px0}" y="{py0}" font-weight="bold">{title}</text>')
    for j, d in enumerate(DECADES):
        group = dec_rows[d]
        by = py0 + 10 + j * (BAR + 4)
        out.append(f'<text x="{px0 - 6}" y="{by + 12}" text-anchor="end" fill="#555">{d}s</text>')
        counts = Counter(r[field] for r in group)
        bx = px0
        for cat, col in zip(cats, colors):
            if not group or not counts[cat]:
                continue
            w = PW * counts[cat] / len(group)
            out.append(f'<rect x="{bx:.1f}" y="{by}" width="{w:.1f}" height="{BAR}" fill="{col}">'
                       f'<title>{d}s, {escape(cat)}: {counts[cat]} of {len(group)}</title></rect>')
            bx += w
        out.append(f'<text x="{px0 + PW + 4}" y="{by + 12}" fill="#777" font-size="10">{len(group)}</text>')
    ly = py0 + 10 + len(DECADES) * (BAR + 4) + 14
    lx, row = px0, 0
    for cat, col in zip(cats, colors):
        w = 22 + len(cat) * 6.0
        if lx + w > px0 + PW + 20:
            lx, row = px0, row + 1
        out.append(f'<rect x="{lx:.1f}" y="{ly + row * 18 - 10}" width="11" height="11" fill="{col}"/>'
                   f'<text x="{lx + 15:.1f}" y="{ly + row * 18}">{escape(cat)}</text>')
        lx += w

out.append("</svg>")
dest = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent / "static" / "history.svg"
dest.write_text("\n".join(out))
print(f"wrote {dest}")
