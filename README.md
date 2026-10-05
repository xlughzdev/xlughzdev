#!/usr/bin/env python3
"""Generates the Lughx GitHub profile SVGs: hero + arena, dark + light.
Pure SVG + SMIL. No JavaScript, no external assets.  Usage: python3 build_svgs.py
"""
import random
from pathlib import Path
from xml.etree import ElementTree as ET

OUT = Path(__file__).resolve().parent
FONT = "ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace"

TH = {
    "dark": dict(
        bg=("#0D1117", "#07111F"), frame="#30363D", acc=("#7C3AED", "#22D3EE", "#10B981"),
        wm=("#8B5CF6", "#22D3EE", "#34D399"), tx="#F8FAFC", mu="#94A3B8", lab="#22D3EE",
        glass=("#0B1220", 0.55), bo=(0.4, 0.8), grid=("#FFFFFF", 0.035), lights=(0.22, 0.14),
        cells=["#161B22", "#0E4429", "#006D32", "#26A641", "#39D353"], flash="#B6FFC8",
        ring="#39D353", ship=("#60A5FA", "#2563EB"), flame="#F97316", bul="#FACC15",
        star="#E6EDF3", so=1.0, glow=True, shadow=False),
    "light": dict(
        bg=("#FFFFFF", "#EEF6FF"), frame="#D0D7DE", acc=("#2563EB", "#06B6D4", "#10B981"),
        wm=("#1D4ED8", "#0E7490", "#047857"), tx="#0F172A", mu="#475569", lab="#0E7490",
        glass=("#FFFFFF", 0.72), bo=(0.45, 0.85), grid=("#0F172A", 0.04), lights=(0.10, 0.10),
        cells=["#EBEDF0", "#9BE9A8", "#40C463", "#30A14E", "#216E39"], flash="#9BE9A8",
        ring="#216E39", ship=("#3B82F6", "#1D4ED8"), flame="#F97316", bul="#D97706",
        star="#64748B", so=0.55, glow=False, shadow=True),
}

# 5x7 pixel glyphs, '#' = lit cell
GLY = {
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "U": ["#...#"] * 6 + [".###."],
    "G": [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
}


def word_cells():
    """Grid cells (col, row) of LUGHX on a 35x7 grid: letters start at cols 3, 9, 15, 21, 27."""
    return {(6 * i + 3 + c, r) for i, ch in enumerate("LUGHX")
            for r, row in enumerate(GLY[ch]) for c, v in enumerate(row) if v == "#"}


def fmt(t, T):
    return (f"{t / T:.5f}".rstrip("0").rstrip(".")) or "0"


def anim(attr, kf, T, rep=True, tag="animate", extra=""):
    """kf = [(seconds, value), ...] on a timeline of T seconds. Base attributes hold the FINAL state."""
    kf = sorted(((min(max(float(t), 0.0), T), str(v)) for t, v in kf), key=lambda k: k[0])
    if kf[0][0] > 0:
        kf.insert(0, (0.0, kf[0][1]))
    if kf[-1][0] < T:
        kf.append((T, kf[-1][1]))
    vals = ";".join(v for _, v in kf)
    kts = ";".join(fmt(t, T) for t, _ in kf)
    end = 'repeatCount="indefinite"' if rep else 'fill="freeze"'
    return f'<{tag} attributeName="{attr}" {extra} values="{vals}" keyTimes="{kts}" dur="{T:g}s" {end}/>'


def head(W, H, label, desc):
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{label}">\n'
            f'<title>{label}</title>\n<desc>{desc}</desc>\n')


# ------------------------------------------------------------------ ARENA
def arena(name):
    t, T = TH[name], 20.0
    (b1, b2), L = t["bg"], t["cells"]
    a0, a1, a2 = t["acc"]
    mu, bul = t["mu"], t["bul"]
    X0, Y0, SY = 34, 64, 344
    cx = lambda c: X0 + 32 * c + 12
    cy = lambda r: Y0 + 32 * r + 12
    nose = SY - 23
    rng = random.Random(42)
    word = word_cells()
    assert len(word) == 73

    free = [(c, r) for c in range(35) for r in range(7) if (c, r) not in word]
    decoys = sorted(rng.sample(free, 14))
    shots = [(1.35 + i * 0.19, c, r, "d") for i, (c, r) in enumerate(decoys)]
    tt = 4.2
    for c in range(3, 32):
        rows = sorted((r for (cc, r) in word if cc == c), reverse=True)
        for r in rows:
            shots.append((tt, c, r, "w"))
            tt += 0.045
        if rows:
            tt += 0.07
    travel = lambda r: 0.05 + (nose - cy(r)) / 1800

    sc = lambda kf: anim("transform", kf, T, tag="animateTransform", extra='type="scale"')
    tr = lambda kf: anim("transform", kf, T, tag="animateTransform", extra='type="translate"')
    op = lambda kf: anim("opacity", kf, T)

    glyph, rings, decoy_s, bullets, shards = [], [], [], [], []
    for ts, c, r, k in shots:
        x, y = cx(c), cy(r)
        hit = ts + travel(r)
        bullets.append(
            f'<g transform="translate({x} 0)"><g opacity="0">'
            + tr([(ts, f"0 {nose}"), (hit, f"0 {y + 4}")])
            + op([(0, 0), (ts, 0), (ts + 0.004, 1), (hit - 0.01, 1), (hit, 0)])
            + f'<rect x="-1.5" y="-9" width="3" height="10" rx="1.5" fill="{bul}"/>'
              f'<rect x="-1.5" y="3" width="3" height="3" rx="1.5" fill="{bul}"/></g></g>')
        if k == "w":
            fin = L[4] if rng.random() < 0.6 else L[3]
            o = [(0, 0), (hit, 0), (hit + 0.05, 1)]
            for j in range(3):  # soft brightness wave during HOLD
                tw = 10.2 + 2.7 * j + (c - 3) * 0.06
                o += [(tw - 0.3, 1), (tw, 0.82), (tw + 0.3, 1)]
            o += [(18.0, 1), (19.4, 0)]
            glyph.append(
                f'<g transform="translate({x} {y})"><g>'
                + sc([(0, 0.3), (hit, 0.3), (hit + 0.15, 1.25), (hit + 0.35, 1)]) + op(o)
                + f'<rect x="-12" y="-12" width="24" height="24" rx="5" fill="{fin}">'
                + anim("fill", [(0, L[0]), (hit, L[0]), (hit + 0.08, t["flash"]), (hit + 0.4, fin),
                                (19.5, fin), (19.7, L[0])], T)
                + '</rect></g></g>')
            rings.append(
                f'<g transform="translate({x} {y})"><rect x="-12" y="-12" width="24" height="24" rx="5" '
                f'fill="none" stroke="{t["ring"]}" stroke-width="2" opacity="0">'
                + sc([(hit, 1), (hit + 0.5, 2.1)]) + op([(hit, 0), (hit + 0.02, 0.85), (hit + 0.5, 0)])
                + '</rect></g>')
        else:
            col, fi = L[rng.randint(1, 4)], 0.4 + rng.random() * 0.5
            decoy_s.append(
                f'<g transform="translate({x} {y})"><g opacity="0">'
                + sc([(0, 0.3), (fi, 0.3), (fi + 0.5, 1), (hit, 1), (hit + 0.07, 1.4)])
                + op([(0, 0), (fi, 0), (fi + 0.5, 1), (hit, 1), (hit + 0.12, 0)])
                + f'<rect x="-12" y="-12" width="24" height="24" rx="5" fill="{col}"/></g></g>')
            for _ in range(4):
                ang, d = rng.uniform(0, 6.283), rng.uniform(14, 28)
                dx, dy = d * (1 if rng.random() > .5 else -1) * abs(__import__("math").cos(ang)), d * __import__("math").sin(ang)
                shards.append(
                    f'<g transform="translate({x} {y})"><rect x="-2" y="-2" width="4" height="4" rx="1" '
                    f'fill="{bul}" opacity="0">' + tr([(hit, "0 0"), (hit + 0.5, f"{dx:.1f} {dy:.1f}")])
                    + op([(hit, 0), (hit + 0.02, 1), (hit + 0.5, 0)]) + '</rect></g>')

    # ship path: rise, shoot decoys, build the word, idle at centre, leave, loop
    wp = [(0, "590 480"), (1.2, f"590 {SY}")]
    runs = []
    for ts, c, r, k in shots:
        x = cx(c)
        if runs and runs[-1][0] == x:
            runs[-1][2] = ts
        else:
            runs.append([x, ts, ts])
    for x, a, b in runs:
        wp += [(a - 0.03, f"{x} {SY}"), (b + 0.02, f"{x} {SY}")]
    wp += [(10.4, f"590 {SY}"), (18.0, f"590 {SY}"), (19.2, "590 480")]
    ship = (f'<g transform="translate(590 {SY})">' + tr(wp) + '<g>'
            '<animateTransform attributeName="transform" type="translate" values="0 0;0 -1.5;0 0" dur="2.4s" repeatCount="indefinite"/>'
            f'<g transform="translate(0 15)"><path d="M-4 0L0 17L4 0Z" fill="{t["flame"]}">'
            '<animateTransform attributeName="transform" type="scale" values="1 1;1 1.35;1 .8;1 1" dur=".26s" repeatCount="indefinite"/></path>'
            '<path d="M-2 0L0 9L2 0Z" fill="#FDE68A"/></g>'
            '<path d="M0 -23L7 -7L16 9L16 15L7 11L0 16L-7 11L-16 15L-16 9L-7 -7Z" fill="url(#ship)"/>'
            '<path d="M0 -23L7 -7L0 -3L-7 -7Z" fill="#FFFFFF" opacity=".25"/>'
            '<ellipse cx="0" cy="-3" rx="3" ry="6" fill="#E0F2FE" opacity=".95"/></g></g>')

    stars = []
    for i in range(52):
        x, y, r = rng.uniform(14, 1166), rng.uniform(10, 410), rng.choice([0.8, 1, 1.2, 1.6])
        lo, hi, d = rng.uniform(.15, .35) * t["so"], rng.uniform(.5, .95) * t["so"], rng.uniform(2.5, 6)
        drift = ('<animateTransform attributeName="transform" type="translate" values="0 0;-40 0;0 0" dur="24s" repeatCount="indefinite"/>' if i < 5 else "")
        stars.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{t["star"]}" opacity="{hi:.2f}">'
                     f'<animate attributeName="opacity" values="{lo:.2f};{hi:.2f};{lo:.2f}" dur="{d:.1f}s" '
                     f'begin="-{rng.uniform(0, d):.1f}s" repeatCount="indefinite"/>{drift}</circle>')

    cells = "".join(f'<rect x="{X0 + 32 * c}" y="{Y0 + 32 * r}" width="24" height="24" rx="5"/>'
                    for c in range(35) for r in range(7))
    gl_open = '<g filter="url(#glow)">' if t["glow"] else "<g>"
    label = "Animated contribution grid: a pixel spaceship clears stray squares, then spells LUGHX in green squares"
    return (head(1180, 420, label, "Decorative animation for the GitHub profile of Lughx (xlughzdev). Pure SVG and SMIL.")
            + f'<style>text{{font-family:{FONT}}}.h{{font-size:11px;font-weight:600;letter-spacing:3px;fill:{mu}}}'
              f'.m{{font-size:11px;letter-spacing:1px;fill:{mu}}}</style>\n<defs>'
              f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{b1}"/><stop offset="1" stop-color="{b2}"/></linearGradient>'
              f'<radialGradient id="lg" cx=".2" cy="0" r=".8"><stop offset="0" stop-color="{a0}" stop-opacity="{t["lights"][0]}"/><stop offset="1" stop-color="{a0}" stop-opacity="0"/></radialGradient>'
              f'<linearGradient id="ship" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t["ship"][0]}"/><stop offset="1" stop-color="{t["ship"][1]}"/></linearGradient>'
              '<filter id="glow" x="-5%" y="-10%" width="110%" height="120%"><feGaussianBlur stdDeviation="2.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>\n'
            + f'<rect x=".5" y=".5" width="1179" height="419" rx="20" fill="url(#bg)" stroke="{t["frame"]}"/>'
            + '<rect x=".5" y=".5" width="1179" height="419" rx="20" fill="url(#lg)"/>\n'
            + "".join(stars)
            + f'\n<text class="h" x="34" y="36">LUGHX.EXE</text><text class="h" x="972" y="36" text-anchor="end">BUILD</text>'
              f'<rect x="986" y="30" width="160" height="6" rx="3" fill="{L[0]}"/>'
              f'<rect x="986" y="30" width="160" height="6" rx="3" fill="{a2}">'
            + anim("width", [(0, 0), (4.2, 0), (9.5, 160), (18.4, 160), (19.4, 0)], T) + '</rect>\n'
            + f'<g fill="{L[0]}">{cells}</g>\n' + gl_open + "".join(glyph) + '</g>\n'
            + "".join(rings) + "".join(decoy_s) + "".join(bullets) + "".join(shards) + "\n" + ship
            + f'\n<text class="m" x="590" y="404" text-anchor="middle">xlughzdev · Lughx</text>\n</svg>\n')


# ------------------------------------------------------------------ HERO
def hero(name):
    t, T = TH[name], 3.6
    (b1, b2), fr = t["bg"], t["frame"]
    a0, a1, a2 = t["acc"]
    w0, w1, w2 = t["wm"]
    tx, mu, lab = t["tx"], t["mu"], t["lab"]
    gc, gop = t["glass"]
    bo0, bo1 = t["bo"]
    L, rng = t["cells"], random.Random(7)

    def rev(t0, dy=8, d=0.5):
        return (anim("opacity", [(t0, 0), (t0 + d, 1)], T, rep=False)
                + anim("transform", [(t0, f"0 {dy}"), (t0 + d, "0 0")], T, rep=False,
                       tag="animateTransform", extra='type="translate"'))

    def card(x, y, w, h):
        flt = ' filter="url(#sh)"' if t["shadow"] else ""
        return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{gc}" fill-opacity="{gop}"{flt} '
                f'stroke="url(#acc)" stroke-opacity="{bo0}">'
                + anim("stroke-opacity", [(0, bo0), (3, bo1), (6, bo0)], 6.0) + '</rect>')

    # ---- ASCII "ANSI Shadow" LUGHX wordmark (text only, no bitmap): solid blocks bright, shadow strokes dim
    ART = [
        "██╗     ██╗   ██╗ ██████╗ ██╗  ██╗██╗  ██╗",
        "██║     ██║   ██║██╔════╝ ██║  ██║╚██╗██╔╝",
        "██║     ██║   ██║██║  ███╗███████║ ╚███╔╝ ",
        "██║     ██║   ██║██║   ██║██╔══██║ ██╔██╗ ",
        "███████╗╚██████╔╝╚██████╔╝██║  ██║██╔╝ ██╗",
        "╚══════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝",
    ]
    assert all(len(r) == 42 for r in ART)
    ln = lambda y, txt, ex: (f'<text x="62" y="{y}" font-size="15" textLength="380" lengthAdjust="spacing" '
                             f'xml:space="preserve" style="white-space:pre" {ex}>{txt}</text>')
    art_rows = []
    for r, row_txt in enumerate(ART):
        y = 250 + 18 * r
        solid = "".join(ch if ch == "█" else " " for ch in row_txt)
        shade = "".join(" " if ch in "█ " else ch for ch in row_txt)
        art_rows.append("<g>" + rev(0.6 + r * 0.12, 6, 0.35)
                        + ln(y, shade, f'fill="{w1}" fill-opacity=".55"')
                        + ln(y, solid, 'font-weight="700" fill="url(#wm)"') + "</g>")
    rules = ('<rect x="62" y="216" width="380" height="1" fill="url(#fade)"/>'
             '<rect x="62" y="366" width="380" height="1" fill="url(#fade)"/>'
             '<text class="h" x="62" y="208">LUGHX.ASCII</text>'
             '<text class="h" x="442" y="208" text-anchor="end">UTF-8</text>')

    rings = "".join(
        f'<circle cx="252" cy="290" r="{rad}" fill="none" stroke="{a1}" stroke-opacity=".14">'
        + anim("stroke-opacity", [(0, .07), (2.5, .22), (5, .07)], 5.0, extra=f'begin="-{i * 1.6:.1f}s"') + '</circle>'
        for i, rad in enumerate((70, 115, 160)))

    # ---- right panel
    def row(y, k, v, t0):
        return f'<g>{rev(t0)}<text class="l" x="700" y="{y}" text-anchor="end">{k}</text><text class="v" x="724" y="{y}">{v}</text></g>'

    def sect(y, txt, t0):
        x2 = 524 + len(txt) * 9 + 14
        return (f'<g>{rev(t0)}<text class="h" x="524" y="{y}">{txt}</text>'
                f'<rect x="{x2}" y="{y - 4}" width="{1120 - x2}" height="1" fill="{fr}"/></g>')

    pills = ""
    for i, p in enumerate(("JavaScript", "Dockerfile")):
        x = 524 + i * 156
        fl = anim("transform", [(0, "0 0"), (2, "0 -2"), (4, "0 0")], 4.0, tag="animateTransform",
                  extra=f'type="translate" begin="{3.2 + i * 0.5}s"')
        pills += (f'<g>{rev(2.5 + i * 0.15)}<g>{fl}<rect x="{x}" y="392" width="140" height="28" rx="14" fill="{a1}" '
                  f'fill-opacity=".10" stroke="{a1}" stroke-opacity=".55"/><circle cx="{x + 18}" cy="406" r="4" fill="{a2}"/>'
                  f'<text class="v" x="{x + 32}" y="411">{p}</text></g></g>')

    cur_x = [(0, 528)] + [(0.9 + i * 0.18, round(528 + 38.4 * (i + 1), 1)) for i in range(5)]
    clip_w = [(0, 0)] + [(0.9 + i * 0.18, round(38.4 * (i + 1), 1)) for i in range(4)] + [(1.62, 400)]

    # ---- footer strip (contribution-graph motif)
    strip = ""
    for i in range(35):
        base = L[rng.choice([0, 0, 1, 2, 3])]
        strip += (f'<rect x="{32 + i * 18}" y="574" width="12" height="12" rx="3" fill="{base}">'
                  + anim("fill", [(0, base), (0.35, L[4]), (0.9, base)], 5.0, extra=f'begin="{3.0 + i * 0.07:.2f}s"') + '</rect>')

    parts = ""
    for _ in range(16):
        d = rng.uniform(12, 22)
        parts += (f'<circle cx="{rng.uniform(20, 1160):.0f}" cy="{rng.uniform(70, 600):.0f}" r="{rng.choice([1, 1.2, 1.5])}" fill="{a1}" opacity=".35">'
                  + anim("transform", [(0, "0 0"), (d / 2, f"0 -{rng.randint(14, 34)}"), (d, "0 0")], d,
                         tag="animateTransform", extra='type="translate"') + '</circle>')

    mark = "".join(f'<rect x="{112 + 8 * a}" y="{18 + 8 * b}" width="6" height="6" rx="1.5" fill="{L[4]}"/>'
                   for a, b in [(0, 0), (0, 1), (0, 2), (0, 3), (1, 3), (2, 3)])

    label = "Lughx (Thai Nhat Minh), JavaScript and Dockerfile developer. Terminal-style profile card for GitHub user xlughzdev."
    return (head(1180, 610, label, "Terminal-style profile card: VISUAL.MAP ASCII wordmark LUGHX and SYSTEM.INFO with name, role, handle, stack and links.")
            + f'<style>text{{font-family:{FONT}}}.h{{font-size:10px;letter-spacing:3px;fill:{mu}}}'
              f'.l{{font-size:11px;letter-spacing:1.5px;fill:{lab}}}.v{{font-size:15px;fill:{tx}}}</style>\n<defs>'
              f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{b1}"/><stop offset="1" stop-color="{b2}"/></linearGradient>'
              f'<linearGradient id="acc" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{a0}"/><stop offset=".5" stop-color="{a1}"/><stop offset="1" stop-color="{a2}"/></linearGradient>'
              f'<linearGradient id="wm" gradientUnits="userSpaceOnUse" x1="62" y1="0" x2="442" y2="0" spreadMethod="reflect">'
              f'<stop offset="0" stop-color="{w0}"/><stop offset=".5" stop-color="{w1}"/><stop offset="1" stop-color="{w2}"/>'
              '<animateTransform attributeName="gradientTransform" type="translate" values="0 0;760 0" dur="24s" repeatCount="indefinite"/></linearGradient>'
              f'<linearGradient id="fade" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{a1}" stop-opacity="0"/><stop offset=".5" stop-color="{a1}" stop-opacity=".55"/><stop offset="1" stop-color="{a1}" stop-opacity="0"/></linearGradient>'
              f'<linearGradient id="scan" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{a1}" stop-opacity="0"/><stop offset=".5" stop-color="{a1}" stop-opacity=".22"/><stop offset="1" stop-color="{a1}" stop-opacity="0"/></linearGradient>'
              f'<radialGradient id="r1" cx=".15" cy=".1" r=".6"><stop offset="0" stop-color="{a0}" stop-opacity="{t["lights"][0]}"/><stop offset="1" stop-color="{a0}" stop-opacity="0"/></radialGradient>'
              f'<radialGradient id="r2" cx=".9" cy=".95" r=".6"><stop offset="0" stop-color="{a1}" stop-opacity="{t["lights"][1]}"/><stop offset="1" stop-color="{a1}" stop-opacity="0"/></radialGradient>'
              f'<pattern id="gp" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="{t["grid"][0]}" stroke-opacity="{t["grid"][1]}"/></pattern>'
              '<clipPath id="lc"><rect x="32" y="88" width="440" height="462" rx="16"/></clipPath>'
              '<clipPath id="nc"><rect x="524" y="150" width="400" height="90">'
            + anim("width", clip_w, T, rep=False, extra='calcMode="discrete"')
            + '</rect></clipPath>'
              '<filter id="sh" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dy="8" stdDeviation="14" flood-color="#0F172A" flood-opacity=".10"/></filter></defs>\n'
            + f'<rect x=".5" y=".5" width="1179" height="609" rx="24" fill="url(#bg)" stroke="{fr}"/>'
              '<rect x=".5" y=".5" width="1179" height="609" rx="24" fill="url(#gp)"/>'
              '<rect x=".5" y=".5" width="1179" height="609" rx="24" fill="url(#r1)"/>'
              '<rect x=".5" y=".5" width="1179" height="609" rx="24" fill="url(#r2)"/>\n'
            + parts
            # window chrome
            + '\n<circle cx="44" cy="28" r="6" fill="#FF5F57"/><circle cx="64" cy="28" r="6" fill="#FEBC2E"/><circle cx="84" cy="28" r="6" fill="#28C840"/>'
            + mark + f'<path d="M1 56H1179" stroke="{fr}"/>'
            + f'<text x="590" y="33" text-anchor="middle" font-size="12" fill="{mu}">xlughzdev@devos ~ $ ./profile.sh --live</text>'
            + f'<circle cx="1107" cy="28" r="4" fill="{a2}">'
            + anim("r", [(0, 4), (1, 5.5), (2, 4)], 2.0) + anim("opacity", [(0, 1), (1, .5), (2, 1)], 2.0)
            + f'</circle><text x="1148" y="32" text-anchor="end" font-size="11" letter-spacing="2" fill="{mu}">LIVE</text>\n'
            # left card
            + f'<g>{rev(0.2, 0, 0.4)}{card(32, 88, 440, 462)}<text class="h" x="60" y="118">VISUAL.MAP</text>'
              f'<g clip-path="url(#lc)">{rings}'
              '<rect x="32" y="88" width="440" height="36" fill="url(#scan)">'
            + anim("transform", [(0, "0 -36"), (7, "0 470")], 7.0, tag="animateTransform", extra='type="translate"')
            + '</rect></g>' + rules + "".join(art_rows)
            + f'<text class="h" x="252" y="470" text-anchor="middle">[ PROFILE / DEVELOPER ]</text>'
              f'<text class="v" x="252" y="498" text-anchor="middle" font-size="13" fill="{a1}">~/lughx $ ship it'
              '<tspan>_<animate attributeName="fill-opacity" values="1;0" dur="1.1s" calcMode="discrete" repeatCount="indefinite"/></tspan></text></g>\n'
            # right card
            + f'<g>{rev(0.3, 0, 0.4)}{card(496, 88, 652, 462)}<text class="h" x="524" y="118">SYSTEM.INFO</text></g>'
            + f'<text class="l" x="524" y="146" opacity="0">[ OK ] loading identity ...'
            + anim("opacity", [(0, 0), (0.15, 1), (0.7, 1), (0.9, 0)], T, rep=False) + '</text>'
            + f'<text class="l" x="524" y="146" opacity="1">xlughzdev@devos:~$ ./profile.sh --live'
            + anim("opacity", [(0.9, 0), (1.0, 1)], T, rep=False) + '</text>\n'
            + f'<g clip-path="url(#nc)"><text x="524" y="214" font-size="64" font-weight="700" fill="{tx}" textLength="192" lengthAdjust="spacing">Lughx</text></g>'
            + '<g>' + anim("opacity", [(0.88, 0), (0.9, 1)], T, rep=False)
            + f'<rect x="728" y="166" width="10" height="52" fill="{a1}">'
            + anim("x", cur_x, T, rep=False, extra='calcMode="discrete"')
            + '<animate attributeName="opacity" values="1;0" dur="1.1s" calcMode="discrete" repeatCount="indefinite"/></rect></g>'
            + '<rect x="524" y="232" width="192" height="2" rx="1" fill="url(#acc)">' + anim("width", [(1.7, 0), (2.2, 192)], T, rep=False) + '</rect>\n'
            + sect(262, "IDENTITY", 1.9) + row(292, "REAL NAME", "Thai Nhat Minh", 2.0)
            + row(318, "ROLE", "JavaScript / Dockerfile developer", 2.1) + row(344, "HANDLE", "@xlughzdev", 2.2)
            + sect(378, "STACK", 2.4) + pills
            + sect(454, "LINKS", 2.7) + row(484, "GITHUB", "github.com/xlughzdev", 2.8) + row(510, "FACEBOOK", "facebook.com/iamlughx", 2.9)
            + '\n' + strip + f'<text x="1148" y="584" text-anchor="end" font-size="11" fill="{mu}">xlughzdev</text>\n</svg>\n')


def check(p):
    txt = p.read_text(encoding="utf-8")
    root = ET.fromstring(txt.encode("utf-8"))  # valid XML
    assert "http" not in txt.replace("http://www.w3.org/2000/svg", ""), "external reference found"
    for bad in ("<script", "<image", "@keyframes", "animation:", "<foreignObject"):
        assert bad not in txt, (p.name, bad)
    n = 0
    for e in root.iter():
        kt = e.get("keyTimes")
        if kt:
            k = [float(v) for v in kt.split(";")]
            assert k[0] == 0 and k[-1] == 1 and k == sorted(k), (p.name, kt[:60])
            assert len(k) == len(e.get("values").split(";")), (p.name, e.get("values")[:60])
            n += 1
    return n


if __name__ == "__main__":
    for nm in ("dark", "light"):
        for kind, fn in (("hero", hero), ("arena", arena)):
            p = OUT / f"{kind}-{nm}.svg"
            p.write_text(fn(nm), encoding="utf-8")
            print(f"{p.name:18s} {p.stat().st_size // 1024:4d} KB  animations checked: {check(p)}")
