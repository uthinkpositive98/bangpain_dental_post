"""Cartoon toolkit for clinic Reels: stick-figure people, the tooth mascot, germs, teeth, and detail helpers.

Everything returns SVG strings for a 1080x1920 canvas. Episodes compose scenes from these in videos/<ep>/scenes.py,
then tools/build_frames.py renders them. See VIDEO_GUIDE.md for art direction.
"""
import math, random

W, H = 1080, 1920
K = "#1d1d1f"          # outline colour
TEAL, TEAL_D, ORANGE = "#138a8f", "#0e5e63", "#f08a3c"
SW = 9                 # main stroke width

# ---------- characters ----------
def face(mood):
    """Moods: happy, big (laughing), talk, worried, sad, bored, squint (disgusted), surprised, scared, angry."""
    eyes = f'<circle cx="-24" cy="-8" r="8" fill="{K}"/><circle cx="24" cy="-8" r="8" fill="{K}"/>'
    brows = {
        "happy": f'<path d="M-40 -34 q16 -10 30 0 M10 -34 q16 -10 30 0" fill="none" stroke="{K}" stroke-width="7" stroke-linecap="round"/>',
        "worried": f'<path d="M-42 -30 l30 -12 M12 -42 l30 12" fill="none" stroke="{K}" stroke-width="7" stroke-linecap="round"/>',
        "sad": f'<path d="M-42 -32 l30 -12 M12 -44 l30 12" fill="none" stroke="{K}" stroke-width="7" stroke-linecap="round"/>',
        "bored": f'<path d="M-40 -30 h30 M10 -30 h30" fill="none" stroke="{K}" stroke-width="7" stroke-linecap="round"/>',
        "squint": f'<path d="M-42 -30 l30 8 M12 -22 l30 -8" fill="none" stroke="{K}" stroke-width="7" stroke-linecap="round"/>',
        "surprised": f'<path d="M-42 -44 q16 -14 30 -4 M12 -48 q16 -10 30 4" fill="none" stroke="{K}" stroke-width="7" stroke-linecap="round"/>',
        "scared": f'<path d="M-42 -30 l30 -12 M12 -42 l30 12" fill="none" stroke="{K}" stroke-width="7" stroke-linecap="round"/>',
        "angry": f'<path d="M-42 -42 l30 12 M12 -30 l30 -12" fill="none" stroke="{K}" stroke-width="8" stroke-linecap="round"/>',
    }
    mouth = {
        "happy": f'<path d="M-26 22 q26 26 52 0" fill="none" stroke="{K}" stroke-width="7" stroke-linecap="round"/>',
        "big": f'<path d="M-30 18 q30 40 60 0 z" fill="{K}"/><path d="M-18 30 q18 12 36 0" fill="#ff8a80"/>',
        "talk": f'<ellipse cx="0" cy="26" rx="20" ry="15" fill="{K}"/>',
        "worried": f'<path d="M-22 32 q22 -18 44 0" fill="none" stroke="{K}" stroke-width="7" stroke-linecap="round"/>',
        "sad": f'<path d="M-22 34 q22 -20 44 0" fill="none" stroke="{K}" stroke-width="7" stroke-linecap="round"/>',
        "bored": f'<path d="M-18 28 h36" stroke="{K}" stroke-width="7" stroke-linecap="round"/>',
        "squint": f'<path d="M-20 30 q10 -8 20 0 q10 8 20 0" fill="none" stroke="{K}" stroke-width="7" stroke-linecap="round"/>',
        "surprised": f'<ellipse cx="0" cy="30" rx="14" ry="18" fill="{K}"/>',
        "scared": f'<path d="M-24 22 h48 v14 q-24 14 -48 0 z" fill="{K}"/><path d="M-20 24 h40 v6 h-40z" fill="#fff"/>',
        "angry": f'<path d="M-22 34 q22 -16 44 0" fill="none" stroke="{K}" stroke-width="8" stroke-linecap="round"/>',
    }
    eye_style = eyes
    if mood == "bored":
        eye_style = f'<path d="M-34 -6 h20 M14 -6 h20" stroke="{K}" stroke-width="8" stroke-linecap="round"/>'
    if mood == "squint":
        eye_style = f'<path d="M-34 -10 l20 6 l-20 6 M34 -10 l-20 6 l20 6" fill="none" stroke="{K}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>'
    return eye_style + brows.get(mood, brows["happy"]) + mouth.get(mood, mouth["happy"])


def person(x, y, s=1.0, mood="happy", shirt=TEAL, hair=True, arms=((-110, 60), (110, 60)),
           legs=((-55, 200), (55, 200)), rot=0, mouth_override=None, extra=""):
    """Stick figure. (x,y) = hip point. Arms given as hand offsets from shoulder."""
    neck = (0, -230)
    shoulder = (0, -200)
    hair_svg = (f'<path d="M-46 -60 q10 -40 40 -34 q8 -26 34 -10 q24 -8 26 22 q-30 -14 -52 -2 q-24 -12 -48 24 z" fill="{K}"/>'
                if hair else "")
    head = (f'<g transform="translate(0,-310)"><circle r="80" fill="#fff" stroke="{K}" stroke-width="{SW}"/>'
            f'{hair_svg}{face(mood)}{mouth_override or ""}</g>')
    shirt_svg = (f'<path d="M-52 -215 L52 -215 L64 -150 L44 -146 L42 -40 L-42 -40 L-44 -146 L-64 -150 Z" '
                 f'fill="{shirt}" stroke="{K}" stroke-width="7" stroke-linejoin="round"/>')
    a = "".join(f'<line x1="{shoulder[0]}" y1="{shoulder[1]}" x2="{shoulder[0]+ax}" y2="{shoulder[1]+ay}" stroke="{K}" '
                f'stroke-width="{SW}" stroke-linecap="round"/><circle cx="{shoulder[0]+ax}" cy="{shoulder[1]+ay}" r="9" fill="{K}"/>'
                for ax, ay in arms)
    l = "".join(f'<line x1="0" y1="0" x2="{lx}" y2="{ly}" stroke="{K}" stroke-width="{SW}" stroke-linecap="round"/>'
                f'<ellipse cx="{lx + (12 if lx >= 0 else -12)}" cy="{ly+4}" rx="26" ry="11" fill="{K}"/>' for lx, ly in legs)
    body = f'<line x1="0" y1="{neck[1]}" x2="0" y2="0" stroke="{K}" stroke-width="{SW}" stroke-linecap="round"/>'
    return (f'<g transform="translate({x},{y}) rotate({rot}) scale({s})">{l}{body}{a}{shirt_svg}{head}{extra}</g>')


def tooth_path(w=1.0):
    return ("M20 40 C 20 -10, 110 -10, 130 20 C 150 -10, 240 -10, 240 40 C 240 120, 215 160, 205 250 "
            "C 198 300, 160 300, 152 250 C 145 200, 115 200, 108 250 C 100 300, 62 300, 55 250 "
            "C 45 160, 20 120, 20 40 Z")


def mascot(x, y, s=1.0, wave=False, item=""):
    arm_r = (f'<path d="M232 120 q50 -40 60 -100" fill="none" stroke="{K}" stroke-width="10" stroke-linecap="round"/>'
             f'<circle cx="292" cy="20" r="14" fill="#fff" stroke="{K}" stroke-width="7"/>' if wave else
             f'<path d="M232 130 q40 10 70 0" fill="none" stroke="{K}" stroke-width="10" stroke-linecap="round"/>'
             f'<circle cx="302" cy="130" r="14" fill="#fff" stroke="{K}" stroke-width="7"/>')
    return f'''<g transform="translate({x},{y}) scale({s}) translate(-130,-140)">
      <path d="M28 130 q-40 10 -60 50" fill="none" stroke="{K}" stroke-width="10" stroke-linecap="round"/>
      <circle cx="-32" cy="180" r="14" fill="#fff" stroke="{K}" stroke-width="7"/>
      {arm_r}
      <path d="{tooth_path()}" fill="#fff" stroke="{K}" stroke-width="9" stroke-linejoin="round"/>
      <path d="M40 150 q90 40 180 0 l-6 34 q-84 36 -168 0 z" fill="{TEAL}" stroke="{K}" stroke-width="6" stroke-linejoin="round"/>
      <path d="M150 168 l40 70 l26 -10 l-36 -64 z" fill="{TEAL}" stroke="{K}" stroke-width="6" stroke-linejoin="round"/>
      <path d="M190 238 l26 -10" stroke="{ORANGE}" stroke-width="8"/>
      <path d="M60 18 q70 -40 140 0" fill="none" stroke="#9aa5ab" stroke-width="10"/>
      <circle cx="130" cy="6" r="26" fill="#dff6ff" stroke="{K}" stroke-width="6"/><circle cx="130" cy="6" r="10" fill="#fff" stroke="#9aa5ab" stroke-width="4"/>
      <ellipse cx="96" cy="84" rx="16" ry="20" fill="{K}"/><ellipse cx="164" cy="84" rx="16" ry="20" fill="{K}"/>
      <circle cx="102" cy="76" r="6" fill="#fff"/><circle cx="170" cy="76" r="6" fill="#fff"/>
      <ellipse cx="70" cy="112" rx="18" ry="10" fill="#ffb3a7"/><ellipse cx="190" cy="112" rx="18" ry="10" fill="#ffb3a7"/>
      <path d="M106 112 q24 26 48 0" fill="none" stroke="{K}" stroke-width="8" stroke-linecap="round"/>
      {item}
    </g>'''


def germ(x, y, s=1.0, color="#9b59d0", hat="", flip=False, scared=False):
    eyes = (f'<circle cx="-14" cy="-6" r="9" fill="#fff" stroke="{K}" stroke-width="4"/><circle cx="14" cy="-6" r="9" fill="#fff" stroke="{K}" stroke-width="4"/>'
            f'<circle cx="-12" cy="-4" r="4" fill="{K}"/><circle cx="16" cy="-4" r="4" fill="{K}"/>')
    mouth = (f'<ellipse cx="0" cy="20" rx="10" ry="12" fill="{K}"/>' if scared else
             f'<path d="M-18 14 q18 18 36 0 q-18 6 -36 0z" fill="{K}"/>')
    blob = ("M-40 0 C -44 -34, -10 -50, 10 -42 C 34 -50, 50 -20, 42 4 C 52 30, 20 48, 0 42 "
            "C -24 50, -50 30, -40 0 Z")
    return (f'<g transform="translate({x},{y}) scale({-s if flip else s},{s})">'
            f'<path d="M-30 30 l-14 18 M30 30 l14 18" stroke="{K}" stroke-width="6" stroke-linecap="round"/>'
            f'<path d="{blob}" fill="{color}" stroke="{K}" stroke-width="6"/>'
            f'<circle cx="-24" cy="-26" r="5" fill="#fff" opacity=".5"/>{eyes}{mouth}{hat}</g>')


def page(body, bg):
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden;font-family:'Loma',sans-serif;}}</style></head>
<body><svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">
<defs>
 <linearGradient id="night" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1f2a4d"/><stop offset="1" stop-color="#3b4a7a"/></linearGradient>
 <linearGradient id="dusk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3d4f8f"/><stop offset=".6" stop-color="#8a8fc4"/><stop offset="1" stop-color="#c9a7c4"/></linearGradient>
 <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8fd3f4"/><stop offset="1" stop-color="#e6f7ff"/></linearGradient>
 <radialGradient id="mouth" cx=".5" cy=".5" r=".6"><stop offset="0" stop-color="#7a1f35"/><stop offset="1" stop-color="#3d0b19"/></radialGradient>
 <radialGradient id="lamp" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#ffe9a8" stop-opacity=".8"/><stop offset="1" stop-color="#ffe9a8" stop-opacity="0"/></radialGradient>
 <pattern id="tiles" width="90" height="90" patternUnits="userSpaceOnUse"><rect width="90" height="90" fill="#e8f6f5"/><path d="M0 0 H90 V90" fill="none" stroke="#c4e3e1" stroke-width="4"/></pattern>
 <pattern id="bricks" width="60" height="40" patternUnits="userSpaceOnUse"><rect width="60" height="40" fill="#d9b26a"/><path d="M0 0 H60 M0 20 H60 M20 0 V20 M50 20 V40" stroke="#8a6a2e" stroke-width="4"/></pattern>
</defs>
<rect width="{W}" height="{H}" fill="{bg}"/>{body}</svg></body></html>'''




# ---------- detail helpers (use several in every scene) ----------
def shadow(x, y, w=180, opacity=0.18):
    """Soft ground shadow under a character or object."""
    return f'<ellipse cx="{x}" cy="{y}" rx="{w/2}" ry="{w/9}" fill="#000" opacity="{opacity}"/>'


def vignette(strength=0.35):
    """Darken the edges a little; gives depth like hand-drawn backgrounds. Put last in a scene body."""
    return (f'<defs><radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".6" stop-color="#000" stop-opacity="0"/>'
            f'<stop offset="1" stop-color="#000" stop-opacity="{strength}"/></radialGradient></defs>'
            f'<rect width="{W}" height="{H}" fill="url(#vig)"/>')


def speckles(x, y, w, h, n=60, color="#000", opacity=0.08, seed=1, rmax=5):
    """Random small dots — plaster/concrete/grain texture on walls and floors."""
    rnd = random.Random(seed)
    return "".join(f'<circle cx="{x + rnd.random()*w:.0f}" cy="{y + rnd.random()*h:.0f}" r="{1 + rnd.random()*rmax:.1f}" '
                   f'fill="{color}" opacity="{opacity}"/>' for _ in range(n))


def cracks(x, y, s=1.0, color=K):
    """A wall crack."""
    return (f'<path transform="translate({x},{y}) scale({s})" d="M0 0 l18 30 l-8 26 l22 34 M18 30 l26 6 M10 56 l-20 14" '
            f'fill="none" stroke="{color}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" opacity=".55"/>')


def planks(y, h, color="#b98b5e", line="#8a6440", width=W, gap=120, seed=2):
    """Wooden floor of horizontal planks with grain lines."""
    rnd = random.Random(seed)
    out = [f'<rect x="0" y="{y}" width="{width}" height="{h}" fill="{color}"/>']
    for row in range(int(h // 60) + 1):
        yy = y + row * 60
        out.append(f'<line x1="0" y1="{yy}" x2="{width}" y2="{yy}" stroke="{line}" stroke-width="4"/>')
        off = rnd.randint(0, gap)
        for xx in range(-off, width, gap * 3):
            out.append(f'<line x1="{xx}" y1="{yy}" x2="{xx}" y2="{yy+60}" stroke="{line}" stroke-width="4"/>')
            out.append(f'<path d="M{xx+30} {yy+22} q40 -8 80 0" fill="none" stroke="{line}" stroke-width="2" opacity=".5"/>')
    return "".join(out)


def window(x, y, w, h, sky="#bfe9f5", night=False):
    sky = "#0f1830" if night else sky
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{sky}" stroke="{K}" stroke-width="9"/>'
            f'<path d="M{x+w/2} {y} V{y+h} M{x} {y+h/2} H{x+w}" stroke="{K}" stroke-width="7"/>'
            f'<path d="M{x+20} {y+30} l40 -14 M{x+24} {y+70} l70 -24" stroke="#fff" stroke-width="8" stroke-linecap="round" opacity=".5"/>')


def plant(x, y, s=1.0):
    return (f'<g transform="translate({x},{y}) scale({s})"><path d="M-40 100 h80 l-12 -100 h-56 z" fill="{ORANGE}" stroke="{K}" stroke-width="6"/>'
            f'<path d="M0 0 q-60 -80 -20 -150 M0 0 q50 -70 30 -160 M0 0 q-10 -90 10 -190" fill="none" stroke="#3f9e5a" stroke-width="16" stroke-linecap="round"/></g>')


def ceiling_lamp(x, y, length=140, on=True):
    glow = f'<circle cx="{x}" cy="{y+length+40}" r="220" fill="#ffe9a8" opacity=".25"/>' if on else ""
    return (f'{glow}<line x1="{x}" y1="0" x2="{x}" y2="{y+length}" stroke="{K}" stroke-width="5"/>'
            f'<path d="M{x-60} {y+length+50} q60 -80 120 0 z" fill="#ffd27a" stroke="{K}" stroke-width="7"/>')


def motion_lines(x, y, n=3, length=60, angle=0):
    return "".join(f'<line x1="{x}" y1="{y+i*24}" x2="{x+length*math.cos(math.radians(angle))}" '
                   f'y2="{y+i*24+length*math.sin(math.radians(angle))}" stroke="{K}" stroke-width="6" stroke-linecap="round"/>'
                   for i in range(n))


def sparkle(x, y, s=1.0, color="#fff"):
    return f'<path transform="translate({x},{y}) scale({s})" d="M0 -24 l7 17 17 7 -17 7 -7 17 -7 -17 -17 -7 17 -7z" fill="{color}"/>'


def sweat(x, y, s=1.0):
    return f'<path transform="translate({x},{y}) scale({s})" d="M0 0 q-14 24 0 30 q14 -6 0 -30z" fill="#7fd3ff" stroke="{K}" stroke-width="3"/>'


def speech_bubble(x, y, w, h, text, size=44, tail="left"):
    """Rounded bubble with short Thai text (keep to a few words; font Loma)."""
    tx = x + 60 if tail == "left" else x + w - 60
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="34" fill="#fff" stroke="{K}" stroke-width="7"/>'
            f'<path d="M{tx-20} {y+h-4} l-10 50 l50 -50 z" fill="#fff" stroke="{K}" stroke-width="7" stroke-linejoin="round"/>'
            f'<rect x="{tx-24}" y="{y+h-12}" width="62" height="14" fill="#fff"/>'
            f'<text x="{x+w/2}" y="{y+h/2+size*0.36}" text-anchor="middle" font-size="{size}" font-weight="bold" '
            f'font-family="Loma" fill="{K}">{text}</text>')
