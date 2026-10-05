from __future__ import annotations

from pathlib import Path
import random
import xml.etree.ElementTree as ET

OUT = Path(__file__).resolve().parent
NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)

FONT = "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace"
GLYPHS = {
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "G": [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
}

THEMES = {
    "dark": {
        "bg1": "#0D1117", "bg2": "#07111F", "panel": "#0F172A", "panel2": "#111827",
        "border": "#25324A", "primary": "#F8FAFC", "muted": "#94A3B8", "faint": "#64748B",
        "violet": "#7C3AED", "cyan": "#22D3EE", "emerald": "#10B981", "grid": "#1B2738",
        "l0": "#161B22", "l1": "#0E4429", "l2": "#006D32", "l3": "#26A641", "l4": "#39D353",
        "ship1": "#60A5FA", "ship2": "#2563EB", "bullet": "#FACC15", "flame": "#F97316",
        "noise": "#FFFFFF", "star": "#A8C7FF", "shadow": "#000000",
        "ring": "#22D3EE",
    },
    "light": {
        "bg1": "#FFFFFF", "bg2": "#EEF6FF", "panel": "#FFFFFF", "panel2": "#F8FAFC",
        "border": "#D0D7DE", "primary": "#0F172A", "muted": "#475569", "faint": "#64748B",
        "violet": "#7C3AED", "cyan": "#06B6D4", "emerald": "#10B981", "grid": "#D8DEE4",
        "l0": "#EBEDF0", "l1": "#9BE9A8", "l2": "#40C463", "l3": "#30A14E", "l4": "#216E39",
        "ship1": "#60A5FA", "ship2": "#2563EB", "bullet": "#D97706", "flame": "#F97316",
        "noise": "#94A3B8", "star": "#6B8DB8", "shadow": "#64748B", "ring": "#06B6D4",
    },
}


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def add(parent, tag, attrib=None, text=None):
    node = ET.SubElement(parent, f"{{{NS}}}{tag}", attrib or {})
    if text is not None:
        node.text = text
    return node


def rect(parent, x, y, w, h, **attrs):
    a = {"x": str(x), "y": str(y), "width": str(w), "height": str(h)}
    a.update({k: str(v) for k, v in attrs.items()})
    return add(parent, "rect", a)


def line(parent, x1, y1, x2, y2, **attrs):
    a = {"x1": str(x1), "y1": str(y1), "x2": str(x2), "y2": str(y2)}
    a.update({k: str(v) for k, v in attrs.items()})
    return add(parent, "line", a)


def circle(parent, cx, cy, r, **attrs):
    a = {"cx": str(cx), "cy": str(cy), "r": str(r)}
    a.update({k: str(v) for k, v in attrs.items()})
    return add(parent, "circle", a)


def text_el(parent, x, y, content, **attrs):
    a = {"x": str(x), "y": str(y)}
    a.update({k: str(v) for k, v in attrs.items()})
    node = add(parent, "text", a)
    node.text = content
    return node


def animate(node, attribute, values, key_times, *, dur="20s", begin=None, additive=None):
    a = {"attributeName": attribute, "values": ";".join(map(str, values)), "keyTimes": ";".join(map(str, key_times)),
         "dur": dur, "repeatCount": "indefinite"}
    if begin is not None:
        a["begin"] = str(begin)
    if additive:
        a["additive"] = additive
    add(node, "animate", a)


def animate_transform(node, values, key_times, *, dur="20s", additive="sum", type_="translate"):
    a = {"attributeName": "transform", "type": type_, "values": ";".join(values),
         "keyTimes": ";".join(map(str, key_times)), "dur": dur, "repeatCount": "indefinite"}
    if additive:
        a["additive"] = additive
    add(node, "animateTransform", a)


def defs_common(root, t, prefix):
    defs = add(root, "defs")
    bg = add(defs, "linearGradient", {"id": f"{prefix}Bg", "x1": "0", "y1": "0", "x2": "1", "y2": "1"})
    add(bg, "stop", {"offset": "0%", "stop-color": t["bg1"]})
    add(bg, "stop", {"offset": "100%", "stop-color": t["bg2"]})
    panel = add(defs, "linearGradient", {"id": f"{prefix}Panel", "x1": "0", "y1": "0", "x2": "1", "y2": "1"})
    add(panel, "stop", {"offset": "0%", "stop-color": t["panel"], "stop-opacity": "0.92"})
    add(panel, "stop", {"offset": "100%", "stop-color": t["panel2"], "stop-opacity": "0.72"})
    accent = add(defs, "linearGradient", {"id": f"{prefix}Accent", "x1": "0", "y1": "0", "x2": "1", "y2": "0"})
    add(accent, "stop", {"offset": "0%", "stop-color": t["violet"]})
    add(accent, "stop", {"offset": "50%", "stop-color": t["cyan"]})
    add(accent, "stop", {"offset": "100%", "stop-color": t["emerald"]})
    ship = add(defs, "g", {"id": "ship"})
    add(ship, "path", {"d": "M0 22 L17 0 L34 22 L27 19 L24 33 L10 33 L7 19 Z", "fill": f"url(#{prefix}Ship)"})
    add(ship, "ellipse", {"cx": "17", "cy": "12", "rx": "5", "ry": "7", "fill": "#DBEAFE", "opacity": "0.88"})
    add(ship, "path", {"d": "M12 31 L17 46 L22 31 Z", "fill": t["flame"]})
    add(ship, "path", {"d": "M15 33 L17 41 L19 33 Z", "fill": "#FDE68A", "opacity": "0.95"})
    shipg = add(defs, "linearGradient", {"id": f"{prefix}Ship", "x1": "0", "y1": "0", "x2": "1", "y2": "1"})
    add(shipg, "stop", {"offset": "0%", "stop-color": t["ship1"]})
    add(shipg, "stop", {"offset": "100%", "stop-color": t["ship2"]})
    bullet = add(defs, "g", {"id": "bullet"})
    rect(bullet, -3, -1.5, 6, 3, rx=1.5, fill=t["bullet"])
    add(bullet, "circle", {"cx": "0", "cy": "0", "r": "3", "fill": t["bullet"], "opacity": "0.18"})
    filter_shadow = add(defs, "filter", {"id": f"{prefix}Shadow", "x": "-20%", "y": "-20%", "width": "140%", "height": "140%"})
    add(filter_shadow, "feDropShadow", {"dx": "0", "dy": "8", "stdDeviation": "12", "flood-color": t["shadow"], "flood-opacity": "0.18"})
    if prefix == "d":
        noise = add(defs, "filter", {"id": f"{prefix}Noise"})
        add(noise, "feTurbulence", {"type": "fractalNoise", "baseFrequency": "0.75", "numOctaves": "2", "stitchTiles": "stitch", "seed": "9"})
        add(noise, "feColorMatrix", {"values": "1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 .045 0"})
    return defs


def word_cells(matrix, x0, y0, cell, gap, fill="currentColor", start_col=0):
    nodes = []
    pitch = cell + gap
    cx = start_col
    for letter in "LUGHX":
        glyph = GLYPHS[letter]
        for ry, row in enumerate(glyph):
            for rx, ch in enumerate(row):
                if ch == "#":
                    x = x0 + (cx + rx) * pitch
                    y = y0 + ry * pitch
                    nodes.append((letter, rx, ry, x, y))
        cx += 5 + 1
    return nodes


def hero_svg(theme_name: str) -> str:
    t = THEMES[theme_name]
    p = "d" if theme_name == "dark" else "l"
    root = ET.Element(f"{{{NS}}}svg", {"width": "1180", "height": "610", "viewBox": "0 0 1180 610",
        "role": "img", "aria-label": f"Lughx terminal profile card for Thai Nhat Minh, a JavaScript and Dockerfile developer, {theme_name} theme"})
    add(root, "title", text=None).text = f"Lughx — developer profile ({theme_name} theme)"
    add(root, "desc", text=None).text = "Premium terminal-style profile card for Lughx, showing identity, stack, and public links."
    defs_common(root, t, p)
    if theme_name == "dark":
        glow = add(root.find(f"{{{NS}}}defs"), "filter", {"id": f"{p}Glow", "x":"-50%", "y":"-50%", "width":"200%", "height":"200%"})
        add(glow, "feGaussianBlur", {"stdDeviation":"3.2", "result":"blur"})
        merge = add(glow, "feMerge")
        add(merge, "feMergeNode", {"in":"blur"})
        add(merge, "feMergeNode", {"in":"SourceGraphic"})
    style = add(root, "style")
    style.text = f"text{{font-family:{FONT};}} .primary{{fill:{t['primary']};}} .muted{{fill:{t['muted']};}} .faint{{fill:{t['faint']};}} .mono{{font-family:{FONT};}}"

    # Background + animated technical grid.
    rect(root, 0, 0, 1180, 610, fill=f"url(#{p}Bg)")
    for gx in range(72, 1130, 48):
        gl = line(root, gx, 80, gx, 548, stroke=t["grid"], **{"stroke-width":"1", "stroke-opacity":"0.12"})
        animate(gl, "stroke-opacity", [0.08,0.15,0.08,0.08], [0,0.22,0.44,1], dur="20s")
    for gy in range(104, 552, 48):
        gl = line(root, 48, gy, 1132, gy, stroke=t["grid"], **{"stroke-width":"1", "stroke-opacity":"0.08"})
        animate(gl, "stroke-opacity", [0.06,0.12,0.06,0.06], [0,0.30,0.60,1], dur="20s")
    if theme_name == "dark":
        rect(root, 0, 0, 1180, 610, fill="#FFFFFF", opacity="0.10", filter=f"url(#{p}Noise)")

    frame = rect(root, 32, 32, 1116, 546, rx=24, fill="none", stroke=t["border"], **{"stroke-width": "1.2"})
    animate(frame, "stroke-opacity", [0.65,1,0.65,0.65], [0,0.28,0.56,1], dur="20s")
    topbar = rect(root, 32, 32, 1116, 48, rx=24, fill=t["panel"], opacity="0.58")
    rect(root, 32, 56, 1116, 24, fill=t["panel"], opacity="0.58")

    for cx, col in [(54, "#FF5F57"), (72, "#FEBC2E"), (90, "#28C840")]:
        c = circle(root, cx, 56, 5.5, fill=col)
        animate(c, "opacity", [0.82,1,0.82,0.82], [0,0.25,0.5,1], dur="20s")
    # tiny pixel L mark
    px0, py0, pc = 106, 48, 6
    for x, y in [(0,0),(0,1),(0,2),(1,2),(2,2)]:
        q = rect(root, px0+x*7, py0+y*7, pc, pc, rx=2, fill=t["emerald"])
        animate(q, "opacity", [0.65,1,0.65,0.65], [0,0.3,0.55,1], dur="20s")
    text_el(root, 392, 61, "xlughzdev@devos ~ $ ./profile.sh --live", fill=t["muted"], **{"font-size":"13", "letter-spacing":"0.15px", "text-anchor":"middle"})
    live_dot = circle(root, 1080, 56, 4, fill=t["emerald"])
    animate(live_dot, "r", [3.3,4.6,3.3,3.3], [0,0.25,0.5,1], dur="20s")
    animate(live_dot, "opacity", [0.38,1,0.38,0.38], [0,0.25,0.5,1], dur="20s")
    text_el(root, 1093, 61, "LIVE", fill=t["muted"], **{"font-size":"11", "letter-spacing":"1.3px", "text-anchor":"start"})

    # Main cards.
    left = rect(root, 48, 88, 440, 462, rx=18, fill=f"url(#{p}Panel)", stroke=t["border"], **{"stroke-width":"1", "filter":f"url(#{p}Shadow)" if theme_name == "light" else "none"})
    right = rect(root, 512, 88, 620, 462, rx=18, fill=f"url(#{p}Panel)", stroke=t["border"], **{"stroke-width":"1", "filter":f"url(#{p}Shadow)" if theme_name == "light" else "none"})
    animate(left, "stroke-opacity", [0.65,1,0.65,0.65], [0,0.32,0.64,1], dur="20s")
    animate(right, "stroke-opacity", [0.65,1,0.65,0.65], [0.1,0.42,0.74,1], dur="20s")

    text_el(root, 72, 118, "VISUAL.MAP", fill=t["muted"], **{"font-size":"11", "letter-spacing":"2.2px"})
    text_el(root, 536, 118, "SYSTEM.INFO", fill=t["muted"], **{"font-size":"11", "letter-spacing":"2.2px"})

    # Signal rings rotate and breathe.
    center_x, center_y = 268, 292
    for r, op, durphase in [(144,0.10,0),(112,0.12,0.12),(80,0.14,0.24)]:
        rg = add(root, "g", {"transform":f"translate({center_x} {center_y})"})
        c = circle(rg, 0, 0, r, fill="none", stroke=t["cyan"], **{"stroke-width":"1", "stroke-opacity":str(op)})
        animate_transform(rg, ["0","18","0","-18","0"], [0,0.25,0.5,0.75,1], dur="20s", type_="rotate")
        # Rotation is decorative; animate the actual ring opacity and radius for a subtle pulse.
        animate(c, "stroke-opacity", [op*0.55,op,op*0.55,op*0.55], [0,0.25+durphase,0.5+durphase,1], dur="20s")
        animate(c, "r", [r,r+4,r,r], [0,0.3+durphase,0.6+durphase,1], dur="20s")
    for dy in [0, 44, 88, 132]:
        line(root, 82, 234+dy, 454, 234+dy, stroke=t["grid"], **{"stroke-width":"1", "stroke-opacity":"0.62"})

    # Big LUGHX pixel wordmark — static-complete, with gentle sweep.
    cell, gap = 12, 3
    word_width = 29*cell + 28*gap
    start_x = center_x - word_width/2
    start_y = 244
    cells = word_cells(GLYPHS, start_x, start_y, cell, gap)
    wg = add(root, "g", {})
    if theme_name == "dark": wg.set("filter", f"url(#{p}Glow)")
    for i, (_, _, _, x, y) in enumerate(cells):
        r = rect(wg, round(x,2), y, cell, cell, rx=3, fill=t["l3"] if i % 4 else t["l4"], opacity="1")
        phase=(i%11)/11*0.10
        animate(r, "opacity", [0.72,1,0.82,1,0.72], [0,0.42+phase,0.50+phase,0.58+phase,1], dur="20s")
    scan = rect(root, 82, 228, 372, 2, rx=1, fill=t["cyan"], opacity="0.08")
    animate(scan, "y", [228,228,400,228], [0,0.12,0.28,1], dur="20s")
    animate(scan, "opacity", [0.03,0.18,0.03,0.03], [0,0.16,0.28,1], dur="20s")
    sheen = rect(root, 86, 238, 32, 174, rx=16, fill=t["cyan"], opacity="0")
    animate(sheen, "x", [84,84,410,84], [0,0.20,0.52,1], dur="20s")
    animate(sheen, "opacity", [0,0.08,0,0], [0,0.22,0.52,1], dur="20s")
    text_el(root, 268, 398, "[ PROFILE / DEVELOPER ]", fill=t["muted"], **{"font-size":"12", "letter-spacing":"1.2px", "text-anchor":"middle"})
    text_el(root, 268, 428, "~/lughx $ ship it", fill=t["faint"], **{"font-size":"13", "text-anchor":"middle"})

    # Right panel.
    text_el(root, 540, 150, "xlughzdev@devos:~$ ./profile.sh --live", fill=t["muted"], **{"font-size":"12"})
    name = text_el(root, 540, 220, "Lughx", fill=t["primary"], **{"font-size":"64", "font-weight":"700"})
    animate(name, "opacity", [0.72,1,0.96,1,0.72], [0,0.04,0.08,0.15,1], dur="20s")
    line(root, 540, 236, 698, 236, stroke=f"url(#{p}Accent)", **{"stroke-width":"2"})
    cursor = rect(root, 705, 172, 3, 58, rx=1.5, fill=t["cyan"], opacity="0.0")
    animate(cursor, "opacity", [0,0,1,1,0,0], [0,0.075,0.078,0.12,0.15,1], dur="20s")
    ok = text_el(root, 974, 150, "[ OK ]", fill=t["emerald"], **{"font-size":"11", "text-anchor":"end"})
    animate(ok, "opacity", [0,0,0.9,0.25,1,1], [0,0.01,0.03,0.055,0.075,1], dur="20s")

    label_x, value_x = 636, 660
    row_y = [278, 310, 342, 374]
    text_el(root, 540, 256, "IDENTITY", fill=t["cyan"], **{"font-size":"11", "letter-spacing":"1.6px"})
    identity = [("NAME","Lughx"),("REAL NAME","Thai Nhat Minh"),("ROLE","JavaScript / Dockerfile developer"),("HANDLE","@xlughzdev")]
    for idx, ((lab,val), y) in enumerate(zip(identity,row_y)):
        text_el(root, label_x, y, lab, fill=t["muted"], **{"font-size":"11", "text-anchor":"end", "letter-spacing":"0.5px"})
        tx = text_el(root, value_x, y, val, fill=t["primary"], **{"font-size":"13"})
        st = 0.08 + idx*0.035
        animate(tx, "opacity", [0,0,1,1], [0,st,st+0.05,1], dur="20s")
        rule = line(root, value_x, y+7, 1080, y+7, stroke=t["grid"], **{"stroke-width":"1", "stroke-opacity":"0.16"})
        animate(rule, "stroke-opacity", [0.06,0.22,0.06,0.06], [0,0.35+idx*0.03,0.55+idx*0.03,1], dur="20s")

    text_el(root, 540, 412, "STACK", fill=t["cyan"], **{"font-size":"11", "letter-spacing":"1.6px"})
    pills = [(540,"JavaScript",t["cyan"]),(676,"Dockerfile",t["emerald"])]
    for idx,(x, lab, accent) in enumerate(pills):
        w = 120 if lab == "JavaScript" else 112
        pg = add(root, "g", {})
        rect(pg, x, 430, w, 30, rx=15, fill=t["panel2"], stroke=accent, **{"stroke-opacity":"0.55"})
        dot=circle(pg, x+15, 445, 4, fill=accent)
        text_el(pg, x+28, 449, lab, fill=t["primary"], **{"font-size":"12"})
        glint=rect(pg,x+w-32,441,10,8,rx=4,fill=accent,opacity="0.18")
        animate_transform(pg,[f"0 0",f"0 {-1.5 if idx==0 else 1.5}","0 0",f"0 {1.2 if idx==0 else -1.2}","0 0"],[0,0.22,0.5,0.74,1],dur="20s",type_="translate")
        animate(glint,"opacity",[0.10,0.34,0.10,0.10],[0,0.3,0.5,1],dur="20s")
        animate(dot,"opacity",[0.55,1,0.55,0.55],[0,0.25,0.5,1],dur="20s")

    text_el(root, 540, 488, "LINKS", fill=t["cyan"], **{"font-size":"11", "letter-spacing":"1.6px"})
    links = [("GitHub","github.com/xlughzdev"),("Facebook","facebook.com/iamlughx")]
    for i,(lab,val) in enumerate(links):
        y = 510 + i*22
        text_el(root, label_x, y, lab, fill=t["muted"], **{"font-size":"11", "text-anchor":"end"})
        text_el(root, value_x, y, val, fill=t["primary"], **{"font-size":"12"})
        sweep = rect(root,value_x-2,y-11,54,2,rx=1,fill=t["cyan"],opacity="0")
        animate(sweep,"x",[value_x-2,value_x-2,1076,value_x-2],[0,0.48+i*0.06,0.70+i*0.06,1],dur="20s")
        animate(sweep,"opacity",[0,0.20,0,0],[0,0.50+i*0.06,0.70+i*0.06,1],dur="20s")

    # Footer contribution sweep with moving highlight.
    y = 566
    start = 540
    for i in range(35):
        rr = rect(root, start+i*15, y, 11, 11, rx=3, fill=t["grid"])
        phase=0.15+i*0.012
        animate(rr, "fill", [t["grid"],t["grid"],t["l3"],t["grid"]], [0,phase,phase+0.03,1], dur="20s")
        animate(rr, "opacity", [0.55,0.55,1,0.55], [0,phase,phase+0.03,1], dur="20s")
    text_el(root, 1116, 594, "xlughzdev", fill=t["faint"], **{"font-size":"10", "text-anchor":"end", "letter-spacing":"1px"})
    return ET.tostring(root, encoding="unicode", short_empty_elements=True)

def deterministic_decoys():
    rng = random.Random(2304)
    glyph_positions = set()
    cx = 3
    for letter in "LUGHX":
        for ry,row in enumerate(GLYPHS[letter]):
            for rx,ch in enumerate(row):
                if ch == "#":
                    glyph_positions.add((cx+rx,ry))
        cx += 6
    candidates = [(x,y) for y in range(7) for x in range(35) if (x,y) not in glyph_positions]
    rng.shuffle(candidates)
    return candidates[:14]


def arena_svg(theme_name: str) -> str:
    t = THEMES[theme_name]
    p = "d" if theme_name == "dark" else "l"
    root = ET.Element(f"{{{NS}}}svg", {"width":"1180", "height":"420", "viewBox":"0 0 1180 420",
        "role":"img", "aria-label":f"Animated contribution-grid arena that spells LUGHX for Lughx, {theme_name} theme"})
    add(root,"title",text=None).text=f"LUGHX space arena ({theme_name} theme)"
    add(root,"desc",text=None).text="A blue spaceship clears stray contribution cells, then builds the pixel word LUGHX and holds it visibly."
    defs_common(root,t,p)
    if theme_name == "dark":
        glow = add(root.find(f"{{{NS}}}defs"), "filter", {"id": f"{p}ArenaGlow", "x":"-40%", "y":"-40%", "width":"180%", "height":"180%"})
        add(glow, "feGaussianBlur", {"stdDeviation":"2.8", "result":"blur"})
        merge=add(glow,"feMerge")
        add(merge,"feMergeNode",{"in":"blur"})
        add(merge,"feMergeNode",{"in":"SourceGraphic"})
    style=add(root,"style"); style.text=f"text{{font-family:{FONT};}}"
    rect(root,0,0,1180,420,fill=f"url(#{p}Bg)")
    rect(root,24,18,1132,384,rx=22,fill=f"url(#{p}Panel)",stroke=t["border"],**{"stroke-width":"1"})
    if theme_name == "dark":
        rect(root,24,18,1132,384,rx=22,fill="#FFFFFF",opacity="0.06",filter=f"url(#{p}Noise)")

    # Ambient orbiting halo behind the arena.
    halo = circle(root,590,190,164,fill="none",stroke=t["cyan"],**{"stroke-width":"1", "stroke-opacity":"0.05"})
    animate(halo,"r",[158,172,158,158],[0,0.28,0.56,1],dur="20s")
    animate(halo,"stroke-opacity",[0.02,0.10,0.02,0.02],[0,0.28,0.56,1],dur="20s")

    # Stars: twinkle + slow drift.
    rng=random.Random(513)
    stars=[]
    for i in range(52):
        x=rng.randint(42,1138); y=rng.randint(28,332); r=rng.choice([0.8,0.9,1.1,1.3])
        base=rng.uniform(0.08 if theme_name=='light' else 0.12,0.32 if theme_name=='light' else 0.58)
        c=circle(root,x,y,r,fill=t["star"],opacity=str(base)); stars.append(c)
    for i,c in enumerate(stars):
        a=0.10 if theme_name=='light' else 0.14
        peak=(0.22 if theme_name=='light' else 0.52) * (0.65 + (i%5)*0.07)
        phase=(i%13)*0.012
        animate(c,"opacity",[a,peak,a,a],[0,0.20+phase,0.40+phase,1],dur="20s")
        if 10 <= i < 18:
            dy=(i%4)-1.5
            dx=4+(i%3)*1.5
            animate_transform(c,["0 0",f"{dx} {dy}",f"{-dx/2} {-dy}","0 0"],[0,0.32,0.67,1],dur="20s",type_="translate")

    # HUD.
    text_el(root,48,42,"LUGHX.EXE",fill=t["primary"],**{"font-size":"11","font-weight":"700","letter-spacing":"1.4px"})
    hud_line=line(root,48,50,260,50,stroke=t["cyan"],**{"stroke-width":"1","stroke-opacity":"0.20"})
    animate(hud_line,"x2",[100,100,260,100],[0,0.18,0.48,1],dur="20s")
    bar_x,bar_y,bar_w,bar_h=948,32,146,8
    rect(root,bar_x,bar_y,bar_w,bar_h,rx=4,fill=t["grid"])
    progress=rect(root,bar_x,bar_y,bar_w,bar_h,rx=4,fill=t["emerald"])
    # Animate from hidden to full width; the static base remains fully visible for fallback.
    animate_transform(progress,["0 0","0 0","1 0","1 0","0 0"],[0,0.225,0.475,0.90,1],dur="20s",type_="scale")
    pglow=rect(root,bar_x,bar_y-2,18,12,rx=6,fill=t["cyan"],opacity="0")
    animate(pglow,"x",[bar_x,bar_x,bar_x+bar_w-18,bar_x],[0,0.22,0.48,1],dur="20s")
    animate(pglow,"opacity",[0,0.22,0,0],[0,0.24,0.48,1],dur="20s")

    x0,y0,cell,gap=34,64,24,8
    pitch=cell+gap
    glyph_data=word_cells(GLYPHS,x0,y0,cell,gap,start_col=3)
    glyph_coord={(round(x,2),round(y,2)):i for i,(_,_,_,x,y) in enumerate(glyph_data)}
    glyph_set=set(glyph_coord)

    # Grid with a subtle scanner that never changes final geometry.
    gg=add(root,"g",{})
    for gy in range(7):
        for gx in range(35):
            x=x0+gx*pitch; y=y0+gy*pitch
            r=rect(gg,x,y,cell,cell,rx=5,fill=t["l0"],opacity="0.96")
            animate(r,"opacity",[0.82,0.96,0.82,0.96],[0,0.30+(gx%5)*0.01,0.50+(gx%5)*0.01,1],dur="20s")

    # Decorative scan beam behind cells.
    beam=rect(root,x0,56,12,230,rx=6,fill=t["cyan"],opacity="0.025")
    animate(beam,"x",[x0,x0,1140,x0],[0,0.12,0.72,1],dur="20s")
    animate(beam,"opacity",[0.02,0.10,0.02,0.02],[0,0.16,0.72,1],dur="20s")

    # Glyph cells: static final state is fully lit; animation temporarily builds them.
    wg=add(root,"g",{})
    if theme_name == "dark": wg.set("filter",f"url(#{p}ArenaGlow)")
    for idx,(_,_,_,x,y) in enumerate(glyph_data):
        r=rect(wg,x,y,cell,cell,rx=5,fill=t["l3"] if idx%4 else t["l4"],opacity="1")
        full_col=round((x-x0)/pitch)
        gy=round((y-y0)/pitch)
        # Bottom-up per column while preserving the exact 4.5–9.5 build window.
        max_rank=28*7-1
        rank=(full_col*7)+(6-gy)
        t_on=4.5 + (rank/max_rank)*4.5
        k0=t_on/20; k1=(t_on+0.14)/20
        animate(r,"opacity",[0,0,1,1,0.98,1],[0,k0,k1,0.475,0.995,1],dur="20s")
        phase=(idx%9)*0.008
        animate(r,"fill",[t["l3"],t["l3"],t["l4"],t["l3"],t["l3"]],[0,k0,k1,0.52+phase,0.90+phase],dur="20s")
        # Ignite ring + expanding outer ripple.
        ring=circle(root,x+cell/2,y+cell/2,5,fill="none",stroke=t["ring"],**{"stroke-width":"1.3","stroke-opacity":"0"})
        animate(ring,"r",[5,5,14,22,5],[0,k0,k1,k1+0.03,1],dur="20s")
        animate(ring,"stroke-opacity",[0,0,0.58,0,0],[0,k0,k1,k1+0.05,1],dur="20s")

    decoys=deterministic_decoys()
    for j,(gx,gy) in enumerate(decoys):
        x=x0+gx*pitch; y=y0+gy*pitch
        d=rect(root,x,y,cell,cell,rx=5,fill=t["l2"],opacity="0")
        appear=0.060+j*0.0015
        hit=0.145+(j%7)*0.004
        animate(d,"opacity",[0,0,0.74,0,0],[0,appear,hit,hit+0.018,1],dur="20s")
        # Hit ring.
        hitring=circle(root,x+cell/2,y+cell/2,5,fill="none",stroke=t["bullet"],**{"stroke-width":"1.5","stroke-opacity":"0"})
        animate(hitring,"r",[5,5,18,5],[0,hit,hit+0.02,hit+0.05],dur="20s")
        animate(hitring,"stroke-opacity",[0,0,0.65,0],[0,hit,hit+0.02,hit+0.05],dur="20s")
        for k,(dx,dy) in enumerate([(-3,-3),(3,-2),(-2,3),(3,3)]):
            shard=line(root,x+cell/2,y+cell/2,x+cell/2+dx*3,y+cell/2+dy*3,stroke=t["bullet"],**{"stroke-width":"2","stroke-linecap":"round","stroke-opacity":"0"})
            animate(shard,"stroke-opacity",[0,0,0.95,0],[0,hit,hit+0.018,hit+0.055],dur="20s")
            animate(shard,"x2",[x+cell/2,x+cell/2+dx*3,x+cell/2+dx*5,x+cell/2+dx*5],[0,hit,hit+0.05,1],dur="20s")
            animate(shard,"y2",[y+cell/2,y+cell/2+dy*3,y+cell/2+dy*5,y+cell/2+dy*5],[0,hit,hit+0.05,1],dur="20s")
        # Bullet with a small trail.
        b=add(root,"use",{"href":"#bullet","transform":f"translate({x+cell/2},348)","opacity":"0"})
        endy=y+cell/2
        t0=0.08+j*0.002; t1=t0+0.012
        animate_transform(b,["0 0","0 0",f"0 {endy-348}",f"0 {endy-348}","0 0"],[0,t0,t1,t1+0.012,1],dur="20s")
        animate(b,"opacity",[0,0,1,1,0,0],[0,t0,t0+0.001,t1,t1+0.012,1],dur="20s")
        trail=rect(root,x+cell/2-1,348,2,32,rx=1,fill=t["bullet"],opacity="0")
        animate(trail,"height",[0,0,32,0,0],[0,t0,t1,t1+0.02,1],dur="20s")
        animate(trail,"opacity",[0,0,0.20,0,0],[0,t0,t1,t1+0.02,1],dur="20s")

    # One bullet per glyph cell for the build phase.
    for idx,(_,_,_,x,y) in enumerate(glyph_data):
        b=add(root,"use",{"href":"#bullet","transform":f"translate({x+cell/2},350)","opacity":"0"})
        t_on=4.5 + (idx/len(glyph_data))*4.5
        k0=t_on/20; k1=(t_on+0.10)/20
        animate_transform(b,["0 0","0 0",f"0 {y+cell/2-350}",f"0 {y+cell/2-350}","0 0"],[0,k0,k1,k1+0.014,1],dur="20s")
        animate(b,"opacity",[0,0,1,1,0,0],[0,k0,k0+0.001,k1,k1+0.014,1],dur="20s")
        trail=rect(root,x+cell/2-1,350,2,18,rx=1,fill=t["bullet"],opacity="0")
        animate(trail,"height",[0,0,18,0,0],[0,k0,k1,k1+0.014,1],dur="20s")
        animate(trail,"opacity",[0,0,0.17,0,0],[0,k0,k1,k1+0.014,1],dur="20s")

    # Ship: intro rise, clearing sweeps, build sweep, idle hover, outro drift.
    ship_wrap=add(root,"g",{})
    ship=add(ship_wrap,"use",{"href":"#ship","transform":"translate(573,328)"})
    animate_transform(ship_wrap,["-180 80","-180 80","-60 0","60 0","0 -3","160 80"],[0,0.06,0.225,0.47,0.90,1],dur="20s",type_="translate")
    animate_transform(ship, ["0 0","0 1.6","0 0","0 -1.6","0 0"],[0,0.20,0.50,0.72,1],dur="20s",type_="translate")
    # Ship wake particles.
    for i in range(6):
        wc=circle(root,573-22-i*10,356+i%2*3,1.8-(i*0.15),fill=t["flame"],opacity="0")
        animate(wc,"opacity",[0,0.45,0,0],[0,0.20+(i*0.015),0.28+(i*0.02),1],dur="20s")
        animate_transform(wc,["0 0",f"{-8-i*2} {2+(i%2)*2}",f"{-18-i*2} {(-2 if i%2 else 3)}","0 0"],[0,0.20+(i*0.015),0.30+(i*0.015),1],dur="20s",type_="translate")

    # Hold phase brightness wave — no bullets cross the word.
    wave=rect(root, x0, y0, 6, 216, fill=t["cyan"], opacity="0")
    animate(wave,"x",[x0,x0,1146,x0],[0,0.47,0.90,1],dur="20s")
    animate(wave,"opacity",[0,0,0.08,0,0],[0,0.47,0.60,0.72,1],dur="20s")

    text_el(root,590,388,"xlughzdev · Lughx",fill=t["muted"],**{"font-size":"11","text-anchor":"middle","letter-spacing":"0.8px"})
    return ET.tostring(root,encoding="unicode",short_empty_elements=True)

def build():
    outputs = {}
    for theme in ("dark","light"):
        outputs[f"hero-{theme}.svg"] = hero_svg(theme)
        outputs[f"arena-{theme}.svg"] = arena_svg(theme)
    readme = """<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./hero-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="./hero-light.svg">
    <img src="./hero-dark.svg" alt="Lughx (Thai Nhat Minh), JavaScript and Dockerfile developer, terminal-style profile card">
  </picture>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./arena-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="./arena-light.svg">
    <img src="./arena-dark.svg" alt="Animated contribution grid where a pixel spaceship clears stray cells and spells LUGHX">
  </picture>
</div>

# Lughx

**JavaScript / Dockerfile developer** · **Thai Nhat Minh** · GitHub [`@xlughzdev`](https://github.com/xlughzdev)

## About

- **Nickname:** Lughx
- **Real name:** Thai Nhat Minh
- **GitHub:** [xlughzdev](https://github.com/xlughzdev)

## Stack

`JavaScript` · `Dockerfile`

## Connect

- GitHub: [github.com/xlughzdev](https://github.com/xlughzdev)
- Facebook: [facebook.com/iamlughx](https://www.facebook.com/iamlughx)
- TikTok: [@lughx.08](https://www.tiktok.com/@lughx.08)
- Discord profile: `yc5p`
- Discord server: [discord.gg/lughxshop](https://discord.gg/lughxshop)

## Motion

The profile uses self-contained SVG + SMIL animation: signal pulses, scanlines, contribution-cell sweeps, star twinkles, spaceship motion, bullet trails, impact rings, and the LUGHX build sequence. No JavaScript or external assets are required by the SVGs.

Regenerate everything with:

```bash
python3 build_svgs.py

"""
outputs["README.md"] = readme
for name, content in outputs.items():
(OUT / name).write_text(content, encoding="utf-8")
print("Generated:")
for name, content in outputs.items():
print(f"  {name}: {len(content.encode('utf-8')):,} bytes")

if name == "main":
build()
