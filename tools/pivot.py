"""Pivot-Animator-style animation toolkit for the clinic Reels (1080x1920, 30 fps).

How Pivot Animator works, and how this file copies it: every character is a skeleton of joints joined by
"sticks". You pose the joints on key frames and the frames in between are tweened. Here a pose is a `P(...)`
(angles in degrees), a timeline is a list of (time_s, P) key frames, and `stickman(track, t)` draws the figure
at time t with smooth easing, breathing, blinking and squash-and-stretch added on top.

Look: clean high-contrast stickman explainer style (white round head, black oval eyes, thick ink outlines,
expressive eyebrows) with Ghibli-like painted colour — soft skies, big cumulus clouds, layered green hills,
warm light, paper grain. Backgrounds are painted once per scene (`BG[...]`), characters and props every frame.

Scene files (videos/<ep>/scenes.py) define SCENES = [Scene(...), ...]; tools/pivot_render.py renders them.
"""
import math, random

W, H, FPS = 1080, 1920, 30
INK = "#2b2622"                 # warm near-black outline
HOODIE, HOODIE_D, HOODIE_L = "#f08a3c", "#c9652a", "#ffb27a"
TEAL, TEAL_D = "#138a8f", "#0e5e63"
SKIN = "#ffffff"
BLUSH = "#ffaaa0"


# ---------------------------------------------------------------- maths / easing
def clamp(v, a=0.0, b=1.0):
    return max(a, min(b, v))


def lerp(a, b, k):
    return a + (b - a) * k


def ease(k, kind="inout"):
    k = clamp(k)
    if kind == "linear":
        return k
    if kind == "in":
        return k * k * k
    if kind == "out":
        return 1 - (1 - k) ** 3
    if kind == "back":                      # overshoot then settle (snappy cartoon pose)
        c = 1.70158
        k -= 1
        return 1 + (c + 1) * k ** 3 + c * k ** 2
    if kind == "bounce":
        n, d = 7.5625, 2.75
        if k < 1 / d:
            return n * k * k
        if k < 2 / d:
            k -= 1.5 / d
            return n * k * k + .75
        if k < 2.5 / d:
            k -= 2.25 / d
            return n * k * k + .9375
        k -= 2.625 / d
        return n * k * k + .984375
    return k * k * (3 - 2 * k) if kind == "smooth" else (4 * k ** 3 if k < .5 else 1 - (-2 * k + 2) ** 3 / 2)


def d(a):                               # unit vector for an angle: 0 = straight down, 90 = right, 180 = up
    r = math.radians(a)
    return math.sin(r), math.cos(r)


def track_value(track, t, default=0.0):
    """Interpolate a list of (time, value[, easing]) keys. Values may be numbers or tuples."""
    if not track:
        return default
    if t <= track[0][0]:
        return track[0][1]
    for (t0, v0, *e0), (t1, v1, *e1) in zip(track, track[1:]):
        if t0 <= t <= t1:
            k = ease((t - t0) / max(1e-6, t1 - t0), e1[0] if e1 else "inout")
            if isinstance(v0, tuple):
                return tuple(lerp(a, b, k) for a, b in zip(v0, v1))
            return lerp(v0, v1, k)
    return track[-1][1]


# ---------------------------------------------------------------- poses
ANGLES = ("rot", "lean", "neck", "lsh", "lel", "rsh", "rel", "lhip", "lkn", "rhip", "rkn")


class P:
    """A stickman pose.  x,y = hip point on the canvas.  s = scale (1 ≈ 600 px tall).

    Angles (degrees). Arms/legs are mirrored so the same number means "outward" on both sides:
      lsh/rsh  shoulder: 0 arm hangs down, 90 straight out sideways, 160 up over the head, -30 across the body
      lel/rel  elbow bend (positive bends the forearm up/inward)
      lhip/rhip 0 leg straight down, + spreads outward;   lkn/rkn knee bend
      lean     torso lean (+ = to the right),  rot = whole-body rotation,  neck = head tilt
    Face: mood (see FACES), look=(dx,dy) pupil offset -1..1, turn -1..1 (face turned left/right),
          sx/sy squash-stretch, hood=True draws the hood up.
    """

    def __init__(self, x=540, y=1200, s=1.0, rot=0, lean=0, neck=0, lsh=12, lel=8, rsh=12, rel=8,
                 lhip=8, lkn=0, rhip=8, rkn=0, mood="happy", look=(0, 0), turn=0.0, sx=1.0, sy=1.0,
                 sweat=False, blush=True, hand_l=None, hand_r=None, front=""):
        self.x, self.y, self.s = x, y, s
        self.rot, self.lean, self.neck = rot, lean, neck
        self.lsh, self.lel, self.rsh, self.rel = lsh, lel, rsh, rel
        self.lhip, self.lkn, self.rhip, self.rkn = lhip, lkn, rhip, rkn
        self.mood, self.look, self.turn = mood, look, turn
        self.sx, self.sy, self.sweat, self.blush = sx, sy, sweat, blush
        self.hand_l, self.hand_r = hand_l, hand_r      # optional SVG drawn in the hand (e.g. toothbrush())
        self.front = front                             # 'l'/'r': draw that arm over the face (facepalm, thinking)

    def but(self, **kw):
        """Copy with changes:  base.but(rsh=150, mood='big')"""
        p = P.__new__(P)
        p.__dict__ = dict(self.__dict__)
        p.__dict__.update(kw)
        return p


def tween(p0, p1, k):
    p = p0.but()
    for a in ("x", "y", "s", "sx", "sy", "turn") + ANGLES:
        setattr(p, a, lerp(getattr(p0, a), getattr(p1, a), k))
    p.look = (lerp(p0.look[0], p1.look[0], k), lerp(p0.look[1], p1.look[1], k))
    for a in ("mood", "sweat", "blush", "hand_l", "hand_r", "front"):
        setattr(p, a, getattr(p1 if k >= .5 else p0, a))
    return p


def pose_at(track, t):
    """track = [(t, P), (t, P, 'back'), ...] -> tweened P at time t (Pivot's in-between frames)."""
    if t <= track[0][0]:
        return track[0][1]
    for (t0, p0, *_), (t1, p1, *e) in zip(track, track[1:]):
        if t0 <= t <= t1:
            return tween(p0, p1, ease((t - t0) / max(1e-6, t1 - t0), e[0] if e else "inout"))
    return track[-1][1]


# ready-made poses (combine with .but(x=..., y=..., s=...))
STAND = P()
WAVE = P(rsh=150, rel=40, mood="big")
POINT = P(rsh=95, rel=-5, mood="talk", look=(1, 0))
SHRUG = P(lsh=60, lel=110, rsh=60, rel=110, mood="worried", neck=-8)
CHEER = P(lsh=128, lel=-18, rsh=128, rel=-18, mood="big", lhip=16, rhip=16)
SHOCK = P(lsh=120, lel=60, rsh=120, rel=60, mood="scared", lhip=18, rhip=18, sweat=True)
SAD = P(lsh=6, lel=2, rsh=6, rel=2, lean=0, neck=12, mood="sad")
THINK = P(rsh=30, rel=140, lsh=-20, lel=70, mood="think", neck=-10, look=(.6, -.8), front="r")
FACEPALM = P(rsh=40, rel=160, lsh=-20, lel=80, mood="sad", neck=14, front="r")
HANDS_HIPS = P(lsh=45, lel=-110, rsh=45, rel=-110, mood="smug")
SIT = P(lhip=80, lkn=-85, rhip=80, rkn=-85, lsh=20, rsh=20)


def walk(base, t, speed=180, x0=None, stride=28, period=0.9):
    """Walk cycle pose at time t (moves right for speed>0)."""
    ph = 2 * math.pi * t / period
    p = base.but()
    p.x = (base.x if x0 is None else x0) + speed * t
    sw = math.sin(ph)
    p.lhip, p.rhip = 6 + stride * sw, 6 - stride * sw
    p.lkn, p.rkn = -max(0, 30 * math.sin(ph + 1.2)), -max(0, 30 * math.sin(ph + 1.2 + math.pi))
    p.lsh, p.rsh = 10 - 22 * sw, 10 + 22 * sw
    p.lel, p.rel = 20, 20
    p.y = base.y - 10 * abs(math.cos(ph))
    p.lean = base.lean + (4 if speed > 0 else -4)
    return p


def run(base, t, speed=520, x0=None, period=0.42):
    p = walk(base, t, speed, x0, stride=46, period=period)
    p.lel = p.rel = 85
    p.lean = base.lean + (14 if speed > 0 else -14)
    p.y -= 14
    return p


def hop(base, t, height=120, period=0.6):
    """Happy bouncing in place with squash-and-stretch."""
    k = (t % period) / period
    up = math.sin(math.pi * k)
    p = base.but()
    p.y = base.y - height * up
    p.sy = 1 + .08 * up - (.10 if k < .08 or k > .92 else 0)
    p.sx = 2 - p.sy
    return p


def shake(t, amp=8, freq=24):
    return amp * math.sin(t * freq * 2.1), amp * .6 * math.cos(t * freq * 1.7)


# ---------------------------------------------------------------- faces
def _brow(x, y, ang, s, w=7):
    dx, dy = 15 * math.cos(math.radians(ang)), 15 * math.sin(math.radians(ang))
    return (f'<path d="M{x - dx:.1f} {y - dy:.1f} L{x + dx:.1f} {y + dy:.1f}" stroke="{INK}" stroke-width="{w}" '
            f'stroke-linecap="round"/>')


FACES = ("happy", "big", "talk", "smile", "smug", "worried", "sad", "cry", "scared", "angry", "surprised",
         "think", "bored", "sleepy", "disgust", "love", "dizzy", "determined")


def face(mood="happy", look=(0, 0), turn=0.0, blink=0.0, blush=True):
    """Face features centred on (0,0) in a head of radius 72."""
    ox = turn * 18
    lx, ly = look[0] * 5, look[1] * 4
    ex = (-25 + ox, 25 + ox)
    ey = -4
    out = []
    # brows: (angle left, angle right, lift)
    brow = {"happy": (-8, 8, 0), "smile": (-6, 6, 0), "big": (-12, 12, -4), "talk": (-5, 5, 0),
            "smug": (-4, 14, 4), "worried": (18, -18, -2), "sad": (20, -20, 0), "cry": (22, -22, 0),
            "scared": (22, -22, -10), "angry": (-24, 24, 6), "surprised": (-10, 10, -14),
            "think": (10, -6, -6), "bored": (0, 0, 6), "sleepy": (0, 0, 8), "disgust": (-18, 10, 4),
            "love": (-8, 8, -4), "dizzy": (10, -10, -4), "determined": (-22, 22, 4)}[mood]
    out.append(_brow(ex[0], -38 + brow[2], -brow[0], 1))
    out.append(_brow(ex[1], -38 + brow[2], brow[1], 1))
    # eyes
    if mood in ("happy", "big") and blink < .5:
        for x in ex:
            out.append(f'<path d="M{x - 11} {ey + 3} q11 -14 22 0" fill="none" stroke="{INK}" stroke-width="7" '
                       f'stroke-linecap="round"/>')
    elif mood == "love":
        for x in ex:
            out.append(f'<path transform="translate({x},{ey})" d="M0 9 C-16 -2 -10 -16 0 -8 C10 -16 16 -2 0 9Z" '
                       f'fill="#e8455a" stroke="{INK}" stroke-width="3"/>')
    elif mood == "dizzy":
        for x in ex:
            out.append(f'<path transform="translate({x},{ey})" d="M-9 -9 L9 9 M9 -9 L-9 9" stroke="{INK}" '
                       f'stroke-width="6" stroke-linecap="round"/>')
    elif mood in ("bored", "sleepy") or blink >= .5:
        for x in ex:
            out.append(f'<path d="M{x - 11} {ey + 2} q11 {8 if mood == "sleepy" else 0} 22 0" fill="none" '
                       f'stroke="{INK}" stroke-width="7" stroke-linecap="round"/>')
    else:
        ry = {"surprised": 17, "scared": 16, "angry": 11, "disgust": 9, "determined": 12}.get(mood, 14)
        rx = 10 if mood not in ("surprised", "scared") else 11
        for x in ex:
            out.append(f'<ellipse cx="{x + lx:.1f}" cy="{ey + ly:.1f}" rx="{rx}" ry="{ry * (1 - blink):.1f}" fill="{INK}"/>'
                       f'<circle cx="{x + lx + 3.5:.1f}" cy="{ey + ly - 5:.1f}" r="3.6" fill="#fff"/>'
                       f'<circle cx="{x + lx - 3:.1f}" cy="{ey + ly + 5:.1f}" r="1.6" fill="#fff" opacity=".8"/>')
    if blush and mood not in ("angry", "scared", "disgust"):
        for x in ex:
            out.append(f'<ellipse cx="{x + (-6 if x < ox else 6)}" cy="20" rx="13" ry="7" fill="{BLUSH}" opacity=".75"/>')
    # mouth
    m = {
        "happy": f'<path d="M-18 22 q18 20 36 0" fill="none" stroke="{INK}" stroke-width="7" stroke-linecap="round"/>',
        "smile": f'<path d="M-14 24 q14 12 28 0" fill="none" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>',
        "big": f'<path d="M-24 18 q24 38 48 0 z" fill="{INK}" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>'
               f'<path d="M-13 32 q13 9 26 0" fill="#ff8a80"/>',
        "talk": f'<ellipse cx="0" cy="27" rx="13" ry="10" fill="{INK}"/><ellipse cx="0" cy="31" rx="7" ry="4" fill="#ff8a80"/>',
        "smug": f'<path d="M-14 28 q16 6 30 -8" fill="none" stroke="{INK}" stroke-width="7" stroke-linecap="round"/>',
        "worried": f'<path d="M-16 32 q8 -8 16 -2 q8 6 16 -2" fill="none" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>',
        "sad": f'<path d="M-16 34 q16 -16 32 0" fill="none" stroke="{INK}" stroke-width="7" stroke-linecap="round"/>',
        "cry": f'<path d="M-18 30 q18 -14 36 0 q-18 10 -36 0z" fill="{INK}"/>',
        "scared": f'<path d="M-20 18 h40 v12 q-20 14 -40 0z" fill="{INK}"/><path d="M-16 20 h32 v5 h-32z" fill="#fff"/>',
        "angry": f'<path d="M-18 34 q18 -14 36 0" fill="none" stroke="{INK}" stroke-width="8" stroke-linecap="round"/>',
        "surprised": f'<ellipse cx="0" cy="30" rx="11" ry="14" fill="{INK}"/>',
        "think": f'<path d="M-6 30 h18" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>',
        "bored": f'<path d="M-14 28 h28" stroke="{INK}" stroke-width="7" stroke-linecap="round"/>',
        "sleepy": f'<ellipse cx="4" cy="30" rx="7" ry="9" fill="{INK}"/>',
        "disgust": f'<path d="M-18 30 q9 -8 18 0 q9 8 18 0" fill="none" stroke="{INK}" stroke-width="7" stroke-linecap="round"/>',
        "love": f'<path d="M-18 22 q18 22 36 0" fill="none" stroke="{INK}" stroke-width="7" stroke-linecap="round"/>',
        "dizzy": f'<path d="M-16 30 q8 -8 16 0 q8 8 16 0" fill="none" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>',
        "determined": f'<path d="M-16 28 h32" stroke="{INK}" stroke-width="8" stroke-linecap="round"/>',
    }[mood]
    out.append(f'<g transform="translate({ox * .9:.1f},0)">{m}</g>')
    if mood == "cry":
        for x in ex:
            out.append(f'<path d="M{x} 8 q-6 24 0 40 q6 -16 0 -40z" fill="#8fd3ff" stroke="{INK}" stroke-width="2.5" opacity=".95"/>')
    return "".join(out)


def blink_at(t, seed=0):
    """Natural blinking: a quick blink every ~3 s, offset by seed."""
    period = 2.6 + (seed % 5) * .37
    k = ((t + seed * .91) % period) / period
    return 1.0 if .965 < k < .995 else 0.0


# ---------------------------------------------------------------- the stickman (orange hoodie pointer)
def _seg(a, b, w, col, outline=True, ow=None):
    ow = ow or w + 10
    s = ""
    if outline:
        s += (f'<path d="M{a[0]:.1f} {a[1]:.1f} L{b[0]:.1f} {b[1]:.1f}" stroke="{INK}" stroke-width="{ow:.1f}" '
              f'stroke-linecap="round"/>')
    return s + (f'<path d="M{a[0]:.1f} {a[1]:.1f} L{b[0]:.1f} {b[1]:.1f}" stroke="{col}" stroke-width="{w:.1f}" '
                f'stroke-linecap="round"/>')


def _limb(a, b, c, w, col, ow):
    path = f'M{a[0]:.1f} {a[1]:.1f} L{b[0]:.1f} {b[1]:.1f} L{c[0]:.1f} {c[1]:.1f}'
    return (f'<path d="{path}" fill="none" stroke="{INK}" stroke-width="{ow:.1f}" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="{path}" fill="none" stroke="{col}" stroke-width="{w:.1f}" stroke-linecap="round" stroke-linejoin="round"/>')


def joints(p):
    """Forward kinematics -> dict of joint positions (canvas pixels)."""
    s = p.s
    L = dict(torso=150 * s, neck=26 * s, head=72 * s, up=88 * s, fore=82 * s, thigh=104 * s, shin=100 * s)
    hip = (p.x, p.y)
    up_ang = 180 + p.lean + p.rot
    ux, uy = d(up_ang)
    chest = (hip[0] + ux * L["torso"] * p.sy, hip[1] + uy * L["torso"] * p.sy)
    nx, ny = d(up_ang + p.neck * .4)
    neck = (chest[0] + nx * L["neck"], chest[1] + ny * L["neck"])
    hx, hy = d(up_ang + p.neck)
    head = (neck[0] + hx * L["head"] * .92, neck[1] + hy * L["head"] * .92)
    down = p.lean + p.rot
    sh = (chest[0] - ux * 14 * s, chest[1] - uy * 14 * s)
    J = dict(hip=hip, chest=chest, neck=neck, head=head, sh=sh, head_ang=up_ang + p.neck - 180)
    nx_, ny_ = -uy, ux                      # unit normal across the shoulders (points to the figure's right)
    for side, sg in (("l", -1), ("r", 1)):
        shp = (sh[0] + sg * nx_ * 44 * s * p.sx, sh[1] + sg * ny_ * 44 * s * p.sx)
        J[side + "sh"] = shp
        a1 = down + sg * getattr(p, side + "sh")
        el = (shp[0] + d(a1)[0] * L["up"], shp[1] + d(a1)[1] * L["up"])
        a2 = a1 + sg * getattr(p, side + "el")
        hd = (el[0] + d(a2)[0] * L["fore"], el[1] + d(a2)[1] * L["fore"])
        J[side + "el"], J[side + "hand"], J[side + "hand_ang"] = el, hd, a2
        b1 = down + sg * getattr(p, side + "hip")
        hip_side = (hip[0] + sg * 18 * s * math.cos(math.radians(down)), hip[1] - sg * 18 * s * math.sin(math.radians(down)))
        kn = (hip_side[0] + d(b1)[0] * L["thigh"], hip_side[1] + d(b1)[1] * L["thigh"])
        b2 = b1 - sg * getattr(p, side + "kn")
        ft = (kn[0] + d(b2)[0] * L["shin"], kn[1] + d(b2)[1] * L["shin"])
        J[side + "hipj"], J[side + "kn"], J[side + "ft"], J[side + "ft_ang"] = hip_side, kn, ft, b2
    return J


def stickman(p, t=0.0, seed=0, breathe=True, hoodie=HOODIE, hoodie_d=HOODIE_D, pants="#3a3f4b", shadow=True,
             hat=""):
    """Draw the orange-hoodie stickman at pose p (already tweened). Adds breathing + blinking."""
    if breathe:
        p = p.but(lean=p.lean + 1.2 * math.sin(t * 2.4 + seed), neck=p.neck + 1.5 * math.sin(t * 1.7 + seed),
                  sy=p.sy * (1 + .012 * math.sin(t * 2.4 + seed)))
    J = joints(p)
    s = p.s
    out = []
    if shadow:
        fy = max(J["lft"][1], J["rft"][1]) + 14 * s
        lift = clamp((fy - (p.y + 210 * s)) / -300, 0, 1) if fy < p.y + 190 * s else 0
        out.append(f'<ellipse cx="{p.x:.1f}" cy="{p.y + 214 * s:.1f}" rx="{110 * s * (1 - .5 * lift):.1f}" '
                   f'ry="{20 * s * (1 - .5 * lift):.1f}" fill="#3b4a6b" opacity="{.22 * (1 - .6 * lift):.2f}"/>')
    # legs (pants) + shoes
    for side in ("l", "r"):
        out.append(_limb(J[side + "hipj"], J[side + "kn"], J[side + "ft"], 20 * s, pants, 32 * s))
        fx, fy = J[side + "ft"]
        sg = -1 if side == "l" else 1
        ang = J[side + "ft_ang"]
        out.append(f'<g transform="translate({fx:.1f},{fy:.1f}) rotate({-ang * .25:.1f})">'
                   f'<path d="M{-14 * s * (1 if sg > 0 else 2.2):.1f} {-10 * s:.1f} q{24 * s:.1f} {-12 * s:.1f} {38 * s:.1f} 0 '
                   f'q{12 * s * sg:.1f} {14 * s:.1f} 0 {20 * s:.1f} h{-38 * s:.1f} z" fill="{INK}" '
                   f'transform="scale({sg},1) translate({-6 * s:.1f},0)"/>'
                   f'<path d="M{-4 * s:.1f} {6 * s:.1f} h{26 * s * sg:.1f}" stroke="#fff" stroke-width="{3 * s:.1f}" opacity=".5"/></g>')
    # hoodie torso: trapezoid along spine
    hx, hy = J["hip"]
    cx, cy = J["chest"]
    ax, ay = cx - hx, cy - hy
    ln = math.hypot(ax, ay) or 1
    nx, ny = -ay / ln, ax / ln
    wt, wb = 62 * s * p.sx, 54 * s * p.sx
    tl = (cx + nx * wt, cy + ny * wt); tr = (cx - nx * wt, cy - ny * wt)
    bl = (hx + nx * wb - ax / ln * 14 * s, hy + ny * wb - ay / ln * 14 * s)
    br = (hx - nx * wb - ax / ln * 14 * s, hy - ny * wb - ay / ln * 14 * s)
    body = (f'M{tl[0]:.1f} {tl[1]:.1f} Q{cx:.1f} {cy - ay / ln * 22 * s:.1f} {tr[0]:.1f} {tr[1]:.1f} '
            f'L{br[0]:.1f} {br[1]:.1f} Q{hx:.1f} {hy + 10 * s:.1f} {bl[0]:.1f} {bl[1]:.1f} Z')
    gid = f"hd{seed}"
    out.append(f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1">'
               f'<stop offset="0" stop-color="{HOODIE_L}"/><stop offset=".45" stop-color="{hoodie}"/>'
               f'<stop offset="1" stop-color="{hoodie_d}"/></linearGradient></defs>')
    out.append(f'<path d="{body}" fill="url(#{gid})" stroke="{INK}" stroke-width="{8 * s:.1f}" stroke-linejoin="round"/>')
    out.append(f'<path d="M{bl[0]:.1f} {bl[1]:.1f} Q{hx:.1f} {hy + 10 * s:.1f} {br[0]:.1f} {br[1]:.1f}" fill="none" '
               f'stroke="{hoodie_d}" stroke-width="{12 * s:.1f}" stroke-linecap="round"/>'
               f'<path d="M{bl[0]:.1f} {bl[1]:.1f} Q{hx:.1f} {hy + 10 * s:.1f} {br[0]:.1f} {br[1]:.1f}" fill="none" '
               f'stroke="{INK}" stroke-width="{3 * s:.1f}" opacity=".0"/>')
    # pocket + hem + folds
    px0, py0 = lerp(bl[0], br[0], .22), lerp(bl[1], br[1], .22)
    px1, py1 = lerp(bl[0], br[0], .78), lerp(bl[1], br[1], .78)
    up = (ax / ln * 46 * s, ay / ln * 46 * s)
    out.append(f'<path d="M{px0 + up[0] * .2:.1f} {py0 + up[1] * .2:.1f} L{px0 + up[0]:.1f} {py0 + up[1]:.1f} '
               f'L{px1 + up[0]:.1f} {py1 + up[1]:.1f} L{px1 + up[0] * .2:.1f} {py1 + up[1] * .2:.1f}" fill="none" '
               f'stroke="{hoodie_d}" stroke-width="{5 * s:.1f}" stroke-linejoin="round"/>')
    out.append(f'<path d="M{lerp(bl[0], tl[0], .55):.1f} {lerp(bl[1], tl[1], .55):.1f} q{nx * -14 * s:.1f} {12 * s:.1f} '
               f'{nx * -6 * s:.1f} {30 * s:.1f}" fill="none" stroke="{hoodie_d}" stroke-width="{4 * s:.1f}" opacity=".7"/>')
    # drawstrings
    for sg in (-1, 1):
        sx0, sy0 = cx + nx * 14 * s * sg, cy + ny * 14 * s * sg + 6 * s
        out.append(f'<path d="M{sx0:.1f} {sy0:.1f} l{-ax / ln * -40 * s + sg * 2:.1f} {40 * s:.1f}" stroke="#fff" '
                   f'stroke-width="{5 * s:.1f}" stroke-linecap="round"/><circle cx="{sx0 - ax / ln * -40 * s + sg * 2:.1f}" '
                   f'cy="{sy0 + 40 * s:.1f}" r="{5 * s:.1f}" fill="#fff" stroke="{INK}" stroke-width="{2.5 * s:.1f}"/>')
    # hood behind head
    hx2, hy2 = J["head"]
    hood = []
    out_head = []
    hood.append(f'<g transform="translate({hx2:.1f},{hy2:.1f}) rotate({-J["head_ang"]:.1f}) scale({s:.3f})">'
                    f'<path d="M-88 10 C-92 -60 -50 -96 0 -96 C50 -96 92 -60 88 10 C86 60 50 92 0 96 C-50 92 -86 60 -88 10Z" '
                    f'fill="{hoodie}" stroke="{INK}" stroke-width="9"/>'
                    f'<path d="M-70 40 C-50 86 50 86 70 40" fill="none" stroke="{hoodie_d}" stroke-width="10" stroke-linecap="round"/>'
                    f'<path d="M-60 -70 C-30 -88 20 -90 50 -76" fill="none" stroke="{HOODIE_L}" stroke-width="8" stroke-linecap="round" opacity=".8"/></g>')
    # head
    ha = J["head_ang"]
    blink = blink_at(t, seed)
    out_head.append(f'<g transform="translate({hx2:.1f},{hy2:.1f}) rotate({-ha:.1f}) scale({s * p.sx:.3f},{s * (2 - p.sx):.3f})">'
                    f'<circle r="70" fill="{SKIN}" stroke="{INK}" stroke-width="9"/>'
                    f'<path d="M-50 -46 q20 -26 52 -24" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round" opacity=".0"/>'
                    f'<path d="M30 -58 q22 12 30 34" fill="none" stroke="#e6ecf2" stroke-width="10" stroke-linecap="round"/>'
                    f'{face(p.mood, p.look, p.turn, blink, p.blush)}{hat}</g>')
    if p.sweat:
        out_head.append(f'<path transform="translate({hx2 + 70 * s:.1f},{hy2 - 40 * s:.1f}) scale({s:.2f})" '
                        f'd="M0 -22 q16 22 0 32 q-16 -10 0 -32z" fill="#9fdcff" stroke="{INK}" stroke-width="4"/>')
    # arms (sleeves) + hands — drawn after torso, before head so hands near face stay visible -> draw after head
    arms = {"l": [], "r": []}
    for side in ("l", "r"):
        arms[side].append(_limb(J[side + "sh"], J[side + "el"], J[side + "hand"], 26 * s, hoodie, 38 * s))
        # cuff
        ex_, ey_ = J[side + "el"]
        hx3, hy3 = J[side + "hand"]
        cxk, cyk = lerp(ex_, hx3, .8), lerp(ey_, hy3, .8)
        arms[side].append(f'<circle cx="{cxk:.1f}" cy="{cyk:.1f}" r="{14 * s:.1f}" fill="{hoodie_d}"/>')
        held = getattr(p, "hand_" + side)
        if held:
            arms[side].append(f'<g transform="translate({hx3:.1f},{hy3:.1f}) rotate({-J[side + "hand_ang"] + 180:.1f}) scale({s:.2f})">{held}</g>')
        arms[side].append(f'<circle cx="{hx3:.1f}" cy="{hy3:.1f}" r="{17 * s:.1f}" fill="{SKIN}" stroke="{INK}" stroke-width="{7 * s:.1f}"/>')
    front = getattr(p, "front", "")           # 'l', 'r' or 'lr': that hand is drawn over the face
    out += hood + [x for sd in "lr" if sd not in front for x in arms[sd]] + out_head + \
        [x for sd in "lr" if sd in front for x in arms[sd]]
    return f'<g>{"".join(out)}</g>'


def actor(track, t, **kw):
    """Draw a stickman from a key-frame track at time t."""
    return stickman(pose_at(track, t), t, **kw)


# ---------------------------------------------------------------- the tooth mascot หมอฟันยิ้ม + germs
TOOTH = ("M20 40 C 20 -10, 110 -10, 130 20 C 150 -10, 240 -10, 240 40 C 240 120, 215 160, 205 250 "
         "C 198 300, 160 300, 152 250 C 145 200, 115 200, 108 250 C 100 300, 62 300, 55 250 "
         "C 45 160, 20 120, 20 40 Z")


def mascot(x, y, t=0.0, s=1.0, mood="happy", wave=0.0, bob=True, sparkle_on=True, la=-40, ra=40, look=(0, 0)):
    """Tooth doctor mascot (the clinic). wave: 0..1 waving strength. la/ra: arm angles."""
    by = (10 * math.sin(t * 3.2)) if bob else 0
    sq = 1 + .03 * math.sin(t * 6.4) if bob else 1
    ra_ = ra + wave * (60 + 35 * math.sin(t * 12))
    def arm(ang, side):
        sx0 = 30 if side < 0 else 230
        ex, ey = sx0 + side * 60 * math.cos(math.radians(ang)), 140 - 60 * math.sin(math.radians(ang)) * -1
        ex = sx0 + side * 62 * math.cos(math.radians(ang))
        ey = 140 + 62 * math.sin(math.radians(-ang))
        return (f'<path d="M{sx0} 140 Q{(sx0 + ex) / 2 + side * 6:.1f} {(140 + ey) / 2 + 10:.1f} {ex:.1f} {ey:.1f}" fill="none" '
                f'stroke="{INK}" stroke-width="12" stroke-linecap="round"/>'
                f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="16" fill="#fff" stroke="{INK}" stroke-width="7"/>')
    sp = ""
    if sparkle_on:
        for i, (sx_, sy_) in enumerate(((-40, -10), (290, 40), (260, -40))):
            k = .6 + .4 * math.sin(t * 4 + i * 2)
            sp += sparkle(sx_, sy_, 20 * k, "#ffd84a")
    return f'''<g transform="translate({x},{y + by:.1f}) scale({s * (2 - sq):.3f},{s * sq:.3f}) translate(-130,-150)">
 <ellipse cx="130" cy="318" rx="110" ry="18" fill="#3b4a6b" opacity=".18"/>
 {arm(la, -1)}{arm(ra_, 1)}
 <defs><radialGradient id="tg" cx=".35" cy=".25" r=".9"><stop offset="0" stop-color="#ffffff"/><stop offset=".7" stop-color="#f4f8ff"/>
 <stop offset="1" stop-color="#cfdcef"/></radialGradient></defs>
 <path d="{TOOTH}" fill="url(#tg)" stroke="{INK}" stroke-width="9" stroke-linejoin="round"/>
 <path d="M48 40 q4 -30 40 -34" fill="none" stroke="#fff" stroke-width="12" stroke-linecap="round"/>
 <path d="M40 150 q90 40 180 0 l-6 34 q-84 36 -168 0 z" fill="{TEAL}" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>
 <path d="M60 18 q70 -40 140 0" fill="none" stroke="#9aa5ab" stroke-width="10"/>
 <circle cx="130" cy="6" r="26" fill="#dff6ff" stroke="{INK}" stroke-width="6"/><circle cx="130" cy="6" r="10" fill="#fff" stroke="#9aa5ab" stroke-width="4"/>
 <g transform="translate(130,92) scale(.9)">{face(mood, look, 0, blink_at(t, 3))}</g>
 {sp}
</g>'''


def germ(x, y, t=0.0, s=1.0, color="#9b6bd6", mood="smug", seed=0, hat=""):
    """Cute germ villain: wobbly blob that bounces."""
    b = math.sin(t * 7 + seed)
    pts = []
    for i in range(10):
        a = i / 10 * 2 * math.pi
        r = 44 + 5 * math.sin(a * 3 + t * 5 + seed)
        pts.append((r * math.cos(a), r * math.sin(a)))
    path = "M" + " ".join(f"{px:.1f} {py:.1f}" for px, py in pts[:1])
    for i in range(10):
        p0, p1 = pts[i], pts[(i + 1) % 10]
        mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
        path += f" Q{p0[0] * 1.08:.1f} {p0[1] * 1.08:.1f} {mx:.1f} {my:.1f}"
    path += " Z"
    spikes = "".join(f'<circle cx="{58 * math.cos(a):.1f}" cy="{58 * math.sin(a):.1f}" r="6" fill="{color}" stroke="{INK}" stroke-width="3"/>'
                     for a in [k * math.pi / 4 + .3 for k in range(8)])
    return (f'<g transform="translate({x},{y - 18 * abs(b):.1f}) scale({s * (1 + .05 * b):.3f},{s * (1 - .05 * b):.3f})">'
            f'<ellipse cx="0" cy="64" rx="40" ry="8" fill="#3b4a6b" opacity=".18"/>{spikes}'
            f'<path d="{path}" fill="{color}" stroke="{INK}" stroke-width="6"/>'
            f'<ellipse cx="-16" cy="-22" rx="10" ry="6" fill="#fff" opacity=".45"/>'
            f'<g transform="scale(.62)">{face(mood, (0, 0), 0, blink_at(t, seed + 7), False)}</g>{hat}</g>')


# ---------------------------------------------------------------- props & effects
def sparkle(x, y, r=18, col="#ffd84a"):
    return (f'<path transform="translate({x:.1f},{y:.1f})" d="M0 {-r:.1f} Q{r * .18:.1f} {-r * .18:.1f} {r:.1f} 0 '
            f'Q{r * .18:.1f} {r * .18:.1f} 0 {r:.1f} Q{-r * .18:.1f} {r * .18:.1f} {-r:.1f} 0 Q{-r * .18:.1f} {-r * .18:.1f} 0 {-r:.1f}Z" '
            f'fill="{col}" stroke="{INK}" stroke-width="3"/>')


def motion_lines(x, y, n=3, length=80, ang=0, col=INK):
    out = []
    for i in range(n):
        dx, dy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        oy = (i - (n - 1) / 2) * 26
        out.append(f'<path d="M{x - dy * oy:.1f} {y + dx * oy:.1f} l{-dx * length:.1f} {-dy * length:.1f}" stroke="{col}" '
                   f'stroke-width="7" stroke-linecap="round" opacity=".55"/>')
    return "".join(out)


def ambient(t, kind="pollen", n=26, seed=1, area=(0, 200, 1080, 1600)):
    """Ghibli-style living air: 'pollen' (floating light motes), 'fireflies', 'petals', 'bubbles', 'leaves'."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = area
    out = []
    for i in range(n):
        bx, by = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        sp, ph, r = rnd.uniform(.4, 1.2), rnd.uniform(0, 6.3), rnd.uniform(3, 8)
        if kind in ("pollen", "fireflies"):
            x = bx + 40 * math.sin(t * sp + ph)
            y = by - (t * 30 * sp) % 260 + 30 * math.cos(t * sp * 1.3 + ph)
            a = .35 + .45 * (0.5 + 0.5 * math.sin(t * 3 * sp + ph))
            col = "#fff7c2" if kind == "pollen" else "#d9ff7a"
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 2.6:.1f}" fill="{col}" opacity="{a * .25:.2f}"/>'
                       f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * .8:.1f}" fill="{col}" opacity="{a:.2f}"/>')
        elif kind == "bubbles":
            y = by - (t * 120 * sp + ph * 80) % (y1 - y0)
            x = bx + 18 * math.sin(t * 2 * sp + ph)
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 2.2:.1f}" fill="#ffffff" fill-opacity=".25" stroke="#ffffff" '
                       f'stroke-width="3" opacity=".8"/><circle cx="{x - r * .7:.1f}" cy="{y - r * .7:.1f}" r="{r * .5:.1f}" fill="#fff"/>')
        else:  # petals / leaves drifting on the wind
            k = (t * .18 * sp + ph / 6.3) % 1
            x = x0 - 80 + (x1 - x0 + 160) * k
            y = by + 60 * math.sin(k * 9 + ph)
            col = rnd.choice(("#ffc4d6", "#ffe0ea", "#fff")) if kind == "petals" else rnd.choice(("#8cc152", "#b5d96b", "#5f9e3f"))
            out.append(f'<ellipse transform="translate({x:.1f},{y:.1f}) rotate({k * 720 + ph * 50:.0f})" rx="{r * 1.8:.1f}" '
                       f'ry="{r * .9:.1f}" fill="{col}" stroke="{INK}" stroke-width="1.5" opacity=".9"/>')
    return "".join(out)


def drifting_clouds(t, y=420, speed=14):
    """A couple of clouds sliding slowly across the sky (adds life to static outdoor backgrounds)."""
    return cloud(-200 + (t * speed + 300) % 1500, y, .55, "#fff", "#d6e2f2") + cloud(1300 - (t * speed * .6 + 200) % 1600, y + 330, .4)


def pop_text(x, y, text, t, t0, size=96, col="#fff", stroke=INK, rot=-6):
    """Comic word that pops in at t0 with overshoot (e.g. 'แย่แล้ว!')."""
    k = ease((t - t0) / .35, "back") if t >= t0 else 0
    if k <= 0:
        return ""
    return (f'<g transform="translate({x},{y}) rotate({rot}) scale({k:.3f})"><text text-anchor="middle" '
            f'font-family="K" font-weight="700" font-size="{size}" fill="{col}" stroke="{stroke}" stroke-width="16" '
            f'paint-order="stroke" stroke-linejoin="round">{text}</text></g>')


def speech_bubble(x, y, text, t, t0=0.0, w=360, h=140, tail=(-60, 110), size=54):
    """Comic speech bubble centred at (x,y) that pops in at t0; tail = offset of the tail tip from the centre."""
    k = ease((t - t0) / .3, "back") if t >= t0 else 0
    if k <= 0:
        return ""
    tx, ty = tail
    bx = max(-w / 2 + 40, min(w / 2 - 40, tx * .4))
    return (f'<g transform="translate({x},{y}) scale({k:.3f})">'
            f'<path d="M{bx - 26:.0f} {h / 2 - 6:.0f} L{tx:.0f} {ty:.0f} L{bx + 26:.0f} {h / 2 - 6:.0f}Z" fill="#fffdf6" '
            f'stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>'
            f'<rect x="{-w / 2:.0f}" y="{-h / 2:.0f}" width="{w}" height="{h}" rx="{h / 2.4:.0f}" fill="#fffdf6" stroke="{INK}" stroke-width="7"/>'
            f'<path d="M{bx - 22:.0f} {h / 2 - 4:.0f} H{bx + 22:.0f}" stroke="#fffdf6" stroke-width="9"/>'
            f'<text y="{size * .36:.0f}" text-anchor="middle" font-family="K" font-weight="600" font-size="{size}" fill="{INK}">{text}</text></g>')


def toothbrush(col="#5fc3c8"):
    """Drawn pointing 'up' from the hand (hand_r=toothbrush())."""
    return (f'<rect x="-8" y="-150" width="16" height="140" rx="8" fill="{col}" stroke="{INK}" stroke-width="5"/>'
            f'<rect x="-14" y="-190" width="28" height="46" rx="6" fill="#fff" stroke="{INK}" stroke-width="5"/>'
            f'<path d="M-10 -186 v38 M-3 -186 v38 M4 -186 v38 M11 -186 v38" stroke="#bfe9ff" stroke-width="3"/>')


def candy(col="#ff6fa8"):
    return (f'<g transform="translate(0,-40)"><path d="M-46 -16 l20 16 l-20 16z M46 -16 l-20 16 l20 16z" fill="{col}" '
            f'stroke="{INK}" stroke-width="5" stroke-linejoin="round"/><circle r="26" fill="{col}" stroke="{INK}" stroke-width="6"/>'
            f'<path d="M-14 -16 q14 16 0 32 M2 -20 q14 18 0 38" fill="none" stroke="#fff" stroke-width="5" opacity=".7"/></g>')


def tooth_icon(x, y, s=1.0, mood="happy", decay=0.0, t=0.0, crown=False):
    """Simple tooth character (patient's tooth) with optional decay spot 0..1."""
    spot = ""
    if decay > 0:
        r = 20 + 46 * decay
        spot = (f'<path d="M{150 - r * .2:.1f} {60 - r * .4:.1f} q{r:.1f} {-r * .2:.1f} {r * 1.1:.1f} {r * .6:.1f} '
                f'q{-r * .1:.1f} {r:.1f} {-r * .9:.1f} {r * .8:.1f} q{-r * .6:.1f} {-r * .5:.1f} {-r * .2:.1f} {-r * 1.4:.1f}z" '
                f'fill="#5b4334" stroke="{INK}" stroke-width="5"/>')
    cr = (f'<path d="M14 54 C 14 -18, 112 -16, 130 14 C 150 -16, 246 -18, 246 54 Q130 92 14 54Z" fill="#ffd34d" '
          f'stroke="{INK}" stroke-width="8" stroke-linejoin="round"/><path d="M40 30 q30 -20 60 -12" stroke="#fff6c2" '
          f'stroke-width="10" fill="none" stroke-linecap="round"/>' if crown else "")
    return (f'<g transform="translate({x},{y}) scale({s}) translate(-130,-150)">'
            f'<ellipse cx="130" cy="318" rx="100" ry="16" fill="#3b4a6b" opacity=".18"/>'
            f'<path d="{TOOTH}" fill="#fffdf7" stroke="{INK}" stroke-width="9" stroke-linejoin="round"/>{spot}{cr}'
            f'<g transform="translate(130,118) scale(.85)">{face(mood, (0, 0), 0, blink_at(t, 5))}</g></g>')


# ---------------------------------------------------------------- Ghibli-style painted backgrounds (static)
def _defs():
    return f'''<defs>
 <filter id="paper" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="3" seed="4"/>
  <feColorMatrix values="0 0 0 0 .55  0 0 0 0 .48  0 0 0 0 .40  0 0 0 .10 0"/></filter>
 <filter id="wash" x="-10%" y="-10%" width="120%" height="120%"><feTurbulence type="fractalNoise" baseFrequency=".012" numOctaves="3" seed="7" result="n"/>
  <feDisplacementMap in="SourceGraphic" in2="n" scale="28"/></filter>
 <filter id="soft"><feGaussianBlur stdDeviation="6"/></filter>
 <filter id="softer"><feGaussianBlur stdDeviation="22"/></filter>
 <filter id="cloud" x="-20%" y="-20%" width="140%" height="140%"><feTurbulence type="fractalNoise" baseFrequency=".02" numOctaves="4" seed="11" result="n"/>
  <feDisplacementMap in="SourceGraphic" in2="n" scale="38" result="d"/><feGaussianBlur in="d" stdDeviation="2.2"/></filter>
 <linearGradient id="skyday" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3f8fd0"/><stop offset=".45" stop-color="#8ccbee"/>
  <stop offset=".8" stop-color="#d9f0f7"/><stop offset="1" stop-color="#fbeccb"/></linearGradient>
 <linearGradient id="skynight" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0f1d48"/><stop offset=".55" stop-color="#2c4a8a"/>
  <stop offset="1" stop-color="#6d7fb8"/></linearGradient>
 <linearGradient id="skysunset" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4a5fa8"/><stop offset=".45" stop-color="#e7a0a8"/>
  <stop offset=".8" stop-color="#ffd2a1"/><stop offset="1" stop-color="#fff0c9"/></linearGradient>
 <linearGradient id="hillfar" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8fb7c9"/><stop offset="1" stop-color="#b9d4dc"/></linearGradient>
 <linearGradient id="hillmid" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9ccc65"/><stop offset="1" stop-color="#5d9b45"/></linearGradient>
 <linearGradient id="hillnear" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7cb342"/><stop offset="1" stop-color="#3f7d3a"/></linearGradient>
 <linearGradient id="wood" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#c98f5a"/><stop offset="1" stop-color="#9c6638"/></linearGradient>
 <linearGradient id="wallwarm" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff4dc"/><stop offset="1" stop-color="#f3dcb5"/></linearGradient>
 <linearGradient id="wallmint" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#eefaf6"/><stop offset="1" stop-color="#cdeee6"/></linearGradient>
 <radialGradient id="sunglow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#fffbe0" stop-opacity=".95"/>
  <stop offset=".4" stop-color="#fff2b8" stop-opacity=".45"/><stop offset="1" stop-color="#fff2b8" stop-opacity="0"/></radialGradient>
 <linearGradient id="beam" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff6cc" stop-opacity=".55"/>
  <stop offset="1" stop-color="#fff6cc" stop-opacity="0"/></linearGradient>
 <radialGradient id="gum" cx=".5" cy=".3" r=".8"><stop offset="0" stop-color="#ffb3b8"/><stop offset="1" stop-color="#e2717f"/></radialGradient>
 <radialGradient id="mouthdark" cx=".5" cy=".55" r=".6"><stop offset="0" stop-color="#8a2a3f"/><stop offset="1" stop-color="#3d0b19"/></radialGradient>
 <radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".6" stop-color="#2b1d10" stop-opacity="0"/>
  <stop offset="1" stop-color="#2b1d10" stop-opacity=".35"/></radialGradient>
</defs>'''


def cloud(x, y, s=1.0, tint="#ffffff", shade="#c7d8ee"):
    """Big Ghibli cumulus: stacked puffs, shaded underside, soft edges."""
    rnd = random.Random(int(x * 7 + y * 13))
    puffs = [(0, 0, 120), (-130, 40, 90), (130, 40, 100), (-60, -60, 95), (70, -70, 110), (220, 70, 70), (-220, 75, 65),
             (0, -130, 80)]
    base = "".join(f'<circle cx="{px + rnd.uniform(-10, 10):.0f}" cy="{py:.0f}" r="{r:.0f}"/>' for px, py, r in puffs)
    return (f'<g transform="translate({x},{y}) scale({s})" filter="url(#cloud)">'
            f'<g fill="{shade}">{base}</g><g fill="{tint}" transform="translate(-10,-22) scale(.96)">{base}</g>'
            f'<ellipse cx="0" cy="96" rx="260" ry="34" fill="{shade}" opacity=".9"/></g>')


def ghibli_tree(x, y, s=1.0, leaf=("#3f7d3a", "#5f9e3f", "#8cc152", "#b5d96b")):
    rnd = random.Random(int(x + y))
    trunk = (f'<path d="M-26 0 C-20 -120 -40 -220 -10 -320 L10 -320 C30 -220 22 -120 30 0Z" fill="#7a5134" stroke="{INK}" stroke-width="6"/>'
             f'<path d="M-8 -200 C-60 -250 -90 -260 -120 -300 M6 -240 C50 -280 90 -290 120 -330" fill="none" stroke="#7a5134" stroke-width="16" stroke-linecap="round"/>')
    blobs = []
    for layer, col in enumerate(leaf):
        for _ in range(9):
            bx, by = rnd.uniform(-190, 190), rnd.uniform(-520, -260) - layer * 6
            r = rnd.uniform(70, 110) - layer * 12
            blobs.append(f'<circle cx="{bx + layer * 8:.0f}" cy="{by - layer * 14:.0f}" r="{r:.0f}" fill="{col}"/>')
    return (f'<g transform="translate({x},{y}) scale({s})"><ellipse cx="0" cy="6" rx="170" ry="26" fill="#2f5f2c" opacity=".35"/>'
            f'{trunk}<g filter="url(#wash)">{"".join(blobs)}</g></g>')


def grass_tufts(y0, y1, n=120, seed=1, cols=("#4f8f3a", "#6aa84f", "#8cc152")):
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        x, y = rnd.uniform(0, W), rnd.uniform(y0, y1)
        h = rnd.uniform(14, 34) * (0.6 + (y - y0) / max(1, y1 - y0))
        c = rnd.choice(cols)
        out.append(f'<path d="M{x:.0f} {y:.0f} q-4 {-h * .6:.0f} -9 {-h:.0f} M{x:.0f} {y:.0f} q2 {-h * .7:.0f} 3 {-h * 1.15:.0f} '
                   f'M{x:.0f} {y:.0f} q6 {-h * .5:.0f} 12 {-h * .9:.0f}" stroke="{c}" stroke-width="3.5" fill="none" stroke-linecap="round"/>')
    return "".join(out)


def flowers(y0, y1, n=40, seed=3):
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        x, y = rnd.uniform(0, W), rnd.uniform(y0, y1)
        c = rnd.choice(("#fff6f0", "#ffd84a", "#ffb3c7", "#c9b6ff"))
        r = rnd.uniform(5, 9)
        out.append(f'<g transform="translate({x:.0f},{y:.0f})">' + "".join(
            f'<circle cx="{r * math.cos(a):.1f}" cy="{r * math.sin(a):.1f}" r="{r * .7:.1f}" fill="{c}"/>'
            for a in [k * 2 * math.pi / 5 for k in range(5)]) + f'<circle r="{r * .5:.1f}" fill="#ffb02e"/></g>')
    return "".join(out)


def _paper_overlay():
    return f'<rect width="{W}" height="{H}" filter="url(#paper)"/><rect width="{W}" height="{H}" fill="url(#vig)"/>'


def bg_meadow(ground=1420, sky="skyday", tree=True, path=True):
    """Rolling hills under a summer sky: the default outdoor scene."""
    return f'''{_defs()}<rect width="{W}" height="{H}" fill="url(#{sky})"/>
<circle cx="820" cy="360" r="300" fill="url(#sunglow)"/>
{cloud(260, 360, 1.15)}{cloud(860, 640, .8)}{cloud(120, 900, .55, "#fff", "#d6e2f2")}
<path d="M0 {ground - 330} C 180 {ground - 430} 360 {ground - 400} 520 {ground - 330} S 860 {ground - 420} 1080 {ground - 360} V{H} H0Z" fill="url(#hillfar)" filter="url(#wash)"/>
<path d="M0 {ground - 180} C 240 {ground - 300} 520 {ground - 250} 700 {ground - 190} S 980 {ground - 240} 1080 {ground - 220} V{H} H0Z" fill="url(#hillmid)" filter="url(#wash)"/>
<path d="M-40 {ground - 60} C 200 {ground - 120} 520 {ground - 80} 760 {ground - 50} S 1040 {ground - 70} 1120 {ground - 60} V{H} H-40Z" fill="url(#hillnear)"/>
{ghibli_tree(880, ground - 40, .9) if tree else ""}
{f'<path d="M420 {H} C 470 {ground + 200} 560 {ground + 40} 640 {ground - 50} L700 {ground - 50} C 660 {ground + 60} 700 {ground + 220} 820 {H}Z" fill="#e7cf9b" opacity=".9" filter="url(#wash)"/>' if path else ""}
{grass_tufts(ground - 70, H, 260, 2)}{flowers(ground - 40, H - 120, 46, 4)}
{_paper_overlay()}'''


def bg_night(ground=1440):
    rnd = random.Random(9)
    stars = "".join(f'<circle cx="{rnd.uniform(0, W):.0f}" cy="{rnd.uniform(0, 1100):.0f}" r="{rnd.uniform(1.2, 3.4):.1f}" '
                    f'fill="#fff" opacity="{rnd.uniform(.4, 1):.2f}"/>' for _ in range(140))
    return f'''{_defs()}<rect width="{W}" height="{H}" fill="url(#skynight)"/>{stars}
<circle cx="800" cy="380" r="210" fill="#fff8d6" opacity=".18" filter="url(#softer)"/><circle cx="800" cy="380" r="86" fill="#fff6cf"/>
<circle cx="770" cy="360" r="14" fill="#efe4b5"/><circle cx="828" cy="404" r="10" fill="#efe4b5"/>
{cloud(200, 700, .7, "#9aa9d6", "#6f7fb3")}
<path d="M0 {ground - 220} C 240 {ground - 330} 560 {ground - 260} 760 {ground - 210} S 1000 {ground - 260} 1080 {ground - 240} V{H} H0Z" fill="#30507a" filter="url(#wash)"/>
<path d="M-40 {ground - 60} C 240 {ground - 120} 600 {ground - 70} 1120 {ground - 70} V{H} H-40Z" fill="#284766"/>
<g transform="translate(130,{ground - 40})"><rect x="0" y="-260" width="300" height="260" fill="#f0d9a8" stroke="{INK}" stroke-width="7"/>
<path d="M-30 -250 L150 -380 L330 -250Z" fill="#a3473b" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>
<rect x="40" y="-200" width="90" height="80" fill="#ffd56b" stroke="{INK}" stroke-width="6"/><rect x="180" y="-140" width="70" height="140" fill="#7a5134" stroke="{INK}" stroke-width="6"/>
<circle cx="85" cy="-160" r="120" fill="#ffd56b" opacity=".18" filter="url(#softer)"/></g>
{grass_tufts(ground - 60, H, 200, 5, ("#1f3d55", "#2c5470", "#3a6a85"))}
{_paper_overlay()}'''


def bg_room(window=True, floor=1460):
    """Cosy Ghibli bedroom/living room with afternoon light beams."""
    return f'''{_defs()}<rect width="{W}" height="{floor}" fill="url(#wallwarm)"/>
<rect y="{floor}" width="{W}" height="{H - floor}" fill="url(#wood)"/>
{"".join(f'<path d="M0 {floor + 40 + i * 70} H{W}" stroke="#8a5a32" stroke-width="3" opacity=".45"/>' for i in range(7))}
<rect y="{floor - 26}" width="{W}" height="30" fill="#a8744a" stroke="{INK}" stroke-width="5"/>
{f"""<g transform="translate(560,300)"><rect width="420" height="520" rx="10" fill="url(#skyday)" stroke="{INK}" stroke-width="10"/>
{cloud(120, 160, .35)}{cloud(320, 330, .25)}
<path d="M0 420 C 120 360 280 400 420 370 V520 H0Z" fill="#8cc152"/><path d="M0 470 C 160 440 300 470 420 450 V520 H0Z" fill="#5f9e3f"/>
<path d="M210 0 V520 M0 260 H420" stroke="{INK}" stroke-width="8"/>
<path d="M-50 -20 h520" stroke="#a8744a" stroke-width="16" stroke-linecap="round"/>
<path d="M-40 -14 q60 300 10 560 l-40 0 q30 -300 -10 -560z" fill="#e98a6d" stroke="{INK}" stroke-width="6"/>
<path d="M460 -14 q-60 300 -10 560 l40 0 q-30 -300 10 -560z" fill="#e98a6d" stroke="{INK}" stroke-width="6"/></g>
<path d="M560 300 L980 300 L620 {floor + 200} L120 {floor + 200}Z" fill="url(#beam)" opacity=".75"/>""" if window else ""}
<g transform="translate(80,{floor - 26})"><rect x="0" y="-360" width="330" height="360" fill="#b98757" stroke="{INK}" stroke-width="7"/>
<path d="M0 -240 h330 M0 -120 h330" stroke="{INK}" stroke-width="6"/>
<rect x="20" y="-350" width="34" height="100" fill="#6fb3d2" stroke="{INK}" stroke-width="4"/><rect x="58" y="-340" width="30" height="90" fill="#e98a6d" stroke="{INK}" stroke-width="4"/>
<rect x="92" y="-356" width="38" height="106" fill="#ffd56b" stroke="{INK}" stroke-width="4"/><circle cx="250" cy="-290" r="34" fill="#8cc152" stroke="{INK}" stroke-width="4"/>
<path d="M230 -250 h40 l-6 -20 h-28z" fill="#d9774f" stroke="{INK}" stroke-width="4"/>
<rect x="30" y="-220" width="120" height="90" rx="8" fill="#f6efe0" stroke="{INK}" stroke-width="4"/><circle cx="240" cy="-170" r="36" fill="#fff" stroke="{INK}" stroke-width="5"/>
<path d="M240 -170 v-22 M240 -170 l16 10" stroke="{INK}" stroke-width="4"/></g>
<g transform="translate(980,{floor - 20})"><path d="M-50 0 h100 l-14 -90 h-72z" fill="#d9774f" stroke="{INK}" stroke-width="6"/>
<g filter="url(#wash)"><circle cx="-30" cy="-140" r="60" fill="#5f9e3f"/><circle cx="30" cy="-170" r="64" fill="#77b255"/><circle cx="0" cy="-230" r="50" fill="#8cc152"/></g></g>
{_paper_overlay()}'''


def bg_bathroom(floor=1500):
    tiles = "".join(f'<path d="M0 {y} H{W}" stroke="#bfe3db" stroke-width="4"/>' for y in range(0, floor, 90))
    tiles += "".join(f'<path d="M{x} 0 V{floor}" stroke="#bfe3db" stroke-width="4"/>' for x in range(0, W, 90))
    return f'''{_defs()}<rect width="{W}" height="{floor}" fill="url(#wallmint)"/>{tiles}
<rect y="{floor}" width="{W}" height="{H - floor}" fill="#cfe7ef"/>
{"".join(f'<path d="M{x} {floor} l-60 {H - floor}" stroke="#aac9d4" stroke-width="4"/>' for x in range(0, W + 200, 140))}
<g transform="translate(300,420)"><rect width="480" height="560" rx="230" fill="#e9f8ff" stroke="{INK}" stroke-width="10"/>
<rect x="24" y="24" width="432" height="512" rx="210" fill="#d4eef7"/>
<path d="M90 140 l120 -80 M110 230 l200 -140" stroke="#fff" stroke-width="18" stroke-linecap="round" opacity=".8"/></g>
<g transform="translate(540,1180)"><path d="M-300 0 h600 q-10 150 -200 170 h-200 q-190 -20 -200 -170z" fill="#fbfdff" stroke="{INK}" stroke-width="9"/>
<rect x="-30" y="170" width="60" height="{floor - 1180 - 170}" fill="#fbfdff" stroke="{INK}" stroke-width="8"/>
<path d="M-20 -60 v-50 h80" fill="none" stroke="#9aa5ab" stroke-width="20" stroke-linecap="round"/>
<g transform="translate(200,-20)"><rect x="-40" y="-90" width="80" height="90" rx="12" fill="#ffd56b" stroke="{INK}" stroke-width="6"/>
<rect x="-24" y="-200" width="12" height="130" rx="6" fill="#5fc3c8" stroke="{INK}" stroke-width="4" transform="rotate(-12)"/>
<rect x="8" y="-190" width="12" height="120" rx="6" fill="#ff8aa0" stroke="{INK}" stroke-width="4" transform="rotate(10)"/></g>
<g transform="translate(-220,-20)"><rect x="-26" y="-130" width="52" height="130" rx="10" fill="#ffffff" stroke="{INK}" stroke-width="6"/>
<rect x="-26" y="-90" width="52" height="40" fill="#5fc3c8"/><rect x="-12" y="-160" width="24" height="30" fill="#e98a6d" stroke="{INK}" stroke-width="5"/></g></g>
<g transform="translate(940,300)"><rect x="-90" y="0" width="180" height="250" rx="10" fill="url(#skyday)" stroke="{INK}" stroke-width="8"/>
<path d="M0 0 V250 M-90 125 H90" stroke="{INK}" stroke-width="6"/></g>
<path d="M850 300 L1030 300 L760 {floor} L300 {floor}Z" fill="url(#beam)" opacity=".6"/>
<g transform="translate(110,{floor - 10})"><path d="M-40 0 h80 l-10 -70 h-60z" fill="#e98a6d" stroke="{INK}" stroke-width="5"/>
<g filter="url(#wash)"><path d="M0 -70 q-60 -80 -20 -170 q20 80 20 170 q10 -110 60 -150 q-10 100 -60 150z" fill="#5f9e3f"/></g></g>
{_paper_overlay()}'''


def bg_clinic(floor=1480):
    return f'''{_defs()}<rect width="{W}" height="{floor}" fill="url(#wallmint)"/>
<rect y="{floor}" width="{W}" height="{H - floor}" fill="#dfeee9"/>
{"".join(f'<path d="M0 {floor + 50 + i * 80} H{W}" stroke="#c4ddd6" stroke-width="4"/>' for i in range(6))}
<rect y="{floor - 300}" width="{W}" height="300" fill="#bfe6df" opacity=".6"/>
<path d="M0 {floor - 300} H{W}" stroke="{TEAL}" stroke-width="10"/>
<g transform="translate(90,300)"><rect width="400" height="480" rx="12" fill="url(#skyday)" stroke="{INK}" stroke-width="10"/>
{cloud(120, 130, .3)}{ghibli_tree(300, 470, .45)}
<path d="M0 400 C 120 360 280 390 400 370 V480 H0Z" fill="#8cc152"/>
<path d="M200 0 V480 M0 240 H400" stroke="{INK}" stroke-width="8"/></g>
<path d="M90 300 L490 300 L860 {floor + 200} L260 {floor + 200}Z" fill="url(#beam)" opacity=".55"/>
<g transform="translate(700,330)"><rect x="-150" y="0" width="300" height="200" rx="16" fill="#fff" stroke="{INK}" stroke-width="8"/>
<text x="0" y="70" text-anchor="middle" font-family="K" font-weight="700" font-size="46" fill="{TEAL_D}">คลินิกทันตกรรม</text>
<text x="0" y="140" text-anchor="middle" font-family="K" font-weight="700" font-size="52" fill="{HOODIE}">บางปะอิน</text>
<path d="M-60 165 h120" stroke="{TEAL}" stroke-width="8" stroke-linecap="round"/></g>
<g transform="translate(980,{floor - 30}) scale(.7)">
<path d="M-260 0 h300 l40 -120 h-300z" fill="{TEAL}" stroke="{INK}" stroke-width="8" stroke-linejoin="round"/>
<path d="M40 -120 l120 -200 l50 20 l-110 190z" fill="{TEAL}" stroke="{INK}" stroke-width="8" stroke-linejoin="round"/>
<rect x="-160" y="0" width="60" height="{H - floor - 60}" fill="#9aa5ab" stroke="{INK}" stroke-width="6"/>
<path d="M-80 -300 q120 -160 260 -140" fill="none" stroke="#9aa5ab" stroke-width="14"/>
<ellipse cx="190" cy="-440" rx="70" ry="34" fill="#fff6c9" stroke="{INK}" stroke-width="7"/>
<circle cx="190" cy="-430" r="160" fill="#fff6c9" opacity=".25" filter="url(#softer)"/></g>
<g transform="translate(980,{floor - 10})"><path d="M-44 0 h88 l-10 -80 h-68z" fill="#e98a6d" stroke="{INK}" stroke-width="5"/>
<g filter="url(#wash)"><circle cx="-24" cy="-130" r="54" fill="#5f9e3f"/><circle cx="26" cy="-156" r="56" fill="#77b255"/></g></g>
{_paper_overlay()}'''


def bg_mouth():
    """Giant friendly close-up of teeth & gums (for scenes inside the mouth)."""
    upper = "".join(f'<path transform="translate({x},{300 + abs(x - 540) * .25:.0f}) scale(.9,1) rotate(180) translate(-130,-280)" '
                    f'd="{TOOTH}" fill="#fffdf6" stroke="{INK}" stroke-width="8" stroke-linejoin="round"/>' for x in range(150, 1000, 195))
    lower = "".join(f'<path transform="translate({x},{1500 - abs(x - 540) * .25:.0f}) scale(.9,1) translate(-130,-60)" '
                    f'd="{TOOTH}" fill="#fffdf6" stroke="{INK}" stroke-width="8" stroke-linejoin="round"/>' for x in range(150, 1000, 195))
    return f'''{_defs()}<rect width="{W}" height="{H}" fill="url(#mouthdark)"/>
<path d="M-40 -40 H1120 V420 Q540 260 -40 420Z" fill="url(#gum)" stroke="{INK}" stroke-width="10"/>
<path d="M-40 1960 H1120 V1440 Q540 1640 -40 1440Z" fill="url(#gum)" stroke="{INK}" stroke-width="10"/>
<path d="M260 1240 Q540 1060 820 1240 Q760 1400 540 1420 Q320 1400 260 1240Z" fill="#e8848f" stroke="{INK}" stroke-width="8"/>
<path d="M540 1120 V1380" stroke="#c8606d" stroke-width="6"/>
{upper}{lower}
<g fill="#fff" opacity=".35">{"".join(f'<circle cx="{x}" cy="{y}" r="{r}"/>' for x, y, r in ((200, 800, 12), (900, 700, 9), (820, 1000, 14), (150, 1100, 8)))}</g>
{_paper_overlay()}'''


def bg_paper(wash="#cfeee9", accent="#ffe2b8"):
    """Clean white paper with soft watercolour washes (the 'white background' explainer look)."""
    return f'''{_defs()}<rect width="{W}" height="{H}" fill="#fffdf8"/>
<g filter="url(#wash)" opacity=".75"><circle cx="540" cy="900" r="430" fill="{wash}"/><circle cx="820" cy="560" r="180" fill="{accent}" opacity=".7"/>
<circle cx="230" cy="1300" r="160" fill="{accent}" opacity=".5"/></g>
<path d="M60 1480 H1020" stroke="{INK}" stroke-width="6" stroke-linecap="round" opacity=".85"/>
{_paper_overlay()}'''


ASSETS = __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.abspath(__file__)), "assets")


def bg_endcard():
    """Clinic end card (logo + every contact channel). Pair with draw=endcard_fg and dur=5."""
    rows = [("#06c755", "LINE", "แอดไลน์นัดหมายด้วยเบอร์ 0923595963"),
            ("#1877f2", "Facebook", "คลินิกทันตกรรมบางปะอิน"),
            ("#f08a3c", "ที่อยู่", "ตรงข้ามการไฟฟ้าบางปะอิน"),
            ("#0e5e63", "เวลาเปิด", "จ.–อา. 09:30–14:00 น. (หยุดวันศุกร์)")]
    items = ""
    for i, (c, k, v) in enumerate(rows):
        y = 1290 + i * 112
        items += (f'<rect x="96" y="{y}" width="888" height="96" rx="28" fill="#ffffff" stroke="{INK}" stroke-width="5"/>'
                  f'<rect x="96" y="{y}" width="196" height="96" rx="28" fill="{c}" stroke="{INK}" stroke-width="5"/>'
                  f'<text x="194" y="{y + 62}" text-anchor="middle" font-family="K" font-weight="700" font-size="38" fill="#fff">{k}</text>'
                  f'<text x="318" y="{y + 62}" font-family="K" font-weight="600" font-size="38" fill="{INK}">{v}</text>')
    return f'''{_defs()}<rect width="{W}" height="{H}" fill="url(#skyday)"/>
<circle cx="540" cy="560" r="520" fill="url(#sunglow)"/>
{cloud(150, 260, .8)}{cloud(930, 420, .6)}
<path d="M0 1050 C 240 960 520 1000 760 1060 S 1000 1010 1080 1030 V{H} H0Z" fill="url(#hillmid)" filter="url(#wash)"/>
<path d="M-40 1180 C 300 1120 700 1150 1120 1170 V{H} H-40Z" fill="#fffdf6"/>
<circle cx="540" cy="620" r="330" fill="#fff" stroke="{TEAL}" stroke-width="10"/>
<image href="file://{ASSETS}/logo.png" x="230" y="308" width="620" height="623" clip-path="circle(300px at 50% 50%)"/>
<text x="540" y="1140" text-anchor="middle" font-family="K" font-weight="700" font-size="58" fill="{TEAL_D}">ปรึกษาทันตแพทย์ได้ที่</text>
<rect x="150" y="1166" width="780" height="2" fill="none"/>
{items}
<g transform="translate(540,1790)"><rect x="-330" y="-62" width="660" height="124" rx="62" fill="{TEAL}" stroke="{INK}" stroke-width="7"/>
<text x="0" y="26" text-anchor="middle" font-family="K" font-weight="700" font-size="80" fill="#fff">☎ 092-359-5963</text></g>
{_paper_overlay()}'''


def endcard_fg(t):
    """Animated layer for the end card: waving mascot + twinkles."""
    k = ease(t / .6, "back")
    return (mascot(900, 980, t, .62 * k, "big", wave=1) +
            sparkle(150, 900, 26 + 6 * math.sin(t * 5), "#ffd84a") + sparkle(960, 700, 20 + 6 * math.sin(t * 4 + 1)))


BG = {"endcard": bg_endcard, "meadow": bg_meadow, "night": bg_night, "room": bg_room, "bathroom": bg_bathroom, "clinic": bg_clinic,
      "mouth": bg_mouth, "paper": bg_paper,
      "sunset": lambda: bg_meadow(sky="skysunset")}


# ---------------------------------------------------------------- scenes
class Scene:
    """One 4-second shot.

    bg      key of BG (painted once) or raw SVG string
    draw    function(t) -> SVG string for the animated layer (t in seconds from scene start)
    cam     key-frame track of (zoom, pan_x, pan_y): [(0,(1,0,0)), (4,(1.12,0,-40))]
    shake   optional function(t) -> (dx,dy) camera shake
    title   short on-screen title (1–4 words) or None;  sub = subtitle (narration text)
    voice   narration line (sent to ElevenLabs);  dur = seconds (4 for story scenes, 5 for the end card)
    image_prompt / anim_prompt: the per-scene prompts from the stickman workflow (kept for the record)
    """

    def __init__(self, bg, draw, voice="", sub=None, title=None, cam=None, shake=None, dur=4.0, endcard=False,
                 image_prompt="", anim_prompt=""):
        self.bg, self.draw, self.voice, self.title = bg, draw, voice, title
        self.sub = sub if sub is not None else voice.replace("...", " ").strip()
        self.cam = cam or [(0, (1.0, 0, 0)), (dur, (1.06, 0, 0))]
        self.shake, self.dur, self.endcard = shake, dur, endcard
        self.image_prompt, self.anim_prompt = image_prompt, anim_prompt
