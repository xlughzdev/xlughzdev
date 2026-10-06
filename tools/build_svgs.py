#!/usr/bin/env python3
"""Generates the Lughx GitHub profile SVGs: hero + arena, dark + light.
Pure SVG + SMIL. No JavaScript, no external assets.  Usage: python3 build_svgs.py
"""
import math
import random
import sys
from html import escape
from pathlib import Path
from xml.etree import ElementTree as ET

OUT = Path(__file__).resolve().parent
if OUT.name == "tools":  # script lives in tools/, output goes to the repo root
    OUT = OUT.parent
ASSETS = OUT / "assets"
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

    label = "Lughx (Thai Nhat Minh), Software Developer. Terminal-style profile card for GitHub user xlughzdev."
    return (head(1180, 610, label, "Terminal-style profile card: VISUAL.MAP ASCII wordmark LUGHX and SYSTEM.INFO with name, real name, role, handle and links.")
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
            + sect(266, "IDENTITY", 1.9) + row(294, "REAL NAME", "Thai Nhat Minh", 2.0)
            + row(320, "ROLE", "Software Developer", 2.1) + row(346, "HANDLE", "@xlughzdev", 2.2)
            + sect(384, "LINKS", 2.4) + row(412, "GITHUB", "github.com/xlughzdev", 2.5)
            + row(438, "FACEBOOK", "facebook.com/iamlughx", 2.6) + row(464, "TIKTOK", "@lughx.08", 2.7)
            + row(490, "DISCORD", "yc5p", 2.8) + row(516, "SERVER", "discord.gg/lughxshop", 2.9)
            + '\n' + strip + f'<text x="1148" y="584" text-anchor="end" font-size="11" fill="{mu}">xlughzdev</text>\n</svg>\n')


# ------------------------------------------------------------------ README ASSETS (assets/*.svg + README.md)
# Edit STACK, run `python3 tools/build_svgs.py --extras`, and the ticker rebuilds itself. No SVG is edited by hand.
STACK = ["C#", "Java", "HTML5", "CSS3", "SQL", "PostgreSQL", "JavaScript", "Node.js", "C++", "Rust", "Dockerfile"]
LINES = ["Software Developer", "Thai Nhat Minh · aka Lughx", "github.com/xlughzdev"]
SECTIONS = [("about", "about", "cat about.md", "ABOUT"), ("stack", "stack", "ls ./stack", "STACK"),
            ("identity", "identity", "cat id.card", "IDENTITY"), ("connect", "connect", "cat contact.txt", "CONNECT")]
BUTTONS = [("github", "GITHUB", "@xlughzdev", "https://github.com/xlughzdev"),
           ("facebook", "FACEBOOK", "iamlughx", "https://www.facebook.com/iamlughx"),
           ("tiktok", "TIKTOK", "@lughx.08", "https://www.tiktok.com/@lughx.08"),
           ("discord-server", "DISCORD SERVER", "lughxshop", "https://discord.gg/lughxshop"),
           ("discord", "DISCORD", "yc5p", None)]


def _style(t):
    return (f'<style>text{{font-family:{FONT}}}.h{{font-size:11px;font-weight:600;letter-spacing:3px;fill:{t["mu"]}}}'
            f'.l{{font-size:13px;fill:{t["lab"]}}}.t{{fill:{t["tx"]}}}.m{{font-size:13px;fill:{t["mu"]}}}</style>')


def _defs(t, extra=""):
    a0, a1, a2 = t["acc"]
    return ('<defs>'
            f'<linearGradient id="acc" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{a0}"/><stop offset=".5" stop-color="{a1}"/><stop offset="1" stop-color="{a2}"/></linearGradient>'
            f'<linearGradient id="fade" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{a1}" stop-opacity=".8"/><stop offset="1" stop-color="{a1}" stop-opacity="0"/></linearGradient>'
            f'<linearGradient id="ship" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t["ship"][0]}"/><stop offset="1" stop-color="{t["ship"][1]}"/></linearGradient>'
            + extra + '</defs>')


def _svg(t, W, H, label, desc, defs, body):
    return head(W, H, label, desc) + _style(t) + "\n" + _defs(t, defs) + "\n" + body + "\n</svg>\n"


def _rev(t0, T, dy=8, d=0.5):
    return (anim("opacity", [(t0, 0), (t0 + d, 1)], T, rep=False)
            + anim("transform", [(t0, f"0 {dy}"), (t0 + d, "0 0")], T, rep=False, tag="animateTransform", extra='type="translate"'))


def _tr(kf, T):
    return anim("transform", kf, T, tag="animateTransform", extra='type="translate"')


def ship_parts(t):
    return (f'<g transform="translate(0 15)"><path d="M-4 0L0 17L4 0Z" fill="{t["flame"]}">'
            '<animateTransform attributeName="transform" type="scale" values="1 1;1 1.35;1 .8;1 1" dur=".26s" repeatCount="indefinite"/></path>'
            '<path d="M-2 0L0 9L2 0Z" fill="#FDE68A"/></g>'
            '<path d="M0 -23L7 -7L16 9L16 15L7 11L0 16L-7 11L-16 15L-16 9L-7 -7Z" fill="url(#ship)"/>'
            '<path d="M0 -23L7 -7L0 -3L-7 -7Z" fill="#FFFFFF" opacity=".25"/>'
            '<ellipse cx="0" cy="-3" rx="3" ry="6" fill="#E0F2FE" opacity=".95"/>')


# ---- 1. aurora wave header (replaces an external waving-header service)
def wave(name):
    t, W, H = TH[name], 1180, 150
    a0, a1, a2 = t["acc"]
    page = t["bg"][0]  # GitHub page colour for this theme
    rng = random.Random(3)

    def layer(base, amp, per, ph, op, dur, rtl):
        pts = " L".join(f"{x},{base + amp * math.sin(2 * math.pi * x / per + ph):.1f}" for x in range(-per, W + per + 1, 10))
        frm, to = (f"{-per} 0", "0 0") if rtl else ("0 0", f"{-per} 0")
        return (f'<path d="M{pts} L{W + per},{H} L{-per},{H} Z" fill="{page}" fill-opacity="{op}">'
                + _tr([(0, frm), (dur, to)], dur) + '</path>')

    parts = ""
    for _ in range(14):
        d = rng.uniform(6, 12)
        parts += (f'<circle cx="{rng.uniform(20, 1160):.0f}" cy="{rng.uniform(30, 110):.0f}" r="{rng.choice([1, 1.4, 1.8])}" fill="#FFFFFF" opacity="0">'
                  + _tr([(0, "0 0"), (d, "0 -26")], d)
                  + anim("opacity", [(0, 0), (d * .3, .7), (d, 0)], d, extra=f'begin="-{rng.uniform(0, d):.1f}s"') + '</circle>')
    defs = (f'<linearGradient id="aur" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{W}" y2="0" spreadMethod="reflect">'
            f'<stop offset="0" stop-color="{a0}"/><stop offset=".5" stop-color="{a1}"/><stop offset="1" stop-color="{a2}"/>'
            f'<animateTransform attributeName="gradientTransform" type="translate" values="0 0;{2 * W} 0" dur="36s" repeatCount="indefinite"/></linearGradient>'
            f'<linearGradient id="tf" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{page}" stop-opacity="1"/><stop offset=".55" stop-color="{page}" stop-opacity="0"/></linearGradient>')
    body = (f'<rect width="{W}" height="{H}" fill="url(#aur)" opacity="{0.6 if name == "dark" else 0.5}"/>'
            f'<rect width="{W}" height="{H}" fill="url(#tf)"/>' + parts
            + layer(88, 16, 590, 0.0, 0.35, 24, False) + layer(104, 13, 400, 1.6, 0.6, 18, True) + layer(121, 10, 300, 3.1, 1, 13, False))
    return _svg(t, W, H, "Decorative aurora wave header with slowly moving colour gradient and layered waves",
                "Animated header band for the GitHub profile of Lughx.", defs, body)


# ---- 2. typing banner
def typing(name):
    t, T, slot, cw, W = TH[name], 14.4, 4.8, 16.8, 1180
    a1 = t["acc"][1]
    defs = body = ""
    for i, s in enumerate(LINES):
        n, t0 = len(s), i * slot
        x = round((W - n * cw) / 2, 1)
        ts = [t0 + 0.15 + k * 1.4 / n for k in range(n)]
        clip = [(0, 0)] + [(ts[k], round(cw * (k + 1), 1)) for k in range(n)]
        cur = [(0, x + 3)] + [(ts[k], round(x + cw * (k + 1) + 3, 1)) for k in range(n)]
        defs += (f'<clipPath id="c{i}"><rect x="{x}" y="10" width="{n * cw + 40:.0f}" height="60">'
                 + anim("width", clip, T, extra='calcMode="discrete"') + '</rect></clipPath>')
        body += (f'<g opacity="{1 if i == 0 else 0}">'
                 + anim("opacity", [(0, 0), (t0, 0), (t0 + 0.01, 1), (t0 + 4.3, 1), (t0 + 4.7, 0)], T)
                 + f'<g clip-path="url(#c{i})"><text class="t" x="{x}" y="50" font-size="28" font-weight="700" '
                   f'textLength="{n * cw:.1f}" lengthAdjust="spacing">{escape(s)}</text></g>'
                 + f'<rect x="{x + 3}" y="24" width="10" height="34" fill="{a1}" opacity="0">'
                 + anim("x", cur, T, extra='calcMode="discrete"')
                 + '<animate attributeName="opacity" values="1;0" dur="0.9s" calcMode="discrete" repeatCount="indefinite"/></rect></g>')
    body += ('<defs><linearGradient id="mid" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="' + a1 + '" stop-opacity="0"/>'
             '<stop offset=".5" stop-color="' + a1 + '" stop-opacity=".7"/><stop offset="1" stop-color="' + a1 + '" stop-opacity="0"/></linearGradient></defs>'
             '<rect x="290" y="80" width="600" height="1" fill="url(#mid)"/>')
    return _svg(t, W, 96, "Typing animation cycling through three lines: Software Developer, Thai Nhat Minh aka Lughx, github.com/xlughzdev",
                "Decorative typing animation for the GitHub profile of Lughx.", defs, body)


# ---- 3. terminal section headers
def section(name, path, cmd, title):
    t, T = TH[name], 2.4
    L, rng = t["cells"], random.Random(len(title))
    s = f"~/lughx/{path} $ {cmd}"
    n, cw = len(s), 7.8
    clip = [(0, 0)] + [(0.2 + k * 1.0 / n, round(cw * (k + 1), 1)) for k in range(n)]
    defs = (f'<clipPath id="pc"><rect x="8" y="8" width="{n * cw + 20:.0f}" height="26">'
            + anim("width", clip, T, rep=False, extra='calcMode="discrete"') + '</rect></clipPath>')
    cells = ""
    for i in range(9):
        base = L[rng.choice([1, 2, 2, 3])]
        cells += (f'<rect x="{1016 + 18 * i}" y="38" width="12" height="12" rx="3" fill="{base}">'
                  + anim("fill", [(0, base), (0.3, L[4]), (0.9, base)], 3.0, extra=f'begin="{i * 0.12:.2f}s"') + '</rect>')
    body = (f'<g clip-path="url(#pc)"><text class="l" x="8" y="26" xml:space="preserve" textLength="{n * cw:.1f}" '
            f'lengthAdjust="spacing">{escape(s)}</text></g>'
            '<g>' + anim("opacity", [(1.0, 0), (1.5, 1)], T, rep=False)
            + f'<text class="t" x="8" y="68" font-size="34" font-weight="700" textLength="{len(title) * 22}" lengthAdjust="spacing">{escape(title)}</text></g>'
            + '<rect x="8" y="81" width="1164" height="1" fill="url(#fade)"/>'
            + '<rect x="8" y="80" width="120" height="3" rx="1.5" fill="url(#acc)" opacity="0">'
            + _tr([(0, "0 0"), (4, "1044 0")], 5.0) + anim("opacity", [(0, 0), (0.4, 0.9), (3.6, 0.9), (4, 0)], 5.0) + '</rect>' + cells)
    return _svg(t, 1180, 96, f"Section header: {title}", "Decorative section header for the GitHub profile of Lughx.", defs, body)


# ---- 4. stack ticker: two rows of chips scrolling in opposite directions
def ticker(name):
    t = TH[name]
    a1, a2 = t["acc"][1], t["acc"][2]
    gc, gop = t["glass"]
    cw = 9.6

    def chips(items, y):
        x, out = 0, ""
        for s in items:
            w = round(28 + len(s) * cw + 20)
            out += (f'<rect x="{x}" y="{y}" width="{w}" height="44" rx="22" fill="{gc}" fill-opacity="{gop}" stroke="{a1}" stroke-opacity=".45"/>'
                    f'<circle cx="{x + 20}" cy="{y + 22}" r="4" fill="{a2}"/>'
                    f'<text class="t" x="{x + 34}" y="{y + 28}" font-size="16" font-weight="600">{escape(s)}</text>')
            x += w + 16
        return out, x

    def row(items, y, dur, rtl):
        c, S = chips(items, y)
        copies = "".join(f'<g transform="translate({k * S} 0)">{c}</g>' for k in range(3))
        frm, to = (f"{-S} 0", "0 0") if rtl else ("0 0", f"{-S} 0")
        return f'<g>{_tr([(0, frm), (dur, to)], dur)}{copies}</g>'

    defs = ('<linearGradient id="eg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#000"/><stop offset=".08" stop-color="#FFF"/>'
            '<stop offset=".92" stop-color="#FFF"/><stop offset="1" stop-color="#000"/></linearGradient>'
            '<mask id="em" maskUnits="userSpaceOnUse" x="0" y="0" width="1180" height="124"><rect width="1180" height="124" fill="url(#eg)"/></mask>')
    body = '<g mask="url(#em)">' + row(STACK, 8, 34, False) + row(STACK[::-1], 68, 42, True) + '</g>'
    return _svg(t, 1180, 124, "Scrolling ticker of technologies: " + ", ".join(STACK), "Decorative stack ticker for the GitHub profile of Lughx.", defs, body)


# ---- 5. holographic developer ID card with scanning laser and barcode
def idcard(name):
    t, T = TH[name], 3.6
    a0, a1, a2 = t["acc"]
    L, gc, gop, (bo0, bo1), fr = t["cells"], *t["glass"], t["bo"], t["frame"]
    bits = "".join(format(ord(c), "08b") for c in "xlughzdev" * 2)
    x, bars = 0.0, ""
    for b in bits:
        w = 3.0 if b == "1" else 1.5
        bars += f"M{300 + x:.1f} 262h{w}v32h-{w}z"
        x += w + 2.0
    BW = round(x)
    cells = ""
    for r, rowS in enumerate(GLY["L"]):
        for c, v in enumerate(rowS):
            cx, cy = 83 + 28 * c, 99 + 28 * r
            if v == "#":
                lv = L[4 if (r + c) % 2 == 0 else 3]
                cells += (f'<rect x="{cx}" y="{cy}" width="22" height="22" rx="5" fill="{lv}">'
                          + anim("fill", [(0, lv), (0.4, t["flash"]), (1.0, lv)], 4.0, extra=f'begin="{(r * 5 + c) * 0.08:.2f}s"') + '</rect>')
            else:
                cells += f'<rect x="{cx}" y="{cy}" width="22" height="22" rx="5" fill="{L[0]}" fill-opacity=".6"/>'
    fields = [("NICKNAME", "Lughx", 300, 104), ("HANDLE", "@xlughzdev", 740, 104),
              ("REAL NAME", "Thai Nhat Minh", 300, 190), ("ROLE", "Software Developer", 740, 190)]
    fl = "".join(f'<g>{_rev(0.6 + i * 0.25, T)}<text class="h" x="{fx}" y="{fy}">{lb}</text>'
                 f'<text class="t" x="{fx}" y="{fy + 36}" font-size="30" font-weight="700">{escape(vl)}</text>'
                 f'<rect x="{fx}" y="{fy + 48}" width="380" height="1" fill="{fr}"/></g>' for i, (lb, vl, fx, fy) in enumerate(fields))
    defs = ('<clipPath id="cd"><rect x="8" y="8" width="1164" height="324" rx="20"/></clipPath>'
            '<clipPath id="mf"><rect x="40" y="84" width="220" height="220" rx="14"/></clipPath>'
            f'<linearGradient id="holo" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{a0}" stop-opacity="0"/><stop offset=".35" stop-color="{a0}"/>'
            f'<stop offset=".5" stop-color="{a1}"/><stop offset=".65" stop-color="{a2}"/><stop offset="1" stop-color="{a2}" stop-opacity="0"/></linearGradient>'
            f'<linearGradient id="trail" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{a1}" stop-opacity="0"/><stop offset="1" stop-color="{a1}" stop-opacity=".35"/></linearGradient>')
    brk = "".join(f'<path d="{d}" fill="none" stroke="{a1}" stroke-width="2" stroke-linecap="round">'
                  + anim("opacity", [(0, 1), (1.5, 0.35), (3, 1)], 3.0) + '</path>'
                  for d in ("M34 94V78H50", "M250 78H266V94", "M34 290V306H50", "M250 306H266V290"))
    body = (f'<rect x="8" y="8" width="1164" height="324" rx="20" fill="{gc}" fill-opacity="{gop}" stroke="url(#acc)" stroke-opacity="{bo0}">'
            + anim("stroke-opacity", [(0, bo0), (3, bo1), (6, bo0)], 6.0) + '</rect>'
            '<g clip-path="url(#cd)"><g transform="skewX(-20)"><rect x="-500" y="0" width="360" height="340" fill="url(#holo)" opacity=".16">'
            + _tr([(0, "0 0"), (7, "2000 0")], 9.0) + '</rect></g></g>'
            + '<text class="h" x="40" y="44">DEVELOPER ID</text>'
            + f'<circle cx="1074" cy="40" r="4" fill="{a2}">' + anim("opacity", [(0, 1), (1, 0.4), (2, 1)], 2.0) + '</circle>'
            + '<text class="h" x="1140" y="44" text-anchor="end">ONLINE</text>'
            + f'<rect x="40" y="60" width="1100" height="1" fill="{fr}"/>'
            + f'<rect x="40" y="84" width="220" height="220" rx="14" fill="{L[0]}" fill-opacity=".35" stroke="{a1}" stroke-opacity=".5"/>'
            + cells + brk
            + f'<g clip-path="url(#mf)"><rect x="40" y="84" width="220" height="26" fill="url(#trail)">' + _tr([(0, "0 -26"), (2.8, "0 196")], 3.2) + '</rect>'
            + f'<rect x="40" y="84" width="220" height="2" fill="{a1}">' + _tr([(0, "0 0"), (2.8, "0 218")], 3.2) + '</rect></g>'
            + fl
            + f'<g><rect x="1088" y="84" width="52" height="40" rx="8" fill="none" stroke="{a1}" stroke-width="1.5"/>'
              f'<path d="M1088 98H1140M1088 110H1140M1108 84V124M1120 84V124" stroke="{a1}" stroke-opacity=".6"/>'
            + anim("opacity", [(0, 1), (1.5, 0.5), (3, 1)], 3.0) + '</g>'
            + f'<path d="{bars}" fill="{t["tx"]}" fill-opacity=".85"/>'
            + f'<rect x="300" y="256" width="2" height="44" fill="{a1}">' + _tr([(0, "0 0"), (3, f"{BW} 0")], 3.6)
            + anim("opacity", [(0, 0), (0.2, 1), (2.8, 1), (3, 0)], 3.6) + '</rect>'
            + '<text class="h" x="300" y="318">XLUGHZDEV</text>')
    return _svg(t, 1180, 340, "Developer ID card: nickname Lughx, real name Thai Nhat Minh, role Software Developer, handle xlughzdev",
                "Holographic ID card with a scanning laser, built from SVG and SMIL.", defs, body)


# ---- 6. link buttons (the README wraps each one in a normal link)
def connect(name, label, value, W=380):
    t = TH[name]
    a1, a2 = t["acc"][1], t["acc"][2]
    gc, gop = t["glass"]
    bo0, bo1 = t["bo"]
    cw = W - 16
    defs = (f'<clipPath id="cc"><rect x="8" y="8" width="{cw}" height="80" rx="16"/></clipPath>'
            f'<linearGradient id="sw" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{a1}" stop-opacity="0"/><stop offset=".5" stop-color="{a1}" stop-opacity=".16"/><stop offset="1" stop-color="{a1}" stop-opacity="0"/></linearGradient>')
    body = (f'<rect x="8" y="8" width="{cw}" height="80" rx="16" fill="{gc}" fill-opacity="{gop}" stroke="url(#acc)" stroke-opacity="{bo0}">'
            + anim("stroke-opacity", [(0, bo0), (2, bo1), (4, bo0)], 4.0) + '</rect>'
            '<g clip-path="url(#cc)"><rect x="-120" y="8" width="120" height="80" fill="url(#sw)">' + _tr([(0, "0 0"), (3, f"{W + 140} 0")], 5.0) + '</rect></g>'
            + f'<circle cx="36" cy="34" r="4" fill="none" stroke="{a2}">' + anim("r", [(0, 4), (2.4, 13)], 2.4) + anim("opacity", [(0, 0.9), (2.4, 0)], 2.4) + '</circle>'
            + f'<circle cx="36" cy="34" r="4" fill="{a2}"/>'
            + f'<text class="h" x="48" y="38">{escape(label)}</text>'
            + f'<text class="t" x="36" y="70" font-size="22" font-weight="700">{escape(value)}</text>'
            + f'<text x="{W - 34}" y="62" font-size="28" text-anchor="end" fill="{a1}">→' + _tr([(0, "0 0"), (1, "6 0"), (2, "0 0")], 2.0) + '</text>')
    return _svg(t, W, 96, f"Link button: {label.title()} {value}", "Decorative link button; the surrounding README link is the clickable part.", defs, body)


# ---- 7. boot log (typed lines, OK tags, progress bar, spinner; 16s loop)
def bootlog(name):
    t, T = TH[name], 16.0
    a1, a2 = t["acc"][1], t["acc"][2]
    gc, gop = t["glass"]
    bo0, fr, L = t["bo"][0], t["frame"], t["cells"]
    items = ["profile loaded", "identity verified", "stack detected", "connection ready", "LUGHX.EXE running"]
    cw, defs, lines = 10.8, "", ""
    for i, s in enumerate(items):
        txt = "> " + s
        n, y, t0 = len(txt), 96 + 36 * i, 0.8 + i * 1.7
        ts = [t0 + k * 0.9 / n for k in range(n)]
        clip = [(0, 0)] + [(ts[k], round(cw * (k + 1), 1)) for k in range(n)]
        defs += (f'<clipPath id="b{i}"><rect x="40" y="{y - 22}" width="{n * cw + 20:.0f}" height="30">'
                 + anim("width", clip, T, extra='calcMode="discrete"') + '</rect></clipPath>')
        g = ('<g>' + anim("opacity", [(0, 0), (t0, 0), (t0 + 0.01, 1)], T)
             + f'<g clip-path="url(#b{i})"><text class="t" x="40" y="{y}" font-size="18" textLength="{n * cw:.1f}" lengthAdjust="spacing" xml:space="preserve">{escape(txt)}</text></g>')
        if i < 4:
            g += (f'<line x1="{40 + n * cw + 16:.0f}" y1="{y - 5}" x2="900" y2="{y - 5}" stroke="{fr}" stroke-width="2" stroke-dasharray="2 8" stroke-linecap="round">'
                  + anim("opacity", [(t0 + 0.9, 0), (t0 + 1.1, 1)], T) + '</line>'
                  f'<text x="920" y="{y}" font-size="18" font-weight="700" fill="{a2}">[ OK ]' + anim("opacity", [(t0 + 1.1, 0), (t0 + 1.12, 1)], T) + '</text>')
        else:
            g += (f'<g transform="translate({40 + n * cw + 26:.0f} {y - 6})"><circle r="7" fill="none" stroke="{a1}" stroke-width="2" stroke-dasharray="12 32" stroke-linecap="round">'
                  '<animateTransform attributeName="transform" type="rotate" values="0;360" dur=".9s" repeatCount="indefinite"/></circle></g>')
        lines += g + '</g>'
    lines += (f'<rect x="40" y="260" width="1100" height="6" rx="3" fill="{L[0]}"/>'
              '<rect x="40" y="260" width="1100" height="6" rx="3" fill="url(#acc)">' + anim("width", [(0, 0), (0.8, 0), (8.7, 1100)], T) + '</rect>')
    body = (f'<rect x="8" y="8" width="1164" height="284" rx="16" fill="{gc}" fill-opacity="{gop}" stroke="url(#acc)" stroke-opacity="{bo0}"/>'
            '<circle cx="40" cy="32" r="6" fill="#FF5F57"/><circle cx="60" cy="32" r="6" fill="#FEBC2E"/><circle cx="80" cy="32" r="6" fill="#28C840"/>'
            '<text class="m" x="590" y="37" text-anchor="middle">lughx.exe</text>'
            f'<circle cx="1068" cy="32" r="4" fill="{a2}">' + anim("opacity", [(0, 1), (1, 0.4), (2, 1)], 2.0) + '</circle>'
            '<text class="h" x="1148" y="36" text-anchor="end">RUNNING</text>'
            f'<rect x="8" y="56" width="1164" height="1" fill="{fr}"/>'
            '<g>' + anim("opacity", [(0, 1), (13.6, 1), (14.8, 0)], T) + lines + '</g>')
    return _svg(t, 1180, 300, "Boot log of lughx.exe: profile loaded, identity verified, stack detected, connection ready, LUGHX.EXE running",
                "Decorative boot sequence for the GitHub profile of Lughx.", defs, body)


# ---- 8. footer: ship lights up a row of cells
def footer(name):
    t, T = TH[name], 12.0
    L, rng = t["cells"], random.Random(11)
    cells = ""
    for c in range(35):
        ta, lv = 0.5 + c * 7.0 / 34, L[rng.choice([2, 3, 3, 4])]
        cells += (f'<rect x="{34 + 32 * c}" y="64" width="24" height="24" rx="5" fill="{L[0]}">'
                  + anim("fill", [(0, L[0]), (ta, L[0]), (ta + 0.1, t["flash"]), (ta + 0.5, lv), (ta + 3.0, lv), (ta + 4.0, L[0])], T) + '</rect>')
    ship = ('<g transform="translate(590 36)">' + _tr([(0, "46 36"), (0.5, "46 36"), (7.5, "1134 36")], T)
            + '<g>' + anim("opacity", [(0, 0), (0.4, 1), (7.2, 1), (7.6, 0)], T)
            + '<g transform="scale(.7)">' + ship_parts(t) + '</g></g></g>')
    body = cells + ship + '<text class="h" x="590" y="116" text-anchor="middle">THANKS FOR VISITING · LUGHX</text>'
    return _svg(t, 1180, 128, "Footer: a small spaceship flies over a row of contribution cells and lights them up",
                "Decorative footer for the GitHub profile of Lughx.", "", body)


def pic(path, alt, extra=""):
    d, l = path.replace("{}", "dark"), path.replace("{}", "light")
    return (f'<picture>\n  <source media="(prefers-color-scheme: dark)" srcset="{d}">\n'
            f'  <source media="(prefers-color-scheme: light)" srcset="{l}">\n  <img src="{d}" alt="{alt}"{extra}>\n</picture>')


def readme():
    def banner(key, title):
        return '<div align="center">\n\n' + pic(f"./assets/section-{key}-{{}}.svg", f"Section header: {title}") + "\n\n</div>\n"

    def btn(key, label, value, href):
        img = pic(f"./assets/btn-{key}-{{}}.svg", f"{label.title()}: {value}", ' width="32%"')
        return f'  <a href="{href}">\n{img}\n  </a>' if href else "  " + img

    row1 = "\n".join(btn(*b) for b in BUTTONS[:3])
    row2 = "\n".join(btn(*b) for b in BUTTONS[3:])
    badges = """![C#](https://img.shields.io/badge/C%23-239120?style=for-the-badge&logo=csharp&logoColor=white)
![Java](https://img.shields.io/badge/Java-ED8B00?style=for-the-badge&logo=java&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-4479A1?style=for-the-badge&logo=sqlite&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![Node.js](https://img.shields.io/badge/Node.js-339933?style=for-the-badge&logo=nodedotjs&logoColor=white)
![C++](https://img.shields.io/badge/C%2B%2B-00599C?style=for-the-badge&logo=cplusplus&logoColor=white)
![Rust](https://img.shields.io/badge/Rust-000000?style=for-the-badge&logo=rust&logoColor=white)
![Dockerfile](https://img.shields.io/badge/Dockerfile-2496ED?style=for-the-badge&logo=docker&logoColor=white)"""

    w100 = ' width="100%"'
    o = ['<div align="center">\n\n'
         + pic("./assets/wave-{}.svg", "Animated aurora wave header", w100) + "\n\n"
         + pic("./hero-{}.svg", "Lughx (Thai Nhat Minh), Software Developer, terminal-style profile card", w100) + "\n\n"
         + pic("./arena-{}.svg", "Animated contribution grid where a pixel spaceship clears stray cells and spells LUGHX", w100) + "\n\n"
         + pic("./assets/typing-{}.svg", "Typing animation: Software Developer, Thai Nhat Minh aka Lughx, github.com/xlughzdev")
         + "\n\n</div>\n",
         banner("about", "About"),
         """> A developer profile built around a simple idea:
> **keep it clean, technical, and focused.**

I'm **Lughx**, real name **Thai Nhat Minh**.

My GitHub account is **[@xlughzdev](https://github.com/xlughzdev)**. I build software using **C#**, **Java**, **HTML5**, **CSS3**, **SQL**, **PostgreSQL**, **JavaScript**, **Node.js**, **C++**, **Rust**, and **Dockerfile**.
""",
         banner("stack", "Stack"),
         '<div align="center">\n\n' + pic("./assets/ticker-{}.svg", "Scrolling ticker of my technologies") + "\n\n" + badges + "\n\n</div>\n",
         banner("identity", "Identity"),
         '<div align="center">\n\n' + pic("./assets/idcard-{}.svg", "Developer ID card: Lughx, Thai Nhat Minh, Software Developer, @xlughzdev") + "\n\n</div>\n",
         banner("connect", "Connect"),
         f'<p align="center">\n{row1}\n</p>\n\n<p align="center">\n{row2}\n</p>\n',
         '<div align="center">\n\n' + pic("./assets/bootlog-{}.svg", "Boot log of lughx.exe") + "\n\n"
         + pic("./assets/footer-{}.svg", "Footer: a small spaceship lights up a row of contribution cells") + "\n\n</div>\n"]
    return "\n".join(o)


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
    ASSETS.mkdir(exist_ok=True)
    extras = "--extras" in sys.argv   # also build assets/*.svg and the generated README.md
    jobs = []
    for nm in ("dark", "light"):
        jobs += [(OUT / f"hero-{nm}.svg", hero(nm)), (OUT / f"arena-{nm}.svg", arena(nm))]
        if extras:
            jobs += [(ASSETS / f"{k}-{nm}.svg", fn(nm)) for k, fn in
                     (("wave", wave), ("typing", typing), ("ticker", ticker), ("idcard", idcard), ("bootlog", bootlog), ("footer", footer))]
            jobs += [(ASSETS / f"btn-{k}-{nm}.svg", connect(nm, lab, val)) for k, lab, val, _ in BUTTONS]
            jobs += [(ASSETS / f"section-{k}-{nm}.svg", section(nm, pth, cmd, ttl)) for k, pth, cmd, ttl in SECTIONS]
    for path, txt in jobs:
        path.write_text(txt, encoding="utf-8")
        print(f"{str(path.relative_to(OUT)):34s} {path.stat().st_size // 1024:4d} KB  animations checked: {check(path)}")
    if extras:
        (OUT / "README.md").write_text(readme(), encoding="utf-8")
        print("README.md written")
